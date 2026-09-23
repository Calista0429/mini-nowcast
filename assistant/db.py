"""Read-only DuckDB access for the assistant and the dashboard."""
from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("MINI_NOWCAST_DB", ROOT / "data" / "mini_nowcast.duckdb"))


def connect() -> duckdb.DuckDBPyConnection:
    # read_only: no writes even if a query slipped past the guard.
    # enable_external_access=false: no reading local files / URLs from inside SQL.
    return duckdb.connect(
        str(DB_PATH), read_only=True, config={"enable_external_access": False}
    )


def query(sql: str) -> pd.DataFrame:
    with connect() as con:
        return con.execute(sql).df()
