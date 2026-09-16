"""Transform raw Open-Meteo JSON snapshots into tidy, typed rows.

Pure functions only: no I/O, no globals — this makes the transformation
logic trivially unit-testable against fixture payloads.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pandas as pd

from adip.validation.schemas import ForecastResponse

MODEL_LABEL = "open-meteo-default-blend"


def _parse_iso(ts: str) -> datetime:
    # Open-Meteo returns local-time ISO strings without offset when a
    # timezone parameter is supplied; we keep them naive-local and rely on
    # the per-city timezone recorded alongside them for interpretation.
    return datetime.fromisoformat(ts)


def forecast_payload_to_snapshot_rows(
    city_id: str, forecast_run_ts: datetime, payload: dict[str, Any], source_file: str
) -> pd.DataFrame:
    """Explode one forecast API response into one row per (city, target hour).

    forecast_horizon_h = hours between when the forecast was retrieved and
    the hour it predicts — the key that makes forecast-evolution analysis
    possible.
    """
    parsed = ForecastResponse.model_validate(payload)
    hourly = parsed.hourly
    n = len(hourly.time)
    # DuckDB's TIMESTAMP columns are timezone-naive; store everything as
    # naive UTC consistently so comparisons/joins across tables never trip
    # over aware-vs-naive mismatches.
    run_ts_naive = (
        forecast_run_ts.astimezone(UTC).replace(tzinfo=None)
        if forecast_run_ts.tzinfo
        else forecast_run_ts
    )

    def col(values: list, idx: int):
        return values[idx] if idx < len(values) else None

    rows = []
    for i in range(n):
        target_ts = _parse_iso(hourly.time[i])
        horizon_h = round((target_ts - run_ts_naive).total_seconds() / 3600)
        rows.append(
            {
                "city_id": city_id,
                "forecast_run_ts": run_ts_naive,
                "target_ts": target_ts,
                "forecast_horizon_h": horizon_h,
                "model": MODEL_LABEL,
                "temperature_c": col(hourly.temperature_2m, i),
                "apparent_temp_c": col(hourly.apparent_temperature, i),
                "relative_humidity": col(hourly.relative_humidity_2m, i),
                "precipitation_mm": col(hourly.precipitation, i),
                "wind_speed_kmh": col(hourly.wind_speed_10m, i),
                "weather_code": col(hourly.weather_code, i),
                "source_file": source_file,
            }
        )
    return pd.DataFrame(rows)


def forecast_payload_to_current_row(
    city_id: str, retrieved_at: datetime, payload: dict[str, Any], source_file: str
) -> pd.DataFrame:
    parsed = ForecastResponse.model_validate(payload)
    if parsed.current is None:
        return pd.DataFrame()
    c = parsed.current
    retrieved_at_naive = (
        retrieved_at.astimezone(UTC).replace(tzinfo=None)
        if retrieved_at.tzinfo
        else retrieved_at
    )
    return pd.DataFrame(
        [
            {
                "city_id": city_id,
                "retrieved_at": retrieved_at_naive,
                "temperature_c": c.temperature_2m,
                "apparent_temp_c": c.apparent_temperature,
                "relative_humidity": c.relative_humidity_2m,
                "precipitation_mm": c.precipitation,
                "wind_speed_kmh": c.wind_speed_10m,
                "weather_code": c.weather_code,
                "source_file": source_file,
            }
        ]
    )


def archive_payload_to_observed_rows(
    city_id: str, payload: dict[str, Any], source_file: str
) -> pd.DataFrame:
    """Archive (ERA5 reanalysis) responses share the forecast response shape,
    but semantically represent OBSERVED history, never predictions.
    """
    parsed = ForecastResponse.model_validate(payload)
    hourly = parsed.hourly
    n = len(hourly.time)

    def col(values: list, idx: int):
        return values[idx] if idx < len(values) else None

    rows = []
    for i in range(n):
        rows.append(
            {
                "city_id": city_id,
                "observed_ts": _parse_iso(hourly.time[i]),
                "temperature_c": col(hourly.temperature_2m, i),
                "relative_humidity": col(hourly.relative_humidity_2m, i),
                "precipitation_mm": col(hourly.precipitation, i),
                "wind_speed_kmh": col(hourly.wind_speed_10m, i),
                "weather_code": col(hourly.weather_code, i),
                "source": "era5-archive-reanalysis",
                "source_file": source_file,
            }
        )
    return pd.DataFrame(rows)
