"""HTTP client for the Open-Meteo forecast and archive APIs.

Design goals:
    * Never fabricate data. If the API cannot be reached or returns something
      we don't understand, raise a clear, typed exception instead of guessing.
    * Be a good API citizen: timeouts, exponential backoff with jitter,
      bounded retries, self-throttling between requests.
    * Keep zero third-party service dependencies beyond `requests`.

Open-Meteo requires no API key. Attribution requirement (CC-BY-4.0-style,
see https://open-meteo.com/en/license) is documented in docs/DATA_SOURCES.md
and the README.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from random import SystemRandom
from typing import Any

import requests

from adip.config import ApiConfig, City, ForecastConfig

logger = logging.getLogger("adip.ingestion")
_RANDOM = SystemRandom()


class OpenMeteoError(Exception):
    """Base class for all Open-Meteo client failures."""


class OpenMeteoHTTPError(OpenMeteoError):
    """Raised for non-2xx HTTP responses after retries are exhausted."""


class OpenMeteoTimeoutError(OpenMeteoError):
    """Raised when all retry attempts time out."""


class OpenMeteoSchemaError(OpenMeteoError):
    """Raised when a 2xx response body doesn't match the expected shape."""


@dataclass(frozen=True, slots=True)
class ForecastFetchResult:
    """A single successful forecast fetch for one city.

    `retrieved_at` is the wall-clock moment the pipeline made the request —
    this is the "forecast_run_timestamp" that makes forecast-evolution
    analysis possible later. It is preserved verbatim and never overwritten.
    """

    city_id: str
    retrieved_at: datetime
    payload: dict[str, Any]


def _sleep_with_backoff(attempt: int, base_seconds: float) -> None:
    delay = base_seconds * (2**attempt) + _RANDOM.uniform(0, base_seconds)
    logger.warning("Retrying after %.2fs (attempt %d)", delay, attempt + 1)
    time.sleep(delay)


def _request_with_retries(
    url: str, params: dict[str, Any], api_cfg: ApiConfig
) -> dict[str, Any]:
    last_exc: Exception | None = None
    for attempt in range(api_cfg.max_retries + 1):
        try:
            response = requests.get(
                url, params=params, timeout=api_cfg.request_timeout_seconds
            )
        except requests.Timeout as exc:
            last_exc = exc
            logger.error("Request timed out (attempt %d): %s", attempt + 1, url)
            if attempt < api_cfg.max_retries:
                _sleep_with_backoff(attempt, api_cfg.backoff_base_seconds)
                continue
            raise OpenMeteoTimeoutError(
                f"Timed out after {api_cfg.max_retries + 1} attempts: {url}"
            ) from exc
        except requests.RequestException as exc:
            last_exc = exc
            logger.error("Network error (attempt %d): %s", attempt + 1, exc)
            if attempt < api_cfg.max_retries:
                _sleep_with_backoff(attempt, api_cfg.backoff_base_seconds)
                continue
            raise OpenMeteoHTTPError(
                f"Network error after {api_cfg.max_retries + 1} attempts: {exc}"
            ) from exc

        if response.status_code == 429:
            # Rate limited: always retry (does not count against "unexpected
            # error" budget the same way, but we still bound total attempts).
            logger.warning("Rate limited (429) on attempt %d", attempt + 1)
            if attempt < api_cfg.max_retries:
                _sleep_with_backoff(attempt, api_cfg.backoff_base_seconds * 2)
                continue
            raise OpenMeteoHTTPError("Rate limited and retries exhausted")

        if 500 <= response.status_code < 600:
            logger.warning("Server error %d on attempt %d", response.status_code, attempt + 1)
            if attempt < api_cfg.max_retries:
                _sleep_with_backoff(attempt, api_cfg.backoff_base_seconds)
                continue
            raise OpenMeteoHTTPError(
                f"Server error {response.status_code} after retries: {url}"
            )

        if response.status_code >= 400:
            # Client errors (bad params etc.) are not retryable.
            raise OpenMeteoHTTPError(
                f"Client error {response.status_code} for {url}: {response.text[:500]}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            last_exc = exc
            logger.error("Malformed JSON on attempt %d", attempt + 1)
            if attempt < api_cfg.max_retries:
                _sleep_with_backoff(attempt, api_cfg.backoff_base_seconds)
                continue
            raise OpenMeteoSchemaError(
                f"Response was not valid JSON after retries: {url}"
            ) from exc

        if not isinstance(data, dict) or not data:
            raise OpenMeteoSchemaError(f"Empty or non-object JSON body from {url}")

        if "error" in data:
            # Open-Meteo returns {"error": true, "reason": "..."} for bad
            # requests even with HTTP 200 in some cases.
            raise OpenMeteoSchemaError(
                f"Open-Meteo reported an error: {data.get('reason', data)}"
            )

        return data

    # Should be unreachable, but keeps type checkers and readers honest.
    raise OpenMeteoError(f"Exhausted retries without success: {last_exc}")


def fetch_forecast(
    city: City, api_cfg: ApiConfig, forecast_cfg: ForecastConfig
) -> ForecastFetchResult:
    """Fetch current + hourly + daily forecast for one city.

    Raises an OpenMeteoError subclass on any failure. Callers must not catch
    broadly and substitute fabricated data — a failed fetch should propagate
    as a failed pipeline run for that city.
    """
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "timezone": city.timezone,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ]
        ),
        "hourly": ",".join(forecast_cfg.hourly_variables),
        "daily": ",".join(forecast_cfg.daily_variables),
        "forecast_days": forecast_cfg.forecast_days,
    }
    retrieved_at = datetime.now(UTC)
    payload = _request_with_retries(api_cfg.forecast_base_url, params, api_cfg)
    _validate_forecast_shape(payload, city.id)
    return ForecastFetchResult(city_id=city.id, retrieved_at=retrieved_at, payload=payload)


def fetch_archive(
    city: City,
    api_cfg: ApiConfig,
    forecast_cfg: ForecastConfig,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Fetch ERA5-reanalysis "observed" data for a finalized date range.

    This is genuinely observed/historical data, distinct from forecasts.
    Callers are responsible for only requesting date ranges old enough to be
    finalized (see ArchiveConfig.min_days_lag).
    """
    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "timezone": city.timezone,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(forecast_cfg.hourly_variables),
        "daily": ",".join(forecast_cfg.daily_variables),
    }
    payload = _request_with_retries(api_cfg.archive_base_url, params, api_cfg)
    _validate_forecast_shape(payload, city.id)
    return payload


def _validate_forecast_shape(payload: dict[str, Any], city_id: str) -> None:
    """Minimal structural validation independent of full Pydantic parsing.

    Fails fast and loudly rather than letting a malformed payload silently
    propagate into storage.
    """
    required_top_level = {"latitude", "longitude", "hourly", "daily"}
    missing = required_top_level - payload.keys()
    if missing:
        raise OpenMeteoSchemaError(f"[{city_id}] Missing required top-level keys: {missing}")
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict) or "time" not in hourly or not hourly["time"]:
        raise OpenMeteoSchemaError(f"[{city_id}] Hourly block missing or empty 'time' array")
