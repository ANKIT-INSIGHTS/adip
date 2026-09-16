-- ADIP analytical schema (DuckDB).
-- This database is a DERIVED artifact: it is rebuilt from data/raw/*.json and
-- data/processed/*.parquet on every pipeline run (see scripts/rebuild_db.py)
-- and is NOT committed to git, so it never produces noisy binary diffs.

CREATE TABLE IF NOT EXISTS forecast_snapshots (
    city_id             VARCHAR NOT NULL,
    forecast_run_ts     TIMESTAMP NOT NULL,   -- when the forecast was retrieved
    target_ts           TIMESTAMP NOT NULL,   -- the hour this row predicts
    forecast_horizon_h  INTEGER NOT NULL,     -- target_ts - forecast_run_ts, in hours
    model               VARCHAR NOT NULL,     -- open-meteo default model blend
    temperature_c       DOUBLE,
    apparent_temp_c     DOUBLE,
    relative_humidity   DOUBLE,
    precipitation_mm    DOUBLE,
    wind_speed_kmh      DOUBLE,
    weather_code        INTEGER,
    source_file         VARCHAR NOT NULL,     -- provenance: raw JSON path
    PRIMARY KEY (city_id, forecast_run_ts, target_ts)
);

CREATE TABLE IF NOT EXISTS observed_weather (
    city_id             VARCHAR NOT NULL,
    observed_ts         TIMESTAMP NOT NULL,
    temperature_c       DOUBLE,
    relative_humidity   DOUBLE,
    precipitation_mm    DOUBLE,
    wind_speed_kmh      DOUBLE,
    weather_code        INTEGER,
    source              VARCHAR NOT NULL DEFAULT 'era5-archive-reanalysis',
    source_file         VARCHAR NOT NULL,
    PRIMARY KEY (city_id, observed_ts)
);

CREATE TABLE IF NOT EXISTS current_conditions (
    city_id             VARCHAR NOT NULL,
    retrieved_at        TIMESTAMP NOT NULL,
    temperature_c       DOUBLE,
    apparent_temp_c     DOUBLE,
    relative_humidity   DOUBLE,
    precipitation_mm    DOUBLE,
    wind_speed_kmh      DOUBLE,
    weather_code        INTEGER,
    source_file         VARCHAR NOT NULL,
    PRIMARY KEY (city_id, retrieved_at)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id              VARCHAR PRIMARY KEY,
    started_at          TIMESTAMP NOT NULL,
    finished_at         TIMESTAMP,
    status              VARCHAR NOT NULL,     -- success | partial_failure | failure
    cities_attempted    INTEGER,
    cities_succeeded    INTEGER,
    records_ingested    INTEGER,
    anomalies_detected  INTEGER,
    commit_created      BOOLEAN
);
