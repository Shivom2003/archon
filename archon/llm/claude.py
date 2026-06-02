"""
Anthropic Claude client with prompt caching support.

Uses the official `anthropic` SDK. Prompt caching is applied to the
system prompt when `cache_system=True`, reducing costs significantly
on multi-turn interviews where the system prompt is large and static.
"""

import os
from collections.abc import AsyncIterator
from typing import Any

import anthropic

from archon.llm.base import LLMClient

# Prompt caching beta header
_CACHE_BETA = "prompt-caching-2024-07-31"

# Default models
DEFAULT_MODEL = "claude-sonnet-4-5"
FALLBACK_MODEL = "claude-haiku-4-5"


class ClaudeClient(LLMClient):
    """Async Anthropic Claude client with prompt caching."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._model = model or os.getenv("ARCHON_MODEL", DEFAULT_MODEL)
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise ValueError(
                "No Anthropic API key found. Set ANTHROPIC_API_KEY or pass api_key=."
            )
        self._client = anthropic.AsyncAnthropic(api_key=self._api_key)

    @property
    def model_id(self) -> str:
        return self._model

    def _build_system(self, system: str, cache: bool) -> list[dict[str, Any]] | str:
        """
        If caching is enabled, wrap the system prompt in a cache_control block.
        The Anthropic API accepts either a plain string or a list of content blocks
        for the system parameter.
        """
        if not cache:
            return system
        return [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    async def generate(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
        cache_system: bool = False,
    ) -> dict[str, Any]:
        """Non-streaming generation. Returns the full response dict."""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "system": self._build_system(system, cache_system),
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        betas = [_CACHE_BETA] if cache_system else []

        response = await self._client.beta.messages.create(
            **kwargs,
            betas=betas,
        ) if cache_system else await self._client.messages.create(**kwargs)

        # Normalise to a plain dict for easy testing / mocking
        return {
            "content": [_block_to_dict(b) for b in response.content],
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
                "cache_creation_tokens": getattr(
                    response.usage, "cache_creation_input_tokens", 0
                ),
            },
        }

    async def stream(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        max_tokens: int = 4096,
        cache_system: bool = False,
    ) -> AsyncIterator[str]:
        """Streaming generation — yields text chunks."""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "system": self._build_system(system, cache_system),
            "messages": messages,
        }
        betas = [_CACHE_BETA] if cache_system else []

        if cache_system:
            async with self._client.beta.messages.stream(**kwargs, betas=betas) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            async with self._client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text


def _block_to_dict(block: Any) -> dict[str, Any]:
    """Convert an Anthropic content block object to a plain dict."""
    if hasattr(block, "type"):
        match block.type:
            case "text":
                return {"type": "text", "text": block.text}
            case "tool_use":
                return {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
    # Fallback: try model_dump if available (Pydantic models)
    if hasattr(block, "model_dump"):
        return block.model_dump()
    return {"type": "unknown", "raw": str(block)}
