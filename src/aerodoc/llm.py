"""Minimal chat client for any OpenAI-compatible API (Gemini, Mistral, Groq, Ollama...).

Changing provider = changing `llm.base_url` and `llm.models` in the YAML config.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from aerodoc.config import get_settings
from aerodoc.pipeline_config import LLMConfig

RETRYABLE = {429, 500, 502, 503, 504}  # rate limit or temporary server overload


@dataclass
class Completion:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float


def _client(cfg: LLMConfig) -> OpenAI:
    # In the cloud sandbox the key is injected by the network proxy, so any placeholder works.
    key = get_settings().gemini_api_key or "proxy-injected"
    return OpenAI(base_url=cfg.base_url, api_key=key, timeout=cfg.timeout_s, max_retries=0)


def chat(messages: list[dict], cfg: LLMConfig) -> Completion:
    """Try each model in order; on overload (429/5xx) switch to the next one immediately.

    Only when every model has failed do we wait (exponential backoff) and start a new round.
    """
    client = _client(cfg)
    errors = []
    for attempt in range(cfg.retries + 1):
        for model in cfg.models:
            start = time.perf_counter()
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                )
            except APIStatusError as exc:
                errors.append(f"{model}: HTTP {exc.status_code}")
                if exc.status_code not in RETRYABLE:
                    continue  # e.g. 404 model not available for this account
            except (APIConnectionError, APITimeoutError) as exc:
                errors.append(f"{model}: {type(exc).__name__}")
            else:
                usage = response.usage
                return Completion(
                    text=(response.choices[0].message.content or "").strip(),
                    model=model,
                    prompt_tokens=usage.prompt_tokens if usage else 0,
                    completion_tokens=usage.completion_tokens if usage else 0,
                    latency_ms=(time.perf_counter() - start) * 1000,
                )
        if attempt < cfg.retries:
            time.sleep(2 * 2**attempt)
    raise RuntimeError("No LLM available: " + "; ".join(errors))
