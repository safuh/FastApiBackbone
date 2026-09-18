"""Application-level policy for logical AI model routing.

The policy resolves stable application route names to explicit provider:model
identifiers. Selection is deterministic; provider SDKs remain behind adapters.
"""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import AIModel
from .errors import AIConfigurationError
from .model_router import AIModelRouter


@dataclass(frozen=True, slots=True)
class AIModelRoutePolicy:
    """Deterministic mapping from logical route names to model identifiers."""

    routes: dict[str, str]

    def __post_init__(self) -> None:
        normalized: dict[str, str] = {}
        for name, identifier in self.routes.items():
            route = name.strip().lower()
            if not route:
                raise AIConfigurationError("AI route name cannot be empty")
            normalized[route] = identifier
        if not normalized:
            raise AIConfigurationError("AI route policy must define at least one route")
        object.__setattr__(self, "routes", normalized)

    def resolve(self, route: str, router: AIModelRouter) -> AIModel:
        """Resolve a logical route through the canonical model parser."""
        name = route.strip().lower()
        if not name:
            raise AIConfigurationError("AI route name cannot be empty")
        try:
            identifier = self.routes[name]
        except KeyError as exc:
            raise AIConfigurationError(f"AI route '{name}' is not configured") from exc
        return router.parse_model_identifier(identifier)
