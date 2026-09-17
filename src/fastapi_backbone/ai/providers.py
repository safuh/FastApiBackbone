"""Provider adapter registry for the optional AI layer.

The registry contains application-owned adapters. Provider SDKs are intentionally
not imported here; concrete adapters are registered by composition code.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from fastapi_backbone.ai.contracts import AIProvider
from fastapi_backbone.ai.errors import (
    AIProviderAlreadyRegisteredError,
    AIProviderNotFoundError,
)


class AIProviderFactory(Protocol):
    """Callable that creates a provider adapter from runtime configuration."""

    def __call__(self) -> AIProvider: ...


class AIProviderRegistry:
    """Explicit registry mapping stable provider names to adapter factories."""

    def __init__(self) -> None:
        self._factories: dict[str, AIProviderFactory] = {}

    def register(self, name: str, factory: AIProviderFactory) -> None:
        normalized = self._normalize_name(name)
        if normalized in self._factories:
            raise AIProviderAlreadyRegisteredError(
                f"AI provider '{normalized}' is already registered"
            )
        self._factories[normalized] = factory

    def unregister(self, name: str) -> None:
        self._factories.pop(self._normalize_name(name), None)

    def create(self, name: str) -> AIProvider:
        normalized = self._normalize_name(name)
        try:
            factory = self._factories[normalized]
        except KeyError as exc:
            raise AIProviderNotFoundError(
                f"AI provider '{normalized}' is not registered"
            ) from exc
        return factory()

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("AI provider name cannot be empty")
        return normalized


def register_provider(
    registry: AIProviderRegistry,
    name: str,
) -> Callable[[AIProviderFactory], AIProviderFactory]:
    """Decorator for explicit adapter registration in composition code."""

    def decorator(factory: AIProviderFactory) -> AIProviderFactory:
        registry.register(name, factory)
        return factory

    return decorator
