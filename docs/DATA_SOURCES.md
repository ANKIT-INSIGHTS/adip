# Data Sources & Provenance

## Open-Meteo

ADIP's only external data dependency is [Open-Meteo](https://open-meteo.com/),
used via two of its APIs:

| API | Purpose | Data class |
|---|---|---|
| `api.open-meteo.com/v1/forecast` | Current conditions + hourly/daily forecast | **Forecast** and **current** |
| `archive-api.open-meteo.com/v1/archive` | ERA5 reanalysis for finalized past dates | **Observed/historical** |

### Why these two endpoints, and why the split matters

The forecast endpoint returns a prediction — it is never treated as ground
truth, even after the fact. The archive endpoint returns ERA5 reanalysis, a
scientifically validated blend of historical observations and modeling used
by meteorologists as a best estimate of what actually happened at a
location. ADIP treats archive data as "observed" for accuracy scoring, but
this is itself an approximation, not a raw station reading — this
distinction is documented here and in `reports/latest_report.md`'s
Limitations section so nobody mistakes reanalysis for direct measurement.

### Attribution & licensing

Open-Meteo's data is available under a
[CC-BY-4.0-compatible license](https://open-meteo.com/en/license) for
non-commercial use, requiring attribution. Accordingly:

- Every raw snapshot file records `"source"` and the retrieval endpoint.
- The README displays a visible "Data provided by Open-Meteo.com" credit.
- ADIP does not resell, relicense, or claim ownership of the underlying
  weather data — only of the pipeline code and the derived analytics it
  computes.

### Reliability characteristics relied upon by this project

- No API key or authentication required.
- No hard-published rate limit for the request volume this project makes
  (~16 cities × 1 forecast call × several times/day); ADIP self-throttles
  and backs off on `429` regardless.
- The archive/reanalysis endpoint lags real time by several days while ERA5
  data is finalized — `configs/pipeline.yaml`'s `archive.min_days_lag`
  encodes this and is the reason very recent forecasts cannot yet be scored
  for accuracy.

### What ADIP never does

- Never fabricates a value the API did not return.
- Never backfills missing history with interpolated or synthetic data.
- Never presents forecast data as if it were observed, or vice versa.
