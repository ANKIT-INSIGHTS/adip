from __future__ import annotations

import pandas as pd
import pytest

from adip.analytics.accuracy import (
    accuracy_metrics,
    join_forecast_to_observed,
    precipitation_accuracy,
)


def _forecast_df():
    return pd.DataFrame(
        {
            "city_id": ["ny", "ny", "london"],
            "target_ts": pd.to_datetime(
                ["2026-01-01 00:00", "2026-01-01 01:00", "2026-01-01 00:00"]
            ),
            "temperature_c": [10.0, 12.0, 5.0],
            "precipitation_mm": [0.0, 1.0, 0.0],
        }
    )


def _observed_df():
    return pd.DataFrame(
        {
            "city_id": ["ny", "ny", "london"],
            "observed_ts": pd.to_datetime(
                ["2026-01-01 00:00", "2026-01-01 01:00", "2026-01-01 00:00"]
            ),
            "temperature_c": [11.0, 11.0, 5.0],
            "precipitation_mm": [0.0, 0.0, 0.0],
        }
    )


def test_join_only_matches_common_timestamps():
    joined = join_forecast_to_observed(_forecast_df(), _observed_df())
    assert len(joined) == 3
    assert "error_c" in joined.columns


def test_join_returns_empty_for_no_observed_data():
    joined = join_forecast_to_observed(_forecast_df(), pd.DataFrame())
    assert joined.empty


def test_accuracy_metrics_overall():
    joined = join_forecast_to_observed(_forecast_df(), _observed_df())
    metrics = accuracy_metrics(joined)
    # errors: ny -1, ny +1, london 0 -> MAE = 2/3, bias = 0
    assert metrics["n"].iloc[0] == 3
    assert abs(metrics["bias_c"].iloc[0]) < 1e-6


def test_accuracy_metrics_by_city():
    joined = join_forecast_to_observed(_forecast_df(), _observed_df())
    by_city = accuracy_metrics(joined, ["city_id"])
    london_row = by_city[by_city["city_id"] == "london"].iloc[0]
    assert london_row["mae_c"] == 0.0


def test_precipitation_accuracy_wet_dry():
    joined = join_forecast_to_observed(_forecast_df(), _observed_df())
    result = precipitation_accuracy(joined, wet_threshold_mm=0.2)
    assert result["n"] == 3
    # forecast predicted wet at hour 2 (1.0mm), observed was dry -> 1 mismatch out of 3
    assert result["wet_dry_accuracy"] == pytest.approx(2 / 3, abs=0.001)
