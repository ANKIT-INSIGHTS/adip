"""Typed configuration loading for ADIP.

All tunable behavior (cities, thresholds, endpoints) lives in YAML under
``configs/`` rather than being hardcoded in source, per the project's design
principle of keeping data/behavior separate from code.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs"


@dataclass(frozen=True, slots=True)
class City:
    id: str
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True, slots=True)
class ApiConfig:
    forecast_base_url: str
    archive_base_url: str
    request_timeout_seconds: float
    max_retries: int
    backoff_base_seconds: float
    min_seconds_between_requests: float


@dataclass(frozen=True, slots=True)
class ForecastConfig:
    hourly_variables: tuple[str, ...]
    daily_variables: tuple[str, ...]
    horizons_hours: tuple[int, ...]
    forecast_days: int


@dataclass(frozen=True, slots=True)
class ArchiveConfig:
    min_days_lag: int


@dataclass(frozen=True, slots=True)
class DataQualityConfig:
    max_null_fraction: float
    max_duplicate_fraction: float
    freshness_max_age_hours: float
    min_expected_row_count_per_city: int


@dataclass(frozen=True, slots=True)
class AnomalyConfig:
    method: str
    threshold: float
    min_history_days: int


@dataclass(frozen=True, slots=True)
class ChangeDetectionConfig:
    float_comparison_decimals: int
    ignore_json_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReportingConfig:
    rolling_windows_days: tuple[int, ...]
    top_n_changes: int


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    api: ApiConfig
    forecast: ForecastConfig
    archive: ArchiveConfig
    data_quality: DataQualityConfig
    anomaly_detection: AnomalyConfig
    change_detection: ChangeDetectionConfig
    reporting: ReportingConfig


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Required config file missing: {path}. ADIP refuses to run with "
            "implicit defaults for data-defining configuration."
        )
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@lru_cache(maxsize=1)
def load_cities(path: Path | None = None) -> tuple[City, ...]:
    raw = _read_yaml(path or (CONFIGS_DIR / "cities.yaml"))
    cities = tuple(City(**entry) for entry in raw["cities"])
    ids = [c.id for c in cities]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate city id detected in configs/cities.yaml")
    return cities


@lru_cache(maxsize=1)
def load_pipeline_config(path: Path | None = None) -> PipelineConfig:
    raw = _read_yaml(path or (CONFIGS_DIR / "pipeline.yaml"))
    return PipelineConfig(
        api=ApiConfig(**raw["api"]),
        forecast=ForecastConfig(
            hourly_variables=tuple(raw["forecast"]["hourly_variables"]),
            daily_variables=tuple(raw["forecast"]["daily_variables"]),
            horizons_hours=tuple(raw["forecast"]["horizons_hours"]),
            forecast_days=raw["forecast"]["forecast_days"],
        ),
        archive=ArchiveConfig(**raw["archive"]),
        data_quality=DataQualityConfig(**raw["data_quality"]),
        anomaly_detection=AnomalyConfig(**raw["anomaly_detection"]),
        change_detection=ChangeDetectionConfig(
            float_comparison_decimals=raw["change_detection"]["float_comparison_decimals"],
            ignore_json_keys=tuple(raw["change_detection"]["ignore_json_keys"]),
        ),
        reporting=ReportingConfig(
            rolling_windows_days=tuple(raw["reporting"]["rolling_windows_days"]),
            top_n_changes=raw["reporting"]["top_n_changes"],
        ),
    )
