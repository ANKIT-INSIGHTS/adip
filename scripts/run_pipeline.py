#!/usr/bin/env python3
"""ADIP pipeline orchestrator.

Sequence (mirrors docs/architecture.md):
  fetch -> raw snapshot -> validate -> transform -> load DuckDB
  -> analytics -> anomaly detection -> reports/charts -> change detection
  -> exit code signals whether a commit is warranted (does NOT commit itself;
     git operations are handled by the GitHub Actions workflow, keeping
     "what to commit" and "how to commit" cleanly separated).

Exit codes:
  0 = success, meaningful changes detected (workflow should commit)
  1 = success, no meaningful changes (workflow should NOT commit)
  2 = pipeline failure (workflow should fail the job, no commit)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import rebuild_db  # noqa: E402
from adip.analytics import accuracy, anomalies, descriptive, forecast_evolution
from adip.change_detection import detect_changes
from adip.config import REPO_ROOT, load_cities, load_pipeline_config
from adip.ingestion.open_meteo_client import (
    OpenMeteoError,
    fetch_archive,
    fetch_forecast,
)
from adip.ingestion.snapshot_writer import write_archive_snapshot, write_snapshot
from adip.reporting import charts
from adip.reporting.report_builder import ReportContext, write_report
from adip.storage.db import get_connection
from adip.transformation.normalize import (
    archive_payload_to_observed_rows,
    forecast_payload_to_current_row,
    forecast_payload_to_snapshot_rows,
)
from adip.validation.quality_checks import run_all_checks
from adip.validation.quality_report import write_quality_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("adip.pipeline")


def _iso_or_none(v):
    return v.isoformat() if v is not None else None


def run(dry_run: bool = False) -> int:
    run_id = str(uuid.uuid4())
    started_at = datetime.now(UTC)
    logger.info("Starting ADIP pipeline run %s", run_id)

    cities = load_cities()
    cfg = load_pipeline_config()

    logger.info("Rebuilding DuckDB from committed raw history before ingesting new data.")
    rebuild_db.rebuild()

    con = get_connection()
    all_snapshot_frames: list[pd.DataFrame] = []
    all_current_frames: list[pd.DataFrame] = []
    all_observed_frames: list[pd.DataFrame] = []
    quality_checks_by_city: dict = {}
    cities_succeeded = 0
    records_ingested = 0

    # --- Ingestion + validation + transformation, per city -----------------
    for city in cities:
        try:
            result = fetch_forecast(city, cfg.api, cfg.forecast)
        except OpenMeteoError as exc:
            logger.error("Ingestion failed for %s: %s", city.id, exc)
            continue

        snapshot_path = write_snapshot(result)
        rel_source = str(snapshot_path.relative_to(REPO_ROOT))

        try:
            snap_rows = forecast_payload_to_snapshot_rows(
                city.id, result.retrieved_at, result.payload, rel_source
            )
            current_row = forecast_payload_to_current_row(
                city.id, result.retrieved_at, result.payload, rel_source
            )
        except Exception:
            logger.exception("Transformation failed for %s", city.id)
            continue

        checks = run_all_checks(
            df=snap_rows,
            city_id=city.id,
            key_columns=["city_id", "forecast_run_ts", "target_ts"],
            null_check_columns=["temperature_c", "relative_humidity"],
            latest_ts=snap_rows["target_ts"].max() if not snap_rows.empty else None,
            cfg=cfg.data_quality,
        )
        quality_checks_by_city[city.id] = checks

        con.executemany(
            """INSERT OR REPLACE INTO forecast_snapshots VALUES
               (?,?,?,?,?,?,?,?,?,?,?,?)""",
            snap_rows[
                [
                    "city_id",
                    "forecast_run_ts",
                    "target_ts",
                    "forecast_horizon_h",
                    "model",
                    "temperature_c",
                    "apparent_temp_c",
                    "relative_humidity",
                    "precipitation_mm",
                    "wind_speed_kmh",
                    "weather_code",
                    "source_file",
                ]
            ].itertuples(index=False, name=None),
        )
        if not current_row.empty:
            con.executemany(
                """INSERT OR REPLACE INTO current_conditions VALUES
                   (?,?,?,?,?,?,?,?,?)""",
                current_row.itertuples(index=False, name=None),
            )

        all_snapshot_frames.append(snap_rows)
        all_current_frames.append(current_row)
        records_ingested += len(snap_rows)
        cities_succeeded += 1

        # Best-effort archive/observed pull for a finalized date window.
        try:
            end = datetime.now(UTC).date() - timedelta(days=cfg.archive.min_days_lag)
            start = end - timedelta(days=2)
            archive_payload = fetch_archive(
                city, cfg.api, cfg.forecast, start.isoformat(), end.isoformat()
            )
            archive_snapshot_path = write_archive_snapshot(
                city.id, start.isoformat(), end.isoformat(), archive_payload
            )
            observed_rows = archive_payload_to_observed_rows(
                city.id, archive_payload, str(archive_snapshot_path.relative_to(REPO_ROOT))
            )
            if not observed_rows.empty:
                con.executemany(
                    """INSERT OR REPLACE INTO observed_weather VALUES
                       (?,?,?,?,?,?,?,?,?)""",
                    observed_rows.itertuples(index=False, name=None),
                )
                all_observed_frames.append(observed_rows)
        except OpenMeteoError as exc:
            logger.warning("Archive fetch failed for %s (non-fatal): %s", city.id, exc)

    if cities_succeeded == 0:
        logger.error("All cities failed ingestion — aborting run without committing.")
        return 2

    # This run's own fetch, kept separate from full history — used to scope
    # "which anomalies/changes came from *this* run" in the report, as
    # distinct from the full-history frames used for baselines below.
    current_df = (
        pd.concat(all_current_frames, ignore_index=True)
        if all_current_frames
        else pd.DataFrame()
    )

    # Pull the FULL historical tables from DuckDB (not just this run's fetch)
    # for analytics. Anomaly detection needs a real baseline (cfg.anomaly_
    # detection.min_history_days), and forecast-evolution/accuracy analysis
    # is meaningless without forecasts issued at multiple past times — both
    # only exist once we look across runs, not within a single run's fetch.
    history_current_df = con.execute("SELECT * FROM current_conditions").df()
    history_snapshots_df = con.execute("SELECT * FROM forecast_snapshots").df()
    history_observed_df = con.execute("SELECT * FROM observed_weather").df()

    # --- Analytics -----------------------------------------------------
    key_metrics: dict = {}
    major_changes_md = ""
    trends_md = ""
    model_results_md = ""
    anomalies_md = ""
    anomaly_count = 0

    if not history_current_df.empty:
        history_current_df = history_current_df.rename(columns={"retrieved_at": "ts"})
        temp_dist = descriptive.distribution_summary(history_current_df, "temperature_c")
        key_metrics["current_temperature_distribution_c"] = temp_dist

        top_changes = descriptive.largest_changes(
            history_current_df, "temperature_c", cfg.reporting.top_n_changes
        )
        if not top_changes.empty:
            major_changes_md = "\n".join(
                f"- **{r.city_id}**: {r.change:+.1f}°C (now {r.temperature_c:.1f}°C)"
                for r in top_changes.itertuples()
            )

        anomaly_df = anomalies.detect_anomalies(
            history_current_df, "temperature_c", cfg.anomaly_detection
        )
        flagged = anomaly_df[anomaly_df["is_anomaly"]] if not anomaly_df.empty else anomaly_df
        anomaly_count = int(len(flagged))
        if not flagged.empty:
            # Report only anomalies from *this* run's retrieval batch, not
            # every historical anomaly ever detected.
            recent_flagged = flagged[
                flagged["ts"].isin(
                    [r.retrieved_at for r in current_df.itertuples()]
                    if not current_df.empty
                    else []
                )
            ]
            report_target = (
                recent_flagged
                if not recent_flagged.empty
                else flagged.tail(cfg.reporting.top_n_changes)
            )
            anomalies_md = "\n".join(
                f"- **{r.city_id}** at {r.ts}: {r.temperature_c:.1f}°C "
                f"(modified z-score {r.modified_zscore:.2f})"
                for r in report_target.itertuples()
            )
            charts.anomaly_timeline_chart(anomaly_df, "temperature_c")

        # City comparison uses only the latest reading per city (this run's
        # data, since history_current_df's tail per group is what we just
        # inserted).
        charts.city_comparison_chart(
            history_current_df,
            "temperature_c",
            "Current temperature by city",
            "current_temperature_by_city",
        )

    if not history_observed_df.empty and not history_snapshots_df.empty:
        joined = accuracy.join_forecast_to_observed(history_snapshots_df, history_observed_df)
        if not joined.empty:
            overall = accuracy.accuracy_metrics(joined)
            by_city = accuracy.accuracy_metrics(joined, ["city_id"])
            precip = accuracy.precipitation_accuracy(joined)
            model_results_md = (
                f"**Overall** (n={int(overall['n'].iloc[0]) if not overall.empty else 0}): "
                f"MAE={overall['mae_c'].iloc[0] if not overall.empty else 'n/a'}°C, "
                f"RMSE={overall['rmse_c'].iloc[0] if not overall.empty else 'n/a'}°C, "
                f"bias={overall['bias_c'].iloc[0] if not overall.empty else 'n/a'}°C\n\n"
                f"Precipitation wet/dry accuracy: {precip.get('wet_dry_accuracy', 'n/a')} "
                f"(n={precip.get('n', 0)})\n\n"
                "**By city:**\n"
                + "\n".join(
                    f"- {r.city_id}: MAE={r.mae_c}°C, RMSE={r.rmse_c}°C, "
                    f"bias={r.bias_c}°C (n={r.n})"
                    for r in by_city.itertuples()
                )
            )

        revisions = forecast_evolution.forecast_revisions(history_snapshots_df)
        rev_summary = forecast_evolution.revision_magnitude_summary(revisions)
        if rev_summary.get("count", 0) > 0:
            trends_md = (
                f"Forecasts are revised by a mean of {rev_summary['mean_abs_revision_c']}°C "
                f"(max {rev_summary['max_abs_revision_c']}°C) between consecutive "
                "issue times, "
                f"based on {rev_summary['count']} revision pair(s) observed so far."
            )

        by_horizon = forecast_evolution.latest_forecast_per_horizon(
            history_snapshots_df, cfg.forecast.horizons_hours
        )
        horizon_joined = accuracy.join_forecast_to_observed(by_horizon, history_observed_df)
        if not horizon_joined.empty:
            horizon_acc = accuracy.accuracy_metrics(horizon_joined, ["requested_horizon_h"])
            charts.forecast_error_by_horizon_chart(horizon_acc)

    # --- Reports ---------------------------------------------------------
    finished_at = datetime.now(UTC)
    quality_json_path, quality_md_path = write_quality_report(quality_checks_by_city)
    quality_payload = json.loads(quality_json_path.read_text(encoding="utf-8"))

    ctx = ReportContext(
        run_started_at=started_at,
        run_finished_at=finished_at,
        cities_attempted=len(cities),
        cities_succeeded=cities_succeeded,
        records_ingested=records_ingested,
        data_quality_summary=quality_payload,
        key_metrics=key_metrics,
        major_changes_md=major_changes_md,
        anomalies_md=anomalies_md,
        trends_md=trends_md,
        model_results_md=model_results_md,
        limitations=[],
    )
    report_path = write_report(ctx)

    # --- Change detection --------------------------------------------------
    candidate_paths = [report_path, quality_json_path, quality_md_path]
    figures_dir = REPO_ROOT / "reports" / "figures"
    if figures_dir.exists():
        candidate_paths.extend(sorted(figures_dir.glob("*.png")))
    raw_dir = REPO_ROOT / "data" / "raw"
    if raw_dir.exists():
        candidate_paths.extend(sorted(raw_dir.rglob("*.json")))

    change_report = detect_changes(candidate_paths, cfg.change_detection)

    con.execute(
        "INSERT INTO pipeline_runs VALUES (?,?,?,?,?,?,?,?,?)",
        [
            run_id,
            started_at,
            finished_at,
            "success" if cities_succeeded == len(cities) else "partial_failure",
            len(cities),
            cities_succeeded,
            records_ingested,
            anomaly_count,
            change_report.has_meaningful_change,
        ],
    )
    con.close()

    summary = {
        "run_id": run_id,
        "status": "success" if cities_succeeded == len(cities) else "partial_failure",
        "duration_seconds": round((finished_at - started_at).total_seconds(), 1),
        "cities_attempted": len(cities),
        "cities_succeeded": cities_succeeded,
        "records_ingested": records_ingested,
        "changed_files": change_report.changed_files,
        "unchanged_files_count": len(change_report.unchanged_files),
        "commit_recommended": change_report.has_meaningful_change,
    }
    print(json.dumps(summary, indent=2, default=str))

    _write_github_summary(summary)

    if dry_run:
        logger.info("Dry run: skipping exit-code-based commit signaling.")
        return 0

    return 0 if change_report.has_meaningful_change else 1


def _write_github_summary(summary: dict) -> None:
    summary_file = __import__("os").environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        return
    lines = [
        "## ADIP Pipeline Run Summary",
        "",
        f"- **Status:** {summary['status']}",
        f"- **Duration:** {summary['duration_seconds']}s",
        f"- **Cities:** {summary['cities_succeeded']}/{summary['cities_attempted']} succeeded",
        f"- **Records ingested:** {summary['records_ingested']}",
        f"- **Files changed:** {len(summary['changed_files'])}",
        f"- **Commit recommended:** "
        f"{'✅ yes' if summary['commit_recommended'] else '⏭️ no — no meaningful change'}",
    ]
    if summary["changed_files"]:
        lines.append("")
        lines.append("<details><summary>Changed files</summary>\n")
        lines.extend(f"- `{f}`" for f in summary["changed_files"][:50])
        lines.append("\n</details>")
    with open(summary_file, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ADIP pipeline.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run fully but always exit 0 (for local iteration).",
    )
    args = parser.parse_args()
    try:
        code = run(dry_run=args.dry_run)
    except Exception:
        logger.exception("Pipeline failed with an unhandled exception.")
        sys.exit(2)
    sys.exit(code)


if __name__ == "__main__":
    main()
