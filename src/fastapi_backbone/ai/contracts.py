"""Application-facing AI contracts.

These protocols are deliberately smaller than any provider SDK. The AI layer
may be implemented by Pydantic AI today and another runtime later.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AIModel:
    """A provider-neutral model selection."""

    provider: str
    model: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AIRequest:
    """Normalized request entering the AI application boundary."""

    prompt: str
    model: AIModel
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AIResponse:
    """Normalized response leaving the AI application boundary."""

    content: str
    model: AIModel
    input_tokens: int | None = None
    output_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AIStreamChunk:
    """One ordered, provider-neutral unit emitted during a streamed response."""

    content: str
    model: AIModel
    is_final: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(Protocol):
    """Port implemented by a concrete AI runtime/provider adapter."""

    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate a response without exposing provider details."""
        ...


class AIStreamingProvider(AIProvider, Protocol):
    """Optional streaming port for providers that support incremental output."""

    def stream(self, request: AIRequest) -> AsyncIterator[AIStreamChunk]:
        """Yield ordered chunks and exactly one final chunk."""
        ...
