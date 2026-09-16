#!/usr/bin/env python3
"""Rebuild data/snapshots/adip.duckdb entirely from committed raw JSON.

Because the DuckDB file is gitignored (to avoid noisy binary diffs), this
script is what makes the project reproducible: `git clone` + `make rebuild-db`
regenerates the full analytical history from source-of-truth raw snapshots.
It's also used as the first step of every pipeline run, before new data is
ingested, so historical analytics always see the complete picture.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from adip.config import REPO_ROOT
from adip.storage.db import get_connection
from adip.transformation.normalize import (
    archive_payload_to_observed_rows,
    forecast_payload_to_current_row,
    forecast_payload_to_snapshot_rows,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("adip.rebuild_db")

RAW_DIR = REPO_ROOT / "data" / "raw"


def rebuild() -> None:
    con = get_connection()
    con.execute("DELETE FROM forecast_snapshots")
    con.execute("DELETE FROM current_conditions")
    con.execute("DELETE FROM observed_weather")

    forecast_files = sorted(p for p in RAW_DIR.rglob("*.json") if "archive" not in p.parts)
    archive_files = (
        sorted((RAW_DIR / "archive").rglob("*.json")) if (RAW_DIR / "archive").exists() else []
    )

    n_snap, n_current, n_observed = 0, 0, 0
    for f in forecast_files:
        try:
            record = json.loads(f.read_text(encoding="utf-8"))
            from datetime import datetime

            retrieved_at = datetime.fromisoformat(record["retrieved_at"])
            rel = str(f.relative_to(REPO_ROOT))
            snap = forecast_payload_to_snapshot_rows(
                record["city_id"], retrieved_at, record["payload"], rel
            )
            current = forecast_payload_to_current_row(
                record["city_id"], retrieved_at, record["payload"], rel
            )
            if not snap.empty:
                con.executemany(
                    "INSERT OR REPLACE INTO forecast_snapshots VALUES "
                    "(?,?,?,?,?,?,?,?,?,?,?,?)",
                    snap[
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
                n_snap += len(snap)
            if not current.empty:
                con.executemany(
                    "INSERT OR REPLACE INTO current_conditions VALUES (?,?,?,?,?,?,?,?,?)",
                    current.itertuples(index=False, name=None),
                )
                n_current += len(current)
        except Exception:
            logger.exception("Skipping unreadable raw file: %s", f)

    for f in archive_files:
        try:
            record = json.loads(f.read_text(encoding="utf-8"))
            rel = str(f.relative_to(REPO_ROOT))
            observed = archive_payload_to_observed_rows(
                record["city_id"], record["payload"], rel
            )
            if not observed.empty:
                con.executemany(
                    "INSERT OR REPLACE INTO observed_weather VALUES (?,?,?,?,?,?,?,?,?)",
                    observed.itertuples(index=False, name=None),
                )
                n_observed += len(observed)
        except Exception:
            logger.exception("Skipping unreadable archive file: %s", f)

    con.close()
    logger.info(
        "Rebuilt DuckDB: %d forecast rows, %d current rows, %d observed rows "
        "from %d forecast files + %d archive files",
        n_snap,
        n_current,
        n_observed,
        len(forecast_files),
        len(archive_files),
    )


if __name__ == "__main__":
    rebuild()
