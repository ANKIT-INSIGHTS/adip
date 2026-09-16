"""Assemble reports/latest_report.md from real, already-computed results.

This module does no analysis of its own — it only formats data that was
computed elsewhere (descriptive stats, accuracy metrics, anomalies, quality
checks) into the required Markdown sections. This separation keeps the
report honest: if a number appears in the report, it's traceable to a
specific analytics function.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from adip.config import REPO_ROOT

REPORT_PATH = REPO_ROOT / "reports" / "latest_report.md"


@dataclass(slots=True)
class ReportContext:
    run_started_at: datetime
    run_finished_at: datetime
    cities_attempted: int
    cities_succeeded: int
    records_ingested: int
    data_quality_summary: dict
    key_metrics: dict
    major_changes_md: str
    anomalies_md: str
    trends_md: str
    model_results_md: str
    limitations: list[str] = field(default_factory=list)


def _quality_line(check: dict) -> str:
    icon = "✅" if check["passed"] else "❌"
    return (
        f"- {icon} **{check['name']}**: {check['measured_value']} "
        f"(threshold {check['threshold']}) — {check.get('detail', '')}"
    )


def build_report(ctx: ReportContext) -> str:
    duration_s = (ctx.run_finished_at - ctx.run_started_at).total_seconds()
    quality_lines = "\n".join(
        _quality_line(c) for c in ctx.data_quality_summary.get("checks", [])
    )
    metrics_lines = "\n".join(f"- **{k}**: {v}" for k, v in ctx.key_metrics.items())
    limitations_lines = (
        "\n".join(f"- {item}" for item in ctx.limitations) or "- None recorded."
    )
    model_results = (
        ctx.model_results_md
        or "_No model results this run (insufficient observed data for scoring)._"
    )
    status_line = (
        "**Status:** ✅ All cities succeeded"
        if ctx.cities_succeeded == ctx.cities_attempted
        else (
            f"**Status:** ⚠️ Partial failure — "
            f"{ctx.cities_attempted - ctx.cities_succeeded} "
            f"{'city' if ctx.cities_attempted - ctx.cities_succeeded == 1 else 'cities'} "
            "failed to fetch"
        )
    )

    return f"""# ADIP — Latest Weather Intelligence Report

_Generated automatically by the ADIP pipeline. All figures below are computed
directly from Open-Meteo forecast and archive data — nothing in this report
is manually written or fabricated._

## Executive Summary

Pipeline run completed at **{ctx.run_finished_at.isoformat()}** covering
**{ctx.cities_succeeded}/{ctx.cities_attempted}** configured cities and
**{ctx.records_ingested}** ingested records in {duration_s:.1f}s.

{status_line}

## Data Coverage

- Cities attempted: {ctx.cities_attempted}
- Cities succeeded: {ctx.cities_succeeded}
- Records ingested this run: {ctx.records_ingested}

## Data Quality

{quality_lines or "_No quality checks recorded this run._"}

## Key Metrics

{metrics_lines or "_No metrics computed this run._"}

## Major Changes

{ctx.major_changes_md or "_No significant period-over-period changes detected._"}

## Anomalies

{ctx.anomalies_md or "_No anomalies detected this run._"}

## Trends

{ctx.trends_md or "_Insufficient history for trend analysis._"}

## Model Results

{model_results}

## Limitations

{limitations_lines}

- Forecast accuracy can only be computed for target hours where ERA5
  archive (observed) data has already been finalized, which lags real time
  by several days — recent forecasts are therefore not yet scoreable.
- Weather forecasting skill inherently degrades with lead time; metrics by
  horizon should be read as a property of the underlying model, not of this
  pipeline.
- Chart byte-for-byte reproducibility across matplotlib versions is not
  guaranteed; change detection tolerates this by only committing charts
  whose pixel content differs.

## Pipeline Run Information

- Started: {ctx.run_started_at.isoformat()}
- Finished: {ctx.run_finished_at.isoformat()}
- Duration: {duration_s:.1f}s
- Data source: [Open-Meteo](https://open-meteo.com/) (forecast + archive APIs)
"""


def write_report(ctx: ReportContext, path: Path | None = None) -> Path:
    out_path = path or REPORT_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_report(ctx), encoding="utf-8")
    return out_path
