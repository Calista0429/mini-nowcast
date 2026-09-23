"""Run the Text-to-SQL eval set against the live LLM and print a scorecard.

    uv run python -m assistant.eval            # all cases
    uv run python -m assistant.eval -k index   # cases whose id contains "index"
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import yaml

from . import db
from .agent import Assistant, _matches_any, _numeric_cells

EVAL_PATH = Path(__file__).with_name("eval_set.yml")
REPORT_PATH = Path(__file__).resolve().parents[1] / "data" / "eval_report.json"


def result_matches(gold: pd.DataFrame, pred: pd.DataFrame | None) -> bool:
    """Every numeric value in the gold result must appear somewhere in the prediction.

    Percent vs fraction (5.06 vs 0.0506) counts as a match: both are correct answers.
    """
    if pred is None:
        return False
    pred_cells = _numeric_cells(pred)
    return all(_matches_any(g, pred_cells) for g in _numeric_cells(gold))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", default="", help="only run cases whose id contains this")
    args = ap.parse_args()

    cases = [c for c in yaml.safe_load(EVAL_PATH.read_text())["cases"] if args.k in c["id"]]
    assistant = Assistant()
    rows, t0 = [], time.time()
    for case in cases:
        res = assistant.ask(case["question"])
        if case.get("expect") == "decline":
            passed = res.declined_reason is not None
        else:
            passed = result_matches(db.query(case["gold"]), res.rows)
        rows.append({
            "id": case["id"],
            "passed": passed,
            "attempts": len(res.attempts),
            "self_corrected": len(res.attempts) > 1 and res.ok,
            "unverified_numbers": len(res.unverified_numbers),
            "tokens": res.usage.prompt_tokens + res.usage.completion_tokens,
            "latency_s": res.latency_s,
            "sql": res.sql,
            "error": res.error or res.declined_reason,
        })
        print(f"{'PASS' if passed else 'FAIL'}  {case['id']:<28} {res.latency_s:>5.1f}s  {rows[-1]['error'] or ''}")

    df = pd.DataFrame(rows)
    summary = {
        "model": assistant.llm.model,
        "cases": len(df),
        "accuracy": round(df["passed"].mean(), 3),
        "self_corrected": int(df["self_corrected"].sum()),
        "answers_with_unverified_numbers": int((df["unverified_numbers"] > 0).sum()),
        "avg_latency_s": round(df["latency_s"].mean(), 2),
        "total_tokens": int(df["tokens"].sum()),
        "wall_time_s": round(time.time() - t0, 1),
    }
    print("\n" + json.dumps(summary, indent=2, ensure_ascii=False))
    if args.k:  # partial runs are for debugging; only a full run updates the published score
        return
    REPORT_PATH.write_text(json.dumps({"summary": summary, "cases": rows}, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
