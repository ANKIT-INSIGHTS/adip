from __future__ import annotations

import pandas as pd

from adip.analytics.anomalies import detect_anomalies, modified_zscores
from adip.analytics.descriptive import distribution_summary, largest_changes
from adip.config import AnomalyConfig

ANOMALY_CFG = AnomalyConfig(method="modified_zscore", threshold=3.5, min_history_days=3)


def test_distribution_summary_basic_stats():
    df = pd.DataFrame({"v": [1, 2, 3, 4, 5]})
    summary = distribution_summary(df, "v")
    assert summary["count"] == 5
    assert summary["median"] == 3
    assert summary["min"] == 1
    assert summary["max"] == 5


def test_distribution_summary_empty():
    df = pd.DataFrame({"v": []})
    summary = distribution_summary(df, "v")
    assert summary["count"] == 0


def test_largest_changes_orders_by_absolute_magnitude():
    df = pd.DataFrame(
        {
            "city_id": ["a", "a", "a"],
            "ts": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
            "v": [10.0, 10.5, 20.0],
        }
    )
    result = largest_changes(df, "v", top_n=1)
    assert len(result) == 1
    assert result.iloc[0]["v"] == 20.0


def test_rolling_average_correct_per_group_alignment():
    from adip.analytics.descriptive import rolling_average

    df = pd.DataFrame(
        {
            "city_id": ["a", "a", "a", "b", "b"],
            "ts": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-01", "2026-01-02"]
            ),
            "v": [10, 20, 15, 100, 200],
        }
    )
    result = rolling_average(df, "v", 3)
    a_rows = result[result["city_id"] == "a"].sort_values("ts")
    b_rows = result[result["city_id"] == "b"].sort_values("ts")
    assert a_rows["rolling_3d_avg"].tolist() == [10.0, 15.0, 15.0]
    assert b_rows["rolling_3d_avg"].tolist() == [100.0, 150.0]


def test_modified_zscore_handles_zero_mad():
    series = pd.Series([5, 5, 5, 5])
    z = modified_zscores(series)
    assert (z == 0).all()


def test_detect_anomalies_flags_outlier():
    df = pd.DataFrame(
        {
            "city_id": ["a"] * 10,
            "v": [20, 21, 20, 21, 20, 21, 20, 21, 20, 100],
        }
    )
    result = detect_anomalies(df, "v", ANOMALY_CFG, min_group_size=3)
    assert result["is_anomaly"].iloc[-1] == True  # noqa: E712
    assert result["is_anomaly"].iloc[0] == False  # noqa: E712


def test_detect_anomalies_skips_small_groups():
    df = pd.DataFrame({"city_id": ["a", "a"], "v": [20, 100]})
    result = detect_anomalies(df, "v", ANOMALY_CFG, min_group_size=5)
    assert result.empty
