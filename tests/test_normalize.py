from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from adip.transformation.normalize import (
    archive_payload_to_observed_rows,
    forecast_payload_to_current_row,
    forecast_payload_to_snapshot_rows,
)


def test_forecast_payload_to_snapshot_rows_row_count(sample_forecast_payload):
    run_ts = datetime(2026, 9, 16, 9, 0)
    df = forecast_payload_to_snapshot_rows(
        "test_city", run_ts, sample_forecast_payload, "raw/x.json"
    )
    assert len(df) == 3
    assert set(df["city_id"]) == {"test_city"}


def test_forecast_horizon_is_hours_from_run_ts(sample_forecast_payload):
    run_ts = datetime(2026, 9, 16, 9, 0)
    df = forecast_payload_to_snapshot_rows(
        "test_city", run_ts, sample_forecast_payload, "raw/x.json"
    )
    # first hourly entry equals run_ts -> horizon 0; second is +1h; third +2h
    assert list(df["forecast_horizon_h"]) == [0, 1, 2]


def test_forecast_payload_to_current_row(sample_forecast_payload):
    run_ts = datetime(2026, 9, 16, 9, 0)
    df = forecast_payload_to_current_row(
        "test_city", run_ts, sample_forecast_payload, "raw/x.json"
    )
    assert len(df) == 1
    assert df.iloc[0]["temperature_c"] == 21.4


def test_archive_payload_to_observed_rows(sample_forecast_payload):
    df = archive_payload_to_observed_rows("test_city", sample_forecast_payload, "raw/a.json")
    assert len(df) == 3
    assert set(df["source"]) == {"era5-archive-reanalysis"}


def test_snapshot_rows_raises_on_malformed(malformed_payload):
    with pytest.raises(ValidationError):
        forecast_payload_to_snapshot_rows(
            "test_city", datetime(2026, 9, 16), malformed_payload, "raw/x.json"
        )
