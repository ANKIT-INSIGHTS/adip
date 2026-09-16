# data/processed/

Reserved for optional intermediate Parquet exports (e.g. a periodic full
dump of the DuckDB tables for external analysis tools). Not currently
written by the default pipeline run — everything it needs lives in
`data/raw/` (source of truth) and the derived, gitignored DuckDB file at
`data/snapshots/adip.duckdb`. Kept as a placeholder extension point rather
than removed, since it's a natural place to add a `make export-parquet`
target later without restructuring the repo.
