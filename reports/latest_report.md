# ADIP — Latest Weather Intelligence Report

_Generated automatically by the ADIP pipeline. All figures below are computed
directly from Open-Meteo forecast and archive data — nothing in this report
is manually written or fabricated._

## Executive Summary

Pipeline run completed at **2026-09-17T00:40:56.102391+00:00** covering
**16/16** configured cities and
**2688** ingested records in 476.1s.

**Status:** ✅ All cities succeeded

## Data Coverage

- Cities attempted: 16
- Cities succeeded: 16
- Records ingested this run: 2688

## Data Quality

- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=new_york
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=los_angeles
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=london
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=paris
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=berlin
- ✅ **freshness_hours**: 0.02 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=madrid
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=moscow
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=dubai
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=mumbai
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=singapore
- ✅ **freshness_hours**: 0.02 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=tokyo
- ✅ **freshness_hours**: 0.01 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=sydney
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=sao_paulo
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=cairo
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=nairobi
- ✅ **freshness_hours**: 0.0 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh
- ✅ **null_fraction**: 0.0 (threshold 0.02) — Max null fraction across ['temperature_c', 'relative_humidity']
- ✅ **duplicate_fraction**: 0.0 (threshold 0.0) — Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts']
- ✅ **row_count**: 168 (threshold 24) — Row count for city=reykjavik
- ✅ **freshness_hours**: 0.01 (threshold 26) — Hours since most recent data point
- ✅ **range_temperature_c**: 0 (threshold [-90.0, 60.0]) — Values outside physically plausible range for temperature_c
- ✅ **range_relative_humidity**: 0 (threshold [0.0, 100.0]) — Values outside physically plausible range for relative_humidity
- ✅ **range_wind_speed_kmh**: 0 (threshold [0.0, 500.0]) — Values outside physically plausible range for wind_speed_kmh

## Key Metrics

- **current_temperature_distribution_c**: {'count': 62, 'mean': 19.42, 'std': 6.6, 'min': 8.7, 'p25': 14.95, 'median': 16.9, 'p75': 25.95, 'max': 31.4}

## Major Changes

- **sydney**: +3.9°C (now 15.6°C)
- **los_angeles**: -3.4°C (now 23.9°C)
- **new_york**: -3.0°C (now 21.9°C)
- **singapore**: +2.5°C (now 27.5°C)
- **cairo**: -1.8°C (now 26.5°C)

## Anomalies

_No anomalies detected this run._

## Trends

Forecasts are revised by a mean of 0.14°C (max 7.7°C) between consecutive issue times, based on 7608 revision pair(s) observed so far.

## Model Results

_No model results this run (insufficient observed data for scoring)._

## Limitations

- None recorded.

- Forecast accuracy can only be computed for target hours where ERA5
  archive (observed) data has already been finalized, which lags real time
  by several days — recent forecasts are therefore not yet scoreable.
- Weather forecasting skill inherently degrades with lead time; metrics by
  horizon should be read as a property of the underlying model, not of this
  pipeline.
- Chart byte-for-byte reproducibility across matplotlib versions is not
  guaranteed; change detection tolerates this by only committing charts
  whose pixel content differs.

## Pipeline Run Information

- Started: 2026-09-17T00:33:00.013149+00:00
- Finished: 2026-09-17T00:40:56.102391+00:00
- Duration: 476.1s
- Data source: [Open-Meteo](https://open-meteo.com/) (forecast + archive APIs)
