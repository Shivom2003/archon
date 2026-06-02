"""Abstract LLM client interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class Message(dict):
    """A conversation message — thin wrapper around dict for type clarity."""


class LLMClient(ABC):
    """
    Abstract interface for an LLM client.
    All concrete clients (Claude, etc.) implement this.
    """

    @abstractmethod
    async def generate(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
        cache_system: bool = False,
    ) -> dict[str, Any]:
        """
        Generate a response (non-streaming).

        Returns a dict with at minimum:
            - "content": list of content blocks
            - "stop_reason": str
            - "usage": dict with input_tokens, output_tokens, cache_read_tokens (optional)
        """
        ...

    @abstractmethod
    async def stream(
        self,
        *,
        system: str,
        messages: list[dict[str, Any]],
        max_tokens: int = 4096,
        cache_system: bool = False,
    ) -> AsyncIterator[str]:
        """
        Stream text tokens.
        Yields string chunks as they arrive.
        """
        ...

    @property
    @abstractmethod
    def model_id(self) -> str:
        """The model identifier string (e.g. 'claude-sonnet-4-5')."""
        ...
