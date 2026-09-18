"""Deterministic tool registration, authorization, and execution.

Tool selection is application policy: an AI runtime may request a named tool, but
the runtime executes it only when the application has explicitly registered and
allowed that tool.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from .errors import AIConfigurationError, AIError

ToolResultT = TypeVar("ToolResultT")
ToolHandler = Callable[[Mapping[str, Any]], ToolResultT | Awaitable[ToolResultT]]


class ToolAuthorizer(Protocol):
    """Application policy deciding whether a subject may execute a tool."""

    def __call__(self, subject: str | None, tool_name: str) -> bool:
        """Return whether the subject is authorized for the named tool."""
        ...


@dataclass(frozen=True, slots=True)
class AITool:
    """Explicitly registered application tool."""

    name: str
    handler: ToolHandler[Any]
    description: str = ""


class AIToolRegistry:
    """Deterministic allowlist of explicitly registered tools."""

    def __init__(self) -> None:
        self._tools: dict[str, AITool] = {}

    def register(self, tool: AITool) -> None:
        name = self._normalize_name(tool.name)
        if name in self._tools:
            raise AIConfigurationError(f"AI tool '{name}' is already registered")
        self._tools[name] = AITool(
            name=name,
            handler=tool.handler,
            description=tool.description,
        )

    def unregister(self, name: str) -> None:
        self._tools.pop(self._normalize_name(name), None)

    def get(self, name: str) -> AITool:
        normalized = self._normalize_name(name)
        try:
            return self._tools[normalized]
        except KeyError as exc:
            raise AIConfigurationError(
                f"AI tool '{normalized}' is not registered"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip().lower()
        if not normalized:
            raise AIConfigurationError("AI tool name cannot be empty")
        return normalized


class AIToolRuntime:
    """Execute only registered and explicitly authorized tools."""

    def __init__(
        self,
        registry: AIToolRegistry,
        *,
        allowlist: set[str] | frozenset[str],
        authorizer: ToolAuthorizer | None = None,
    ) -> None:
        normalized = frozenset(registry._normalize_name(name) for name in allowlist)
        unknown = sorted(normalized.difference(registry.names()))
        if unknown:
            raise AIConfigurationError(
                f"AI tool allowlist contains unregistered tools: {', '.join(unknown)}"
            )
        self._registry = registry
        self._allowlist = normalized
        self._authorizer = authorizer

    def allowed_tools(self) -> tuple[str, ...]:
        """Return the deterministic, sorted execution allowlist."""
        return tuple(sorted(self._allowlist))

    async def execute(
        self,
        name: str,
        arguments: Mapping[str, Any],
        *,
        subject: str | None = None,
    ) -> Any:
        """Execute an explicitly allowed tool after authorization checks."""
        normalized = name.strip().lower()
        if not normalized:
            raise AIConfigurationError("AI tool name cannot be empty")
        if normalized not in self._allowlist:
            raise AIError(f"AI tool '{normalized}' is not allowed")

        tool = self._registry.get(normalized)
        if self._authorizer is not None and not self._authorizer(subject, normalized):
            raise AIError(f"AI tool '{normalized}' is not authorized")

        result = tool.handler(dict(arguments))
        if inspect.isawaitable(result):
            return await result
        return result
