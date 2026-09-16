"""Anomaly detection using the modified z-score (median + MAD), which is
robust to the outliers it's trying to detect — a plain mean/stddev z-score
gets dragged by the very anomalies you want to find.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from adip.config import AnomalyConfig

_MAD_SCALE = 0.6745  # makes MAD comparable to standard deviation for normal data


def modified_zscores(series: pd.Series) -> pd.Series:
    median = series.median()
    mad = (series - median).abs().median()
    if mad == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return _MAD_SCALE * (series - median) / mad


def detect_anomalies(
    df: pd.DataFrame,
    value_col: str,
    cfg: AnomalyConfig,
    group_col: str = "city_id",
    min_group_size: int | None = None,
) -> pd.DataFrame:
    """Flag rows whose |modified z-score| exceeds cfg.threshold, computed
    per group (e.g. per city) so a hot city doesn't get flagged relative to
    a cold one.

    Groups smaller than min_group_size (defaults to cfg.min_history_days)
    are skipped entirely rather than producing an unreliable z-score from a
    tiny sample.
    """
    min_size = min_group_size or cfg.min_history_days
    out_frames = []
    for _, group in df.groupby(group_col):
        if len(group) < min_size:
            continue
        g = group.copy()
        g["modified_zscore"] = modified_zscores(g[value_col])
        g["is_anomaly"] = g["modified_zscore"].abs() > cfg.threshold
        out_frames.append(g)
    if not out_frames:
        return df.iloc[0:0].assign(modified_zscore=[], is_anomaly=[])
    return pd.concat(out_frames, ignore_index=True)
