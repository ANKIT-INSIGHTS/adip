"""DuckDB access layer.

The DuckDB file itself is a build artifact (gitignored, rebuilt every run
from raw JSON + processed Parquet), which keeps git history free of noisy
binary diffs while still giving us fast analytical SQL locally and in CI.
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from adip.config import REPO_ROOT

logger = logging.getLogger("adip.storage")

DB_PATH = REPO_ROOT / "data" / "snapshots" / "adip.duckdb"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    _apply_schema(con)
    return con


def _apply_schema(con: duckdb.DuckDBPyConnection) -> None:
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    con.execute(ddl)


def table_row_count(con: duckdb.DuckDBPyConnection, table: str) -> int:
    return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # noqa: S608
