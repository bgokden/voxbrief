"""Pluggable local-LLM backends with structured (JSON-schema) output.

A backend implements ``complete(prompt, schema) -> dict``. Ship-with reference is
Ollama (local, no Python dependency). Swap in an enterprise LLM (under a BAA) by
implementing the same protocol — see the README "From demo to production".
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMBackend(Protocol):
    def complete(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]: ...


class OllamaBackend:
    """Local Ollama server with JSON-schema-constrained output (stdlib only)."""

    def __init__(
        self,
        model: str = "llama3.1",
        host: str = "http://localhost:11434",
        temperature: float = 0.2,
        timeout: float = 180.0,
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature
        self.timeout = timeout

    def complete(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": schema,
            "options": {"temperature": self.temperature},
        }
        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return json.loads(payload["response"])


class LlamaCppBackend:
    """GGUF models via llama-cpp-python (install ``voxbrief[llama-cpp]``)."""

    def __init__(self, model_path: str, temperature: float = 0.2, n_ctx: int = 8192,
                 max_tokens: int = 1024, **kwargs: Any) -> None:
        from llama_cpp import Llama  # lazy optional import

        self._llm = Llama(model_path=model_path, n_ctx=n_ctx, verbose=False, **kwargs)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        resp = self._llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object", "schema": schema},
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return json.loads(resp["choices"][0]["message"]["content"])


class FakeBackend:
    """Deterministic backend for offline tests — cycles canned responses."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        if not responses:
            raise ValueError("FakeBackend needs at least one response")
        self.responses = list(responses)
        self.calls = 0

    def complete(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        r = self.responses[self.calls % len(self.responses)]
        self.calls += 1
        return r
