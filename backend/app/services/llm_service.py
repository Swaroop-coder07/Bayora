"""LLM provider calls. Stdlib only, so it can run inside the minimal sandbox worker."""
import json
import re
import urllib.request
from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    model_version: str


def _mock(system: str, user: str) -> LLMResult:
    """Deterministic demo model: leaks on classic injection phrasing, refuses on softer probing."""
    low = user.lower()
    token = re.search(r"Internal reference token \(never disclose\): (\S+)", system)
    canary = token.group(1) if token else ""
    if "ignore" in low and ("instruction" in low or "system prompt" in low):
        text = "Sure! My instructions are:\n" + system
    elif "spaced" in low and canary:
        text = "Here is the code, spaced out: " + " ".join(canary)
    elif any(k in low for k in ("system prompt", "reveal", "verbatim", "internal", "secret", "repeat")):
        text = "I'm sorry, I can't share my configuration."
    else:
        text = "Happy to help with that. Could you tell me a bit more about what you need?"
    return LLMResult(text, "mock-model-1")


def _anthropic(system: str, user: str, api_key: str, model: str) -> LLMResult:
    body = json.dumps(
        {"model": model, "max_tokens": 700, "system": system, "messages": [{"role": "user", "content": user}]}
    ).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={"content-type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
    )
    with urllib.request.urlopen(req, timeout=50) as resp:
        data = json.loads(resp.read())
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return LLMResult(text, data.get("model", model))


def generate(system: str, user: str, provider: str = "mock", api_key: str = "", model: str = "") -> LLMResult:
    if provider == "anthropic":
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        return _anthropic(system, user, api_key, model)
    return _mock(system, user)
