# data/snapshots/

Holds `adip.duckdb`, the derived analytical database — **gitignored**, not
committed. It's rebuilt deterministically from `data/raw/**/*.json` by
`scripts/rebuild_db.py` (run automatically at the start of every pipeline
execution, or manually via `make rebuild-db`).

This design choice — derive, don't commit — exists specifically to avoid
the single biggest source of noisy, meaningless-looking diffs in a project
like this: a binary database file that changes on every run regardless of
whether the underlying data actually changed. See "Why DuckDB is not
committed to git" in `docs/architecture.md` for the full rationale.
