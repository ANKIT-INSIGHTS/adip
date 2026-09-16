"""Static consistency check: every SQL INSERT's placeholder count must match
its target table's column count in schema.sql.

This exists because a mismatch here is a silent, easy-to-introduce bug (as
happened during development) that unit tests exercising the DataFrame
transformation logic alone would never catch — it only manifests when
DuckDB actually executes the statement. Parsing this statically means the
test suite catches it without needing DuckDB installed.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "src" / "adip" / "storage" / "schema.sql"
SQL_FILES = [
    REPO_ROOT / "scripts" / "run_pipeline.py",
    REPO_ROOT / "scripts" / "rebuild_db.py",
]


def _table_column_counts() -> dict[str, int]:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    tables = {}
    for m in re.finditer(r"CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\n\);", schema, re.S):
        name, body = m.group(1), m.group(2)
        cols = [
            line.strip().split()[0]
            for line in body.splitlines()
            if line.strip() and not line.strip().upper().startswith("PRIMARY")
        ]
        tables[name] = len(cols)
    return tables


def test_insert_placeholder_counts_match_schema():
    tables = _table_column_counts()
    assert tables, "Failed to parse any tables from schema.sql — regex may be stale"

    mismatches = []
    for path in SQL_FILES:
        src = path.read_text(encoding="utf-8")
        for m in re.finditer(r"INSERT(?: OR REPLACE)? INTO (\w+) VALUES\s*\(([^)]*)\)", src):
            table, placeholders = m.group(1), m.group(2)
            n_placeholders = placeholders.count("?")
            n_columns = tables.get(table)
            if n_columns is None:
                mismatches.append(f"{path.name}: unknown table '{table}'")
            elif n_placeholders != n_columns:
                mismatches.append(
                    f"{path.name}: INSERT INTO {table} has {n_placeholders} "
                    f"placeholders but table has {n_columns} columns"
                )
    assert not mismatches, "\n".join(mismatches)
