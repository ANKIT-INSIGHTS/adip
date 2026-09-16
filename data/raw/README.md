# data/raw/

Immutable, append-only raw API responses — the project's source of truth.

- `data/raw/<YYYY-MM-DD>/<city_id>_<retrieved_at>.json` — forecast API
  snapshots, one per city per pipeline run.
- `data/raw/archive/<YYYY-MM-DD>/<city_id>_<start>_to_<end>.json` — ERA5
  archive ("observed") snapshots.

These files are committed to git and are what `scripts/rebuild_db.py` uses
to reconstruct the full analytical DuckDB database from scratch — see
`docs/architecture.md`. Never edit a file here by hand; every write goes
through `src/adip/ingestion/snapshot_writer.py`.

This file exists so the (initially empty) `data/raw/` directory survives a
git clone even before the pipeline has run for the first time.
