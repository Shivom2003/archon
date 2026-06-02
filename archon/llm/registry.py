"""
Model registry — maps model name strings to client instances.
Handles fallback logic when a primary model is unavailable.
"""

from __future__ import annotations

import os

from archon.llm.base import LLMClient

# Lazy imports to avoid import errors if anthropic isn't installed
_CLIENTS: dict[str, type[LLMClient]] = {}


def _load_clients() -> None:
    global _CLIENTS
    if _CLIENTS:
        return
    try:
        from archon.llm.claude import ClaudeClient

        _CLIENTS["claude"] = ClaudeClient  # type: ignore[assignment]
    except ImportError:
        pass


# Known model → provider mappings
MODEL_PROVIDER: dict[str, str] = {
    # Claude models
    "claude-opus-4-5": "claude",
    "claude-opus-4-7": "claude",
    "claude-sonnet-4-5": "claude",
    "claude-sonnet-4-7": "claude",
    "claude-haiku-4-5": "claude",
    # Shorthand aliases
    "opus": "claude",
    "sonnet": "claude",
    "haiku": "claude",
}


def get_client(model: str | None = None) -> LLMClient:
    """
    Return an LLMClient for the given model name.

    Falls back to ARCHON_FALLBACK_MODEL env var, then to claude-haiku-4-5.
    Raises ImportError with a helpful message if the provider SDK isn't installed.
    """
    _load_clients()

    resolved = model or os.getenv("ARCHON_MODEL", "claude-sonnet-4-5")
    provider = MODEL_PROVIDER.get(resolved)

    if provider is None:
        # Unknown model — try to infer provider from model name prefix
        if resolved.startswith("claude"):
            provider = "claude"
        else:
            raise ValueError(f"Unknown model '{resolved}'. Set ARCHON_MODEL to a supported model name.")

    client_class = _CLIENTS.get(provider)
    if client_class is None:
        raise ImportError(
            f"Provider '{provider}' requires additional dependencies. "
            "Install them with: pip install archon[{provider}]"
        )

    try:
        return client_class(model=resolved)  # type: ignore[call-arg]
    except Exception as exc:
        # Try fallback model
        fallback = os.getenv("ARCHON_FALLBACK_MODEL", "claude-haiku-4-5")
        if fallback != resolved:
            try:
                return client_class(model=fallback)  # type: ignore[call-arg]
            except Exception:
                pass
        raise exc
