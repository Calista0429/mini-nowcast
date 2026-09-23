"""Thin LLM client. DeepSeek exposes an OpenAI-compatible API, so the OpenAI SDK is used."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    def add(self, other: "Usage") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens


@dataclass
class JSONReply:
    data: dict
    usage: Usage = field(default_factory=Usage)


class LLMClient(Protocol):
    model: str

    def complete_json(self, system: str, messages: list[dict]) -> JSONReply: ...


class DeepSeekClient:
    def __init__(self, model: str | None = None) -> None:
        from openai import OpenAI

        self.model = model or os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
        self._client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            timeout=60,
            max_retries=2,
        )

    def complete_json(self, system: str, messages: list[dict]) -> JSONReply:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=2000,
        )
        content = resp.choices[0].message.content or "{}"
        usage = Usage(resp.usage.prompt_tokens, resp.usage.completion_tokens) if resp.usage else Usage()
        return JSONReply(json.loads(content), usage)
