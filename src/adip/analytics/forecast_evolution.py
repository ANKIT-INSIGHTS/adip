"""Compare forecasts issued at different times for the same target hour.

Example: three forecast runs (Mon, Tue, Wed morning) each predicted
Wednesday noon's temperature. This module aligns those predictions by
(city, target_ts) so we can see how the prediction converged (or didn't) as
the target hour approached — and, once observed data exists for that hour,
how far off the final forecast was.
"""

from __future__ import annotations

import pandas as pd


def forecast_revisions(snapshots: pd.DataFrame) -> pd.DataFrame:
    """Given all forecast_snapshots rows for a (city, target_ts) pair across
    multiple forecast_run_ts values, compute how the prediction changed
    between consecutive issue times.

    Expects columns: city_id, forecast_run_ts, target_ts, temperature_c
    """
    if snapshots.empty:
        return snapshots
    df = snapshots.sort_values(["city_id", "target_ts", "forecast_run_ts"]).copy()
    df["prev_temperature_c"] = df.groupby(["city_id", "target_ts"])["temperature_c"].shift(1)
    df["revision_c"] = df["temperature_c"] - df["prev_temperature_c"]
    return df


def revision_magnitude_summary(revisions: pd.DataFrame) -> dict:
    """Summarize how much forecasts typically get revised before landing."""
    valid = revisions.dropna(subset=["revision_c"])
    if valid.empty:
        return {"count": 0}
    return {
        "count": int(len(valid)),
        "mean_abs_revision_c": round(float(valid["revision_c"].abs().mean()), 2),
        "max_abs_revision_c": round(float(valid["revision_c"].abs().max()), 2),
    }


def latest_forecast_per_horizon(
    snapshots: pd.DataFrame, horizons_hours: tuple[int, ...]
) -> pd.DataFrame:
    """For each city and target hour, keep only the forecast row whose
    horizon is closest to each of the configured horizons (e.g. the "24h
    ahead" forecast for that target hour), which is what accuracy-by-horizon
    analysis needs.
    """
    if snapshots.empty:
        return snapshots
    frames = []
    for h in horizons_hours:
        df = snapshots.copy()
        df["horizon_distance"] = (df["forecast_horizon_h"] - h).abs()
        idx = df.groupby(["city_id", "target_ts"])["horizon_distance"].idxmin()
        nearest = df.loc[idx].copy()
        nearest = nearest[nearest["horizon_distance"] <= 3]  # 3h tolerance
        nearest["requested_horizon_h"] = h
        frames.append(nearest)
    return pd.concat(frames, ignore_index=True) if frames else snapshots.iloc[0:0]
