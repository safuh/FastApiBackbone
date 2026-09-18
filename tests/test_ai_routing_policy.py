import pytest

from fastapi_backbone.ai import AIModelRouter, AIProviderRegistry
from fastapi_backbone.ai.errors import AIConfigurationError
from fastapi_backbone.ai.routing_policy import AIModelRoutePolicy


def router() -> AIModelRouter:
    return AIModelRouter(AIProviderRegistry())


def test_resolves_logical_route_to_provider_model() -> None:
    policy = AIModelRoutePolicy({"default": "OPENAI:gpt-test"})

    model = policy.resolve(" DEFAULT ", router())

    assert model.provider == "openai"
    assert model.model == "gpt-test"


def test_rejects_unknown_route() -> None:
    policy = AIModelRoutePolicy({"default": "openai:gpt-test"})

    with pytest.raises(AIConfigurationError, match="not configured"):
        policy.resolve("missing", router())


def test_rejects_empty_policy() -> None:
    with pytest.raises(AIConfigurationError, match="at least one route"):
        AIModelRoutePolicy({})


def test_rejects_empty_route_name() -> None:
    with pytest.raises(AIConfigurationError, match="route name"):
        AIModelRoutePolicy({" ": "openai:gpt-test"})
