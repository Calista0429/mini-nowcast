"""Validate LLM-generated SQL before it touches the database.

The model's output is treated as untrusted input:
  * exactly one statement, and it must be a read-only query (SELECT / set operation)
  * no DML/DDL or engine commands anywhere in the tree (INSERT, COPY, ATTACH, PRAGMA ...)
  * only tables listed in the semantic layer; no table functions such as read_csv()
  * a row cap is added when the query has no LIMIT

Execution also happens on a read-only connection (see assistant/db.py) as a second line of defence.
"""
from __future__ import annotations

from dataclasses import dataclass

import sqlglot
from sqlglot import exp

MAX_ROWS = 1000

_FORBIDDEN = (
    exp.Insert, exp.Update, exp.Delete, exp.Merge, exp.Create, exp.Drop, exp.Alter,
    exp.Command, exp.Copy, exp.Set, exp.Pragma, exp.Attach, exp.Detach, exp.Use,
    exp.Transaction, exp.Commit, exp.Rollback, exp.LoadData, exp.Describe,
)


class UnsafeSQLError(ValueError):
    """Raised when generated SQL violates a guard rule. The message is fed back to the LLM."""


@dataclass(frozen=True)
class GuardedSQL:
    sql: str
    tables: tuple[str, ...]
    limit_added: bool


def guard_sql(sql: str, allowed_tables: set[str], max_rows: int = MAX_ROWS) -> GuardedSQL:
    try:
        statements = [s for s in sqlglot.parse(sql, read="duckdb") if s is not None]
    except sqlglot.errors.ParseError as e:
        raise UnsafeSQLError(f"SQL could not be parsed: {e}") from e
    if len(statements) != 1:
        raise UnsafeSQLError(f"Expected exactly one statement, got {len(statements)}.")
    tree = statements[0]

    if not isinstance(tree, exp.Query):
        raise UnsafeSQLError(f"Only SELECT queries are allowed, got {tree.key.upper()}.")
    for node in tree.walk():
        if isinstance(node, _FORBIDDEN):
            raise UnsafeSQLError(f"Statement type {node.key.upper()} is not allowed.")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    used: set[str] = set()
    for table in tree.find_all(exp.Table):
        if not isinstance(table.this, exp.Identifier):
            raise UnsafeSQLError(f"Table functions are not allowed: {table.sql(dialect='duckdb')}")
        name = table.name.lower()
        if not table.db and name in cte_names:
            continue
        qualified = f"{table.db}.{name}".lower() if table.db else name
        if qualified not in allowed_tables:
            raise UnsafeSQLError(
                f"Table '{qualified}' is not allowed. Use only: {', '.join(sorted(allowed_tables))}."
            )
        used.add(qualified)

    out = tree.sql(dialect="duckdb")
    limit_added = tree.args.get("limit") is None
    if limit_added:
        out = f"select * from ({out}) as q limit {max_rows}"
    return GuardedSQL(sql=out, tables=tuple(sorted(used)), limit_added=limit_added)
