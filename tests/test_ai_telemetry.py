import pytest

from fastapi_backbone.ai import AIModel, AIRequest, AIResponse
from fastapi_backbone.ai.errors import AIConfigurationError
from fastapi_backbone.ai.telemetry import AIModelPricing, AIUsageTelemetry


def test_records_tokens_latency_and_estimated_cost() -> None:
    telemetry = AIUsageTelemetry(
        {"gpt-test": AIModelPricing(input_cost_per_token=0.001, output_cost_per_token=0.002)}
    )
    model = AIModel(provider="openai", model="gpt-test")
    usage = telemetry.observe(
        AIRequest(prompt="hello", model=model),
        AIResponse(content="world", model=model, input_tokens=10, output_tokens=5),
        latency_seconds=1.25,
    )
    assert usage.total_tokens == 15
    assert usage.latency_seconds == 1.25
    assert usage.estimated_cost == pytest.approx(0.02)
    assert telemetry.records() == (usage,)


def test_unknown_pricing_keeps_cost_unknown() -> None:
    model = AIModel(provider="openai", model="gpt-test")
    usage = AIUsageTelemetry().observe(
        AIRequest(prompt="hello", model=model),
        AIResponse(content="world", model=model, input_tokens=2, output_tokens=3),
        latency_seconds=0.5,
    )
    assert usage.estimated_cost is None


def test_rejects_invalid_pricing() -> None:
    with pytest.raises(AIConfigurationError, match="pricing"):
        AIModelPricing(input_cost_per_token=-1)


def test_rejects_negative_latency() -> None:
    model = AIModel(provider="openai", model="gpt-test")
    with pytest.raises(AIConfigurationError, match="latency"):
        AIUsageTelemetry().observe(
            AIRequest(prompt="hello", model=model),
            AIResponse(content="world", model=model),
            latency_seconds=-0.1,
        )


def test_rejects_negative_token_counts() -> None:
    model = AIModel(provider="openai", model="gpt-test")
    with pytest.raises(AIConfigurationError, match="token"):
        AIUsageTelemetry().observe(
            AIRequest(prompt="hello", model=model),
            AIResponse(content="world", model=model, input_tokens=-1),
            latency_seconds=0.1,
        )
