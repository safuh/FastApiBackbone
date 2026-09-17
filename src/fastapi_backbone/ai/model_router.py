"""Provider-neutral model parsing and routing."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi_backbone.ai.contracts import AIModel
from fastapi_backbone.ai.errors import AIConfigurationError
from fastapi_backbone.ai.providers import AIProviderRegistry


@dataclass(frozen=True, slots=True)
class ModelRoute:
    """Resolved provider/model pair."""

    model: AIModel


class AIModelRouter:
    """Resolve configured model identifiers and obtain provider adapters."""

    def __init__(self, registry: AIProviderRegistry) -> None:
        self._registry = registry

    @staticmethod
    def parse_model_identifier(identifier: str) -> AIModel:
        value = identifier.strip()
        if not value:
            raise AIConfigurationError("AI model identifier cannot be empty")
        if ":" not in value:
            raise AIConfigurationError(
                "AI model identifier must use the 'provider:model' format"
            )
        provider, model = value.split(":", 1)
        provider = provider.strip().lower()
        model = model.strip()
        if not provider or not model:
            raise AIConfigurationError(
                "AI model identifier must contain both provider and model"
            )
        return AIModel(provider=provider, model=model)

    def resolve(self, identifier: str) -> tuple[AIModel, object]:
        model = self.parse_model_identifier(identifier)
        provider = self._registry.create(model.provider)
        return model, provider
