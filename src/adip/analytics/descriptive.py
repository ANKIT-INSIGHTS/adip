"""Descriptive analytics: rolling averages, period-over-period change,
distribution summaries. All functions are pure and operate on DataFrames
pulled from DuckDB, so they're independently unit-testable.
"""

from __future__ import annotations

import pandas as pd


def rolling_average(
    df: pd.DataFrame,
    value_col: str,
    window_days: int,
    group_col: str = "city_id",
    time_col: str = "ts",
) -> pd.DataFrame:
    """Compute a per-group rolling average over a trailing time window.

    `time_col` must be a datetime64 column already present in `df` (default
    name "ts") — callers rename their timestamp column to this before
    calling, since different tables use different names (target_ts,
    observed_ts, retrieved_at).
    """
    out = df.sort_values([group_col, time_col]).copy()
    rolled = out.groupby(group_col).rolling(f"{window_days}D", on=time_col)[value_col].mean()
    # `rolled` is indexed by (group_col, time_col) in the same row order as
    # `out` (both sorted by [group_col, time_col]), so assigning by position
    # is safe; aligning by the MultiIndex directly would fail because `out`
    # still has its own integer index.
    out[f"rolling_{window_days}d_avg"] = rolled.to_numpy()
    return out


def period_over_period_change(
    df: pd.DataFrame, value_col: str, group_col: str = "city_id", time_col: str = "ts"
) -> pd.DataFrame:
    """Latest value minus previous value, per group, sorted by time."""
    out = df.sort_values([group_col, time_col]).copy()
    out["prev_value"] = out.groupby(group_col)[value_col].shift(1)
    out["change"] = out[value_col] - out["prev_value"]
    return out


def distribution_summary(df: pd.DataFrame, value_col: str) -> dict:
    series = df[value_col].dropna()
    if series.empty:
        return {"count": 0}
    return {
        "count": int(series.count()),
        "mean": round(float(series.mean()), 2),
        "std": round(float(series.std()), 2) if series.count() > 1 else 0.0,
        "min": round(float(series.min()), 2),
        "p25": round(float(series.quantile(0.25)), 2),
        "median": round(float(series.median()), 2),
        "p75": round(float(series.quantile(0.75)), 2),
        "max": round(float(series.max()), 2),
    }


def largest_changes(
    df: pd.DataFrame,
    value_col: str,
    top_n: int,
    group_col: str = "city_id",
    time_col: str = "ts",
) -> pd.DataFrame:
    """Top-N largest absolute period-over-period changes, most recent first
    per group.
    """
    changed = period_over_period_change(df, value_col, group_col, time_col)
    changed = changed.dropna(subset=["change"])
    changed["abs_change"] = changed["change"].abs()
    return changed.sort_values("abs_change", ascending=False).head(top_n)
