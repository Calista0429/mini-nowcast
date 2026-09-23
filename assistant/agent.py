"""Natural-language questions -> guarded SQL -> result -> grounded answer.

Pipeline
  1. plan    LLM writes one SQL query (plus chart hint) from the semantic layer, or declines.
  2. guard   sql_guard rejects anything that is not a read-only query on allowed tables.
  3. run     execute on a read-only connection; on a guard/SQL error, the error is sent back
             to the LLM for a corrected query (up to MAX_ATTEMPTS).
  4. answer  LLM summarises only the returned rows, and lists every number it cites.
  5. verify  each cited number is checked against the result cells; unmatched ones are flagged.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import duckdb
import pandas as pd

from . import db, semantic
from .llm import ChatClient, LLMClient, Usage
from .sql_guard import UnsafeSQLError, guard_sql

MAX_ATTEMPTS = 3
ANSWER_ROWS = 60  # rows shown to the model when writing the answer
LOG_PATH = Path(__file__).resolve().parents[1] / "data" / "assistant_log.jsonl"

PLAN_SYSTEM = """You translate business questions into one DuckDB SQL query.

{schema}

Rules:
- Use only the tables above, with their fully qualified names.
- Respect each table's grain. Columns marked NOT additive must not be summed across rows.
- Prefer returning a small, already-aggregated result (at most a few dozen rows).
- If the question cannot be answered from these tables, do not guess: set "sql" to null
  and explain why in "cannot_answer_reason".

Reply with a JSON object:
{{
  "sql": "<one SELECT statement, or null>",
  "chart": {{"type": "line" | "bar" | "table", "x": "<column or null>", "y": "<column or null>", "color": "<column or null>"}},
  "assumptions": ["<interpretation choices you made, e.g. which period 'last year' means>"],
  "cannot_answer_reason": "<only when sql is null>"
}}"""

ANSWER_SYSTEM = """You explain query results to a business user.
Answer in the same language as the question. Be concise: 2-4 sentences.
Use ONLY numbers that appear in the result rows, or simple arithmetic on them
(differences, ratios, percent changes). Never invent data that is not in the rows.
If the rows are empty or cannot answer the question, say so.
List every quantity you mention in cited_numbers (amounts, counts, ratios, index values),
but not dates, years or month names.

Reply with a JSON object:
{
  "answer": "<the answer text>",
  "cited_numbers": [{"text": "<number as written in the answer>", "value": <the underlying number as a plain float, e.g. 0.047 for 4.7%>, "derived": <true if you computed it, false if copied from a cell>}]
}"""


@dataclass
class Attempt:
    sql: str | None
    error: str | None = None


@dataclass
class CitedNumber:
    text: str
    value: float
    derived: bool
    verified: bool


@dataclass
class AssistantResult:
    question: str
    sql: str | None = None
    rows: pd.DataFrame | None = None
    chart: dict = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    answer: str = ""
    cited_numbers: list[CitedNumber] = field(default_factory=list)
    attempts: list[Attempt] = field(default_factory=list)
    declined_reason: str | None = None
    error: str | None = None
    usage: Usage = field(default_factory=Usage)
    latency_s: float = 0.0

    @property
    def ok(self) -> bool:
        return self.rows is not None and self.error is None

    @property
    def unverified_numbers(self) -> list[CitedNumber]:
        return [n for n in self.cited_numbers if not n.verified]


class Assistant:
    def __init__(self, llm: LLMClient | None = None, run_sql=db.query, log_path: Path | None = LOG_PATH):
        self.llm = llm or ChatClient()
        self.run_sql = run_sql
        self.log_path = log_path
        self.allowed = semantic.allowed_tables()
        self.plan_system = PLAN_SYSTEM.format(schema=semantic.render())

    def ask(self, question: str) -> AssistantResult:
        t0 = time.time()
        res = AssistantResult(question=question)
        try:
            self._plan_and_run(res)
            if res.ok:
                self._answer(res)
        except Exception as e:  # surface, don't crash the UI
            res.error = f"{type(e).__name__}: {e}"
        res.latency_s = round(time.time() - t0, 2)
        self._log(res)
        return res

    # -- steps ---------------------------------------------------------------

    def _plan_and_run(self, res: AssistantResult) -> None:
        messages: list[dict] = [{"role": "user", "content": res.question}]
        for _ in range(MAX_ATTEMPTS):
            reply = self.llm.complete_json(self.plan_system, messages)
            res.usage.add(reply.usage)
            plan = reply.data
            sql = plan.get("sql")
            if not sql:
                res.declined_reason = plan.get("cannot_answer_reason") or "The model could not map the question to the data."
                return
            attempt = Attempt(sql=sql)
            res.attempts.append(attempt)
            try:
                guarded = guard_sql(sql, self.allowed)
                rows = self.run_sql(guarded.sql)
            except (UnsafeSQLError, duckdb.Error) as e:
                attempt.error = str(e).splitlines()[0][:500]
                messages += [
                    {"role": "assistant", "content": json.dumps(plan, ensure_ascii=False)},
                    {"role": "user", "content": f"That query failed: {attempt.error}\nReturn a corrected JSON reply."},
                ]
                continue
            res.sql = guarded.sql
            res.rows = rows
            res.chart = plan.get("chart") or {}
            res.assumptions = plan.get("assumptions") or []
            return
        res.error = f"No valid query after {MAX_ATTEMPTS} attempts. Last error: {res.attempts[-1].error}"

    def _answer(self, res: AssistantResult) -> None:
        rows = res.rows
        shown = rows.head(ANSWER_ROWS).to_csv(index=False)
        note = f"\n(showing {ANSWER_ROWS} of {len(rows)} rows)" if len(rows) > ANSWER_ROWS else ""
        content = f"Question: {res.question}\n\nSQL:\n{res.sql}\n\nResult rows (CSV):\n{shown}{note}"
        reply = self.llm.complete_json(ANSWER_SYSTEM, [{"role": "user", "content": content}])
        res.usage.add(reply.usage)
        res.answer = reply.data.get("answer", "")
        cells = _numeric_cells(rows)
        for c in reply.data.get("cited_numbers") or []:
            try:
                value = float(c["value"])
            except (KeyError, TypeError, ValueError):
                continue
            derived = bool(c.get("derived"))
            res.cited_numbers.append(
                CitedNumber(
                    text=str(c.get("text", value)),
                    value=value,
                    derived=derived,
                    verified=_matches_any(value, cells) or (derived and _derivable(value, cells)),
                )
            )

    def _log(self, res: AssistantResult) -> None:
        if not self.log_path:
            return
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": getattr(self.llm, "model", "?"),
            "question": res.question,
            "sql": res.sql,
            "attempts": [asdict(a) for a in res.attempts],
            "rows": None if res.rows is None else len(res.rows),
            "declined_reason": res.declined_reason,
            "error": res.error,
            "unverified_numbers": [n.text for n in res.unverified_numbers],
            "prompt_tokens": res.usage.prompt_tokens,
            "completion_tokens": res.usage.completion_tokens,
            "latency_s": res.latency_s,
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# -- number verification -----------------------------------------------------

def _numeric_cells(df: pd.DataFrame) -> list[float]:
    values: list[float] = []
    for col in df.columns:
        s = df[col]
        if pd.api.types.is_bool_dtype(s):
            continue
        if pd.api.types.is_numeric_dtype(s):
            values += [float(v) for v in s.dropna().tolist()]
    return [v for v in values if math.isfinite(v)]


def _close(a: float, b: float) -> bool:
    # Tolerates rounding in prose ("£1.23M", "4.7%"): 1% relative, or small absolute for ~0 values.
    return math.isclose(a, b, rel_tol=0.01, abs_tol=0.005)


def _matches_any(value: float, cells: list[float]) -> bool:
    # Also accept percentages written as 4.7 for a cell holding 0.047, and vice versa.
    candidates = (value, value / 100, value * 100)
    return any(_close(v, c) for v in candidates for c in cells)


def _derivable(value: float, cells: list[float], limit: int = 200) -> bool:
    """True if value is a difference, ratio or percent change of two result cells."""
    cells = cells[:limit]
    for i, a in enumerate(cells):
        for j, b in enumerate(cells):
            if i == j:
                continue
            outcomes = [a - b, a + b]
            if b:
                outcomes += [a / b, a / b - 1]
            if any(_matches_any(value, [o]) for o in outcomes):
                return True
    return False
