"""Load the UCI Online Retail II workbook into DuckDB (schema `raw`).

The xlsx is slow to parse, so it is converted to Parquet once and cached.
Every run appends a row to raw.ingest_log so data volume can be audited.
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "raw" / "online_retail_II.xlsx"
PARQUET = ROOT / "data" / "processed" / "online_retail_ii.parquet"
DB = ROOT / "data" / "mini_nowcast.duckdb"


def xlsx_to_parquet() -> None:
    if PARQUET.exists():
        print(f"[skip] cached parquet: {PARQUET.name}")
        return
    t0 = time.time()
    sheets = pd.read_excel(XLSX, sheet_name=None, dtype={"Invoice": str, "StockCode": str, "Description": str})
    frames = []
    for name, df in sheets.items():
        df["source_sheet"] = name
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df.to_parquet(PARQUET, index=False)
    print(f"[ok] xlsx -> parquet: {len(df):,} rows in {time.time() - t0:.0f}s")


def load_duckdb() -> None:
    con = duckdb.connect(str(DB))
    con.execute("create schema if not exists raw")
    con.execute(
        f"create or replace table raw.online_retail as select * from read_parquet('{PARQUET}')"
    )
    n = con.execute("select count(*) from raw.online_retail").fetchone()[0]
    con.execute(
        "create table if not exists raw.ingest_log(loaded_at timestamp, source varchar, row_count bigint)"
    )
    con.execute("insert into raw.ingest_log values (?, ?, ?)", [datetime.now(), XLSX.name, n])
    con.close()
    print(f"[ok] raw.online_retail: {n:,} rows -> {DB.name}")


if __name__ == "__main__":
    xlsx_to_parquet()
    load_duckdb()
