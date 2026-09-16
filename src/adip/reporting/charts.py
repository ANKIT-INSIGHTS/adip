"""Generate chart PNGs with matplotlib.

Charts are written with a fixed DPI and deterministic styling so that
identical underlying data produces byte-identical (or near-identical) PNGs
run to run — this matters because change_detection hashes PNGs by raw bytes.
Matplotlib's Agg backend with a fixed dpi is deterministic enough in practice
for this project's purposes; true bit-for-bit determinism is not guaranteed
across matplotlib versions, which is a documented limitation (see
docs/architecture.md).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from adip.config import REPO_ROOT  # noqa: E402

FIGURES_DIR = REPO_ROOT / "reports" / "figures"
DPI = 110
plt.rcParams.update({"figure.dpi": DPI, "savefig.dpi": DPI, "font.size": 10})


def _save(fig: plt.Figure, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def temperature_trend_chart(df: pd.DataFrame, city_id: str) -> Path:
    fig, ax = plt.subplots(figsize=(8, 4))
    subset = df[df["city_id"] == city_id].sort_values("ts")
    ax.plot(subset["ts"], subset["temperature_c"], color="#c0392b", linewidth=1.5)
    ax.set_title(f"Temperature trend — {city_id}")
    ax.set_ylabel("°C")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    return _save(fig, f"temperature_trend_{city_id}")


def city_comparison_chart(df: pd.DataFrame, value_col: str, title: str, name: str) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5))
    latest = df.sort_values("ts").groupby("city_id").tail(1)
    latest = latest.sort_values(value_col, ascending=False)
    ax.bar(latest["city_id"], latest[value_col], color="#2980b9")
    ax.set_title(title)
    ax.set_ylabel(value_col)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    return _save(fig, name)


def forecast_error_by_horizon_chart(accuracy_by_horizon: pd.DataFrame) -> Path | None:
    if accuracy_by_horizon.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, 4))
    d = accuracy_by_horizon.sort_values("requested_horizon_h")
    ax.plot(d["requested_horizon_h"], d["mae_c"], marker="o", label="MAE (°C)")
    ax.plot(d["requested_horizon_h"], d["rmse_c"], marker="s", label="RMSE (°C)")
    ax.set_xlabel("Forecast horizon (hours)")
    ax.set_ylabel("Error (°C)")
    ax.set_title("Forecast error by lead time")
    ax.legend()
    ax.grid(alpha=0.3)
    return _save(fig, "forecast_error_by_horizon")


def anomaly_timeline_chart(df_with_anomalies: pd.DataFrame, value_col: str) -> Path | None:
    if df_with_anomalies.empty:
        return None
    fig, ax = plt.subplots(figsize=(9, 4))
    d = df_with_anomalies.sort_values("ts")
    ax.plot(d["ts"], d[value_col], color="#7f8c8d", linewidth=1, label="value")
    anomalies = d[d["is_anomaly"]]
    ax.scatter(
        anomalies["ts"], anomalies[value_col], color="#e74c3c", zorder=5, label="anomaly"
    )
    ax.set_title("Anomaly timeline")
    ax.legend()
    fig.autofmt_xdate()
    return _save(fig, "anomaly_timeline")
