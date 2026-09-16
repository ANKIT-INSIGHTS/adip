"""Write immutable raw JSON snapshots of every successful API fetch.

Raw snapshots are the source of truth: everything downstream (DuckDB tables,
Parquet, reports, charts) can be rebuilt from them. They are never edited or
overwritten in place, only appended.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from adip.config import REPO_ROOT
from adip.ingestion.open_meteo_client import ForecastFetchResult

RAW_DATA_DIR = REPO_ROOT / "data" / "raw"
RAW_ARCHIVE_DIR = REPO_ROOT / "data" / "raw" / "archive"


def snapshot_path(result: ForecastFetchResult) -> Path:
    date_dir = result.retrieved_at.strftime("%Y-%m-%d")
    run_ts = result.retrieved_at.strftime("%Y%m%dT%H%M%SZ")
    return RAW_DATA_DIR / date_dir / f"{result.city_id}_{run_ts}.json"


def write_snapshot(result: ForecastFetchResult) -> Path:
    """Persist a raw snapshot to disk. Idempotent: same result -> same path
    -> same bytes, so re-running never creates spurious duplicate files.
    """
    path = snapshot_path(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "city_id": result.city_id,
        "retrieved_at": result.retrieved_at.isoformat(),
        "source": "open-meteo-forecast-api",
        "payload": result.payload,
    }
    # Sort keys for deterministic byte output -> deterministic git diffs.
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_archive_snapshot(
    city_id: str, start_date: str, end_date: str, payload: dict[str, Any]
) -> Path:
    """Persist a raw ERA5-archive response. Naming is date-range-based (not
    timestamp-based) since re-requesting the same finalized range should
    always overwrite the same file with byte-identical content — the
    underlying reanalysis data for a finalized past date does not change.
    """
    retrieved_at = datetime.now(UTC)
    date_dir = retrieved_at.strftime("%Y-%m-%d")
    path = RAW_ARCHIVE_DIR / date_dir / f"{city_id}_{start_date}_to_{end_date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "city_id": city_id,
        "start_date": start_date,
        "end_date": end_date,
        "retrieved_at": retrieved_at.isoformat(),
        "source": "open-meteo-archive-api-era5",
        "payload": payload,
    }
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return path
