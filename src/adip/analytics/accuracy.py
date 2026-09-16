"""Forecast accuracy metrics computed against genuine observed data only.

Every metric here requires a real join between a forecast row and an
observed_weather row for the same (city_id, timestamp). If no observed row
exists yet (the archive API lags real time), that target hour is simply
excluded — never imputed or guessed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def join_forecast_to_observed(
    forecast_df: pd.DataFrame, observed_df: pd.DataFrame
) -> pd.DataFrame:
    """Inner join on (city_id, timestamp). Only rows with a genuine observed
    match survive — this is intentional: we never fabricate a
    "ground truth" for hours the archive hasn't finalized yet.
    """
    if forecast_df.empty or observed_df.empty:
        return pd.DataFrame()
    merged = forecast_df.merge(
        observed_df,
        left_on=["city_id", "target_ts"],
        right_on=["city_id", "observed_ts"],
        suffixes=("_forecast", "_observed"),
        how="inner",
    )
    merged["error_c"] = merged["temperature_c_forecast"] - merged["temperature_c_observed"]
    return merged


def accuracy_metrics(
    joined: pd.DataFrame, group_cols: list[str] | None = None
) -> pd.DataFrame:
    """Compute MAE, RMSE, and mean bias, optionally grouped (e.g. by
    ['city_id'] or ['requested_horizon_h']).

    MAE (mean absolute error) and RMSE (root mean squared error) measure
    magnitude of error; bias (mean signed error) reveals systematic
    over/under-prediction.
    """
    if joined.empty:
        return pd.DataFrame(columns=(group_cols or []) + ["mae_c", "rmse_c", "bias_c", "n"])

    def _agg(g: pd.DataFrame) -> pd.Series:
        err = g["error_c"].dropna()
        if err.empty:
            return pd.Series({"mae_c": np.nan, "rmse_c": np.nan, "bias_c": np.nan, "n": 0})
        return pd.Series(
            {
                "mae_c": round(float(err.abs().mean()), 2),
                "rmse_c": round(float(np.sqrt((err**2).mean())), 2),
                "bias_c": round(float(err.mean()), 2),
                "n": int(err.count()),
            }
        )

    if group_cols:
        return joined.groupby(group_cols).apply(_agg).reset_index()
    return _agg(joined).to_frame().T


def precipitation_accuracy(joined: pd.DataFrame, wet_threshold_mm: float = 0.2) -> dict:
    """Binary wet/dry classification accuracy — a more meaningful precipitation
    metric than raw mm error, since precipitation forecasts are inherently
    more about occurrence than exact amount.
    """
    if joined.empty or "precipitation_mm_forecast" not in joined.columns:
        return {"n": 0}
    df = joined.dropna(subset=["precipitation_mm_forecast", "precipitation_mm_observed"])
    if df.empty:
        return {"n": 0}
    pred_wet = df["precipitation_mm_forecast"] >= wet_threshold_mm
    obs_wet = df["precipitation_mm_observed"] >= wet_threshold_mm
    accuracy = float((pred_wet == obs_wet).mean())
    return {
        "n": int(len(df)),
        "wet_dry_accuracy": round(accuracy, 3),
        "wet_threshold_mm": wet_threshold_mm,
    }
