"""Application-facing AI contracts.

These protocols are deliberately smaller than any provider SDK. The AI layer
may be implemented by Pydantic AI today and another runtime later.
"""

from __future__ import annotations

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


class AIProvider(Protocol):
    """Port implemented by a concrete AI runtime/provider adapter."""

    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate a response without exposing provider details upstream."""
        ...
