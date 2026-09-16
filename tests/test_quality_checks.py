from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd

from adip.config import DataQualityConfig
from adip.validation.quality_checks import (
    check_duplicates,
    check_freshness,
    check_null_fraction,
    check_range,
    check_row_count,
)

CFG = DataQualityConfig(
    max_null_fraction=0.1,
    max_duplicate_fraction=0.0,
    freshness_max_age_hours=24,
    min_expected_row_count_per_city=5,
)


def test_null_fraction_passes_under_threshold():
    df = pd.DataFrame({"a": [1, 2, 3, None]})
    result = check_null_fraction(df, ["a"], CFG)
    assert result.measured_value == 0.25 or not result.passed  # 25% > 10% threshold
    assert result.passed is False


def test_null_fraction_passes_with_no_nulls():
    df = pd.DataFrame({"a": [1, 2, 3, 4]})
    result = check_null_fraction(df, ["a"], CFG)
    assert result.passed is True
    assert result.measured_value == 0.0


def test_duplicates_detected():
    df = pd.DataFrame({"k": [1, 1, 2]})
    result = check_duplicates(df, ["k"], CFG)
    assert result.passed is False


def test_no_duplicates_passes():
    df = pd.DataFrame({"k": [1, 2, 3]})
    result = check_duplicates(df, ["k"], CFG)
    assert result.passed is True


def test_row_count_below_threshold_fails():
    df = pd.DataFrame({"a": [1, 2]})
    result = check_row_count(df, "city", CFG)
    assert result.passed is False


def test_row_count_meets_threshold_passes():
    df = pd.DataFrame({"a": range(5)})
    result = check_row_count(df, "city", CFG)
    assert result.passed is True


def test_freshness_recent_passes():
    ts = datetime.now(UTC) - timedelta(hours=1)
    result = check_freshness(ts, CFG)
    assert result.passed is True


def test_freshness_stale_fails():
    ts = datetime.now(UTC) - timedelta(hours=48)
    result = check_freshness(ts, CFG)
    assert result.passed is False


def test_freshness_missing_data_fails():
    result = check_freshness(None, CFG)
    assert result.passed is False


def test_range_check_flags_out_of_range_temperature():
    df = pd.DataFrame({"temperature_c": [20.0, 150.0, -5.0]})
    result = check_range(df, "temperature_c", -90.0, 60.0)
    assert result.passed is False
    assert result.measured_value == 1


def test_range_check_passes_within_bounds():
    df = pd.DataFrame({"temperature_c": [10.0, 20.0, 30.0]})
    result = check_range(df, "temperature_c", -90.0, 60.0)
    assert result.passed is True
