from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from adip.config import ApiConfig, City, ForecastConfig
from adip.ingestion.open_meteo_client import (
    OpenMeteoHTTPError,
    OpenMeteoSchemaError,
    OpenMeteoTimeoutError,
    _validate_forecast_shape,
    fetch_forecast,
)

CITY = City(
    id="test_city",
    name="Test City",
    country="XX",
    latitude=0.0,
    longitude=0.0,
    timezone="UTC",
)
API_CFG = ApiConfig(
    forecast_base_url="https://api.open-meteo.com/v1/forecast",
    archive_base_url="https://archive-api.open-meteo.com/v1/archive",
    request_timeout_seconds=5,
    max_retries=2,
    backoff_base_seconds=0.01,
    min_seconds_between_requests=0,
)
FORECAST_CFG = ForecastConfig(
    hourly_variables=("temperature_2m",),
    daily_variables=("temperature_2m_max",),
    horizons_hours=(24,),
    forecast_days=3,
)


def _mock_response(status_code=200, json_data=None, text=""):
    resp = Mock()
    resp.status_code = status_code
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = ValueError("no json")
    return resp


def test_fetch_forecast_success(sample_forecast_payload):
    with patch("requests.get", return_value=_mock_response(200, sample_forecast_payload)):
        result = fetch_forecast(CITY, API_CFG, FORECAST_CFG)
    assert result.city_id == "test_city"
    assert result.payload["hourly"]["time"]


def test_fetch_forecast_raises_on_schema_error(malformed_payload):
    with patch("requests.get", return_value=_mock_response(200, malformed_payload)):
        with pytest.raises(OpenMeteoSchemaError):
            fetch_forecast(CITY, API_CFG, FORECAST_CFG)


def test_fetch_forecast_raises_on_client_error():
    with patch("requests.get", return_value=_mock_response(404, text="not found")):
        with pytest.raises(OpenMeteoHTTPError):
            fetch_forecast(CITY, API_CFG, FORECAST_CFG)


def test_fetch_forecast_retries_then_succeeds_on_server_error(sample_forecast_payload):
    responses = [_mock_response(500), _mock_response(200, sample_forecast_payload)]
    with patch("requests.get", side_effect=responses):
        result = fetch_forecast(CITY, API_CFG, FORECAST_CFG)
    assert result.city_id == "test_city"


def test_fetch_forecast_exhausts_retries_on_persistent_server_error():
    with patch("requests.get", return_value=_mock_response(503)):
        with pytest.raises(OpenMeteoHTTPError):
            fetch_forecast(CITY, API_CFG, FORECAST_CFG)


def test_fetch_forecast_raises_on_timeout():
    with patch("requests.get", side_effect=requests.Timeout("timed out")):
        with pytest.raises(OpenMeteoTimeoutError):
            fetch_forecast(CITY, API_CFG, FORECAST_CFG)


def test_fetch_forecast_raises_on_malformed_json():
    with patch("requests.get", return_value=_mock_response(200, None)):
        with pytest.raises(OpenMeteoSchemaError):
            fetch_forecast(CITY, API_CFG, FORECAST_CFG)


def test_fetch_forecast_raises_on_empty_body():
    with patch("requests.get", return_value=_mock_response(200, {})):
        with pytest.raises(OpenMeteoSchemaError):
            fetch_forecast(CITY, API_CFG, FORECAST_CFG)


def test_validate_forecast_shape_accepts_valid(sample_forecast_payload):
    _validate_forecast_shape(sample_forecast_payload, "test_city")  # should not raise


def test_validate_forecast_shape_rejects_missing_hourly_time():
    payload = {"latitude": 1, "longitude": 1, "hourly": {}, "daily": {}}
    with pytest.raises(OpenMeteoSchemaError):
        _validate_forecast_shape(payload, "test_city")
