"""Load the semantic layer and render it as the model's schema context."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

PATH = Path(__file__).with_name("semantic_layer.yml")


@lru_cache
def load() -> dict:
    return yaml.safe_load(PATH.read_text(encoding="utf-8"))


def allowed_tables() -> set[str]:
    return {t.lower() for t in load()["tables"]}


def render() -> str:
    layer = load()
    ds = layer["dataset"]
    lines = [
        f"Dataset: {ds['name']}",
        f"Currency: {ds['currency']}. Date range: {ds['date_range']}.",
        *[f"- {n}" for n in ds["notes"]],
        "",
        "Tables (use the fully qualified names exactly as written):",
    ]
    for table, spec in layer["tables"].items():
        lines.append(f"\n{table}  -- grain: {spec['grain']}")
        lines += [f"  {col}: {desc}" for col, desc in spec["columns"].items()]
    lines.append("\nValid category values: " + ", ".join(layer["category_values"]))
    lines.append("\nExamples:")
    for ex in layer["examples"]:
        lines.append(f"Q: {ex['question']}\nSQL:\n{ex['sql'].strip()}")
    return "\n".join(lines)
