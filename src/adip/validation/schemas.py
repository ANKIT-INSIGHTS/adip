"""Pydantic models describing the Open-Meteo response shapes we depend on.

These exist to catch upstream schema drift (a new/renamed field, a changed
type) at the earliest possible point, with a clear error, instead of letting
malformed data silently flow into DuckDB and reports.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class HourlyBlock(BaseModel):
    time: list[str]
    temperature_2m: list[float | None] = Field(default_factory=list)
    apparent_temperature: list[float | None] = Field(default_factory=list)
    relative_humidity_2m: list[float | None] = Field(default_factory=list)
    precipitation: list[float | None] = Field(default_factory=list)
    wind_speed_10m: list[float | None] = Field(default_factory=list)
    weather_code: list[int | None] = Field(default_factory=list)

    @field_validator("time")
    @classmethod
    def _time_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("hourly.time must not be empty")
        return v


class DailyBlock(BaseModel):
    time: list[str]
    temperature_2m_max: list[float | None] = Field(default_factory=list)
    temperature_2m_min: list[float | None] = Field(default_factory=list)
    precipitation_sum: list[float | None] = Field(default_factory=list)
    sunshine_duration: list[float | None] = Field(default_factory=list)
    sunrise: list[str] = Field(default_factory=list)
    sunset: list[str] = Field(default_factory=list)


class CurrentBlock(BaseModel):
    time: str
    temperature_2m: float | None = None
    apparent_temperature: float | None = None
    relative_humidity_2m: float | None = None
    precipitation: float | None = None
    wind_speed_10m: float | None = None
    weather_code: int | None = None


class ForecastResponse(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    hourly: HourlyBlock
    daily: DailyBlock
    current: CurrentBlock | None = None

    def hourly_row_count(self) -> int:
        return len(self.hourly.time)
