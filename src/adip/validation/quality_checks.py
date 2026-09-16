"""Automated data-quality checks over normalized DataFrames.

Produces a structured, serializable result set consumed by
reporting/report_builder.py to build reports/data_quality/latest.json and
latest.md. Every check is independent and returns a pass/fail plus the
measured value, so the report is always grounded in a real computation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from adip.config import DataQualityConfig


@dataclass(slots=True)
class CheckResult:
    name: str
    passed: bool
    measured_value: float | int | str
    threshold: float | int | str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_null_fraction(
    df: pd.DataFrame, columns: list[str], cfg: DataQualityConfig
) -> CheckResult:
    if df.empty:
        return CheckResult(
            "null_fraction", False, 1.0, cfg.max_null_fraction, "DataFrame is empty"
        )
    frac = df[columns].isna().mean().max()
    return CheckResult(
        "null_fraction",
        bool(frac <= cfg.max_null_fraction),
        round(float(frac), 4),
        cfg.max_null_fraction,
        f"Max null fraction across {columns}",
    )


def check_duplicates(
    df: pd.DataFrame, key_columns: list[str], cfg: DataQualityConfig
) -> CheckResult:
    if df.empty:
        return CheckResult(
            "duplicate_fraction", True, 0.0, cfg.max_duplicate_fraction, "No rows to check"
        )
    dup_frac = df.duplicated(subset=key_columns).mean()
    return CheckResult(
        "duplicate_fraction",
        bool(dup_frac <= cfg.max_duplicate_fraction),
        round(float(dup_frac), 4),
        cfg.max_duplicate_fraction,
        f"Duplicate fraction on key {key_columns}",
    )


def check_row_count(df: pd.DataFrame, city_id: str, cfg: DataQualityConfig) -> CheckResult:
    n = len(df)
    passed = n >= cfg.min_expected_row_count_per_city
    return CheckResult(
        "row_count",
        passed,
        n,
        cfg.min_expected_row_count_per_city,
        f"Row count for city={city_id}",
    )


def check_freshness(latest_ts: datetime | None, cfg: DataQualityConfig) -> CheckResult:
    if latest_ts is None:
        return CheckResult(
            "freshness_hours", False, "n/a", cfg.freshness_max_age_hours, "No data present"
        )
    now = datetime.now(UTC)
    if latest_ts.tzinfo is None:
        latest_ts = latest_ts.replace(tzinfo=UTC)
    age_hours = (now - latest_ts).total_seconds() / 3600
    passed = age_hours <= cfg.freshness_max_age_hours
    return CheckResult(
        "freshness_hours",
        passed,
        round(age_hours, 2),
        cfg.freshness_max_age_hours,
        "Hours since most recent data point",
    )


def check_range(df: pd.DataFrame, column: str, low: float, high: float) -> CheckResult:
    if df.empty or column not in df.columns:
        return CheckResult(
            f"range_{column}", True, "n/a", f"[{low}, {high}]", "No data to check"
        )
    series = df[column].dropna()
    if series.empty:
        return CheckResult(
            f"range_{column}", True, "n/a", f"[{low}, {high}]", "All values null"
        )
    out_of_range = ((series < low) | (series > high)).sum()
    passed = out_of_range == 0
    return CheckResult(
        f"range_{column}",
        bool(passed),
        int(out_of_range),
        f"[{low}, {high}]",
        f"Values outside physically plausible range for {column}",
    )


def run_all_checks(
    df: pd.DataFrame,
    city_id: str,
    key_columns: list[str],
    null_check_columns: list[str],
    latest_ts: datetime | None,
    cfg: DataQualityConfig,
) -> list[CheckResult]:
    results = [
        check_null_fraction(df, null_check_columns, cfg),
        check_duplicates(df, key_columns, cfg),
        check_row_count(df, city_id, cfg),
        check_freshness(latest_ts, cfg),
    ]
    if "temperature_c" in df.columns:
        results.append(check_range(df, "temperature_c", -90.0, 60.0))
    if "relative_humidity" in df.columns:
        results.append(check_range(df, "relative_humidity", 0.0, 100.0))
    if "wind_speed_kmh" in df.columns:
        results.append(check_range(df, "wind_speed_kmh", 0.0, 500.0))
    return results
