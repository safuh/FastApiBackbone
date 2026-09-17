from dataclasses import dataclass

import pytest

from fastapi_backbone.ai.contracts import AIModel, AIRequest, AIResponse
from fastapi_backbone.ai.errors import (
    AIConfigurationError,
    AIProviderAlreadyRegisteredError,
    AIProviderNotFoundError,
)
from fastapi_backbone.ai.model_router import AIModelRouter
from fastapi_backbone.ai.providers import AIProviderRegistry
from fastapi_backbone.core.config import Environment, Settings


@dataclass
class FakeProvider:
    async def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(content=request.prompt, model=request.model)


def test_provider_registry_is_explicit_and_case_normalized() -> None:
    registry = AIProviderRegistry()
    registry.register(" OpenAI ", FakeProvider)

    provider = registry.create("openai")

    assert isinstance(provider, FakeProvider)
    assert registry.names() == ("openai",)


def test_provider_registry_rejects_duplicates_and_unknown_provider() -> None:
    registry = AIProviderRegistry()
    registry.register("ollama", FakeProvider)

    with pytest.raises(AIProviderAlreadyRegisteredError):
        registry.register("OLLAMA", FakeProvider)
    with pytest.raises(AIProviderNotFoundError):
        registry.create("gemini")


def test_model_identifier_is_provider_neutral() -> None:
    model = AIModelRouter.parse_model_identifier("ollama:qwen3:8b")

    assert model == AIModel(provider="ollama", model="qwen3:8b")


@pytest.mark.parametrize("identifier", ["", "qwen3", ":model", "provider:"])
def test_invalid_model_identifier_is_rejected(identifier: str) -> None:
    with pytest.raises(AIConfigurationError):
        AIModelRouter.parse_model_identifier(identifier)


def test_model_router_resolves_registered_provider() -> None:
    registry = AIProviderRegistry()
    registry.register("ollama", FakeProvider)
    router = AIModelRouter(registry)

    route = router.resolve("ollama:qwen3:8b")

    assert route.model.provider == "ollama"
    assert route.model.model == "qwen3:8b"
    assert isinstance(route.provider, FakeProvider)


def test_ai_settings_are_part_of_canonical_settings() -> None:
    settings = Settings(
        environment=Environment.TEST,
        ai_enabled=True,
        ai_model="ollama:qwen3:8b",
    )

    assert settings.ai_settings().enabled is True
    assert settings.ai_settings().model == "ollama:qwen3:8b"


def test_enabled_ai_requires_model() -> None:
    with pytest.raises(ValueError, match="AI_MODEL"):
        Settings(environment=Environment.TEST, ai_enabled=True)
