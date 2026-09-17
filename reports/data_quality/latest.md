# Data Quality Report

_Generated: 2026-09-17T06:40:10.388140+00:00_

**Overall status:** ✅ PASS (105/105 checks passed)

| City | Check | Passed | Measured | Threshold | Detail |
|---|---|---|---|---|---|
| new_york | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| new_york | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| new_york | row_count | ✅ | 168 | 24 | Row count for city=new_york |
| new_york | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| new_york | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| new_york | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| new_york | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| los_angeles | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| los_angeles | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| los_angeles | row_count | ✅ | 168 | 24 | Row count for city=los_angeles |
| los_angeles | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| los_angeles | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| los_angeles | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| los_angeles | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| london | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| london | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| london | row_count | ✅ | 168 | 24 | Row count for city=london |
| london | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| london | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| london | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| london | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| paris | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| paris | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| paris | row_count | ✅ | 168 | 24 | Row count for city=paris |
| paris | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| paris | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| paris | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| paris | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| berlin | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| berlin | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| berlin | row_count | ✅ | 168 | 24 | Row count for city=berlin |
| berlin | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| berlin | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| berlin | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| berlin | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| moscow | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| moscow | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| moscow | row_count | ✅ | 168 | 24 | Row count for city=moscow |
| moscow | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| moscow | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| moscow | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| moscow | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| dubai | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| dubai | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| dubai | row_count | ✅ | 168 | 24 | Row count for city=dubai |
| dubai | freshness_hours | ✅ | 0.01 | 26 | Hours since most recent data point |
| dubai | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| dubai | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| dubai | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| mumbai | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| mumbai | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| mumbai | row_count | ✅ | 168 | 24 | Row count for city=mumbai |
| mumbai | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| mumbai | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| mumbai | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| mumbai | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| singapore | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| singapore | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| singapore | row_count | ✅ | 168 | 24 | Row count for city=singapore |
| singapore | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| singapore | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| singapore | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| singapore | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| tokyo | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| tokyo | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| tokyo | row_count | ✅ | 168 | 24 | Row count for city=tokyo |
| tokyo | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| tokyo | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| tokyo | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| tokyo | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| sydney | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| sydney | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| sydney | row_count | ✅ | 168 | 24 | Row count for city=sydney |
| sydney | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| sydney | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| sydney | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| sydney | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| sao_paulo | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| sao_paulo | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| sao_paulo | row_count | ✅ | 168 | 24 | Row count for city=sao_paulo |
| sao_paulo | freshness_hours | ✅ | 0.01 | 26 | Hours since most recent data point |
| sao_paulo | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| sao_paulo | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| sao_paulo | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| cairo | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| cairo | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| cairo | row_count | ✅ | 168 | 24 | Row count for city=cairo |
| cairo | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| cairo | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| cairo | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| cairo | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| nairobi | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| nairobi | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| nairobi | row_count | ✅ | 168 | 24 | Row count for city=nairobi |
| nairobi | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| nairobi | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| nairobi | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| nairobi | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
| reykjavik | null_fraction | ✅ | 0.0 | 0.02 | Max null fraction across ['temperature_c', 'relative_humidity'] |
| reykjavik | duplicate_fraction | ✅ | 0.0 | 0.0 | Duplicate fraction on key ['city_id', 'forecast_run_ts', 'target_ts'] |
| reykjavik | row_count | ✅ | 168 | 24 | Row count for city=reykjavik |
| reykjavik | freshness_hours | ✅ | 0.0 | 26 | Hours since most recent data point |
| reykjavik | range_temperature_c | ✅ | 0 | [-90.0, 60.0] | Values outside physically plausible range for temperature_c |
| reykjavik | range_relative_humidity | ✅ | 0 | [0.0, 100.0] | Values outside physically plausible range for relative_humidity |
| reykjavik | range_wind_speed_kmh | ✅ | 0 | [0.0, 500.0] | Values outside physically plausible range for wind_speed_kmh |
