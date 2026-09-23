"""Thin LLM client for any OpenAI-compatible chat API.

Configured through three environment variables (see .env.example):
    LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

That covers DeepSeek, OpenAI, Moonshot/Kimi, Qwen (DashScope), Zhipu, Groq, Together,
OpenRouter, a local Ollama or vLLM server, and anything else speaking the same protocol.
The only requirement is support for `response_format={"type": "json_object"}`; providers
without it can set LLM_JSON_MODE=off, which falls back to prompt-only JSON instructions.
"""
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


def _env(*names: str, default: str | None = None) -> str | None:
    """First of `names` that is set. Older DEEPSEEK_*/OPENAI_* names still work."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


class ChatClient:
    """Any OpenAI-compatible chat completions endpoint."""

    def __init__(self, model: str | None = None, base_url: str | None = None, api_key: str | None = None) -> None:
        from openai import OpenAI

        self.model = model or _env("LLM_MODEL", "DEEPSEEK_MODEL", "OPENAI_MODEL", default="deepseek-chat")
        key = api_key or _env("LLM_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "No API key found. Copy .env.example to .env and set LLM_API_KEY, "
                "LLM_BASE_URL and LLM_MODEL (any OpenAI-compatible provider)."
            )
        self.json_mode = _env("LLM_JSON_MODE", default="on").lower() not in ("off", "false", "0")
        self._client = OpenAI(
            api_key=key,
            base_url=base_url or _env("LLM_BASE_URL", "DEEPSEEK_BASE_URL", "OPENAI_BASE_URL",
                                      default="https://api.deepseek.com"),
            timeout=60,
            max_retries=2,
        )

    def complete_json(self, system: str, messages: list[dict]) -> JSONReply:
        if not self.json_mode:
            system += "\n\nReply with a single valid JSON object and nothing else."
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=0,
            max_tokens=2000,
            **({"response_format": {"type": "json_object"}} if self.json_mode else {}),
        )
        content = resp.choices[0].message.content or "{}"
        usage = Usage(resp.usage.prompt_tokens, resp.usage.completion_tokens) if resp.usage else Usage()
        return JSONReply(json.loads(_strip_code_fence(content)), usage)


def _strip_code_fence(text: str) -> str:
    """Some providers wrap JSON in ```json fences even when asked not to."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    return text.strip()


DeepSeekClient = ChatClient  # backwards-compatible alias
