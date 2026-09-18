import asyncio

import pytest

from fastapi_backbone.ai import AIModel, AIRequest, AIResponse
from fastapi_backbone.ai.errors import AIError
from fastapi_backbone.ai.resilience import (
    AICircuitBreaker,
    AICircuitOpenError,
    AIResilienceError,
    AIResiliencePolicy,
    ResilientAIProvider,
)


def request() -> AIRequest:
    model = AIModel(provider="example", model="example-model")
    return AIRequest(prompt="hello", model=model)


def response() -> AIResponse:
    return AIResponse(content="ok", model=request().model)


class SequenceProvider:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    async def generate(self, request):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


@pytest.mark.asyncio
async def test_retries_then_succeeds() -> None:
    provider = SequenceProvider([AIError("temporary"), response()])
    runtime = ResilientAIProvider(
        provider,
        policy=AIResiliencePolicy(max_retries=1),
    )

    assert await runtime.generate(request()) == response()
    assert provider.calls == 2


@pytest.mark.asyncio
async def test_timeout_is_retried_and_then_fails() -> None:
    class SlowProvider:
        calls = 0

        async def generate(self, request):
            self.calls += 1
            await asyncio.sleep(1)
            return response()

    provider = SlowProvider()
    runtime = ResilientAIProvider(
        provider,
        policy=AIResiliencePolicy(timeout_seconds=0.001, max_retries=1),
    )

    with pytest.raises(AIResilienceError):
        await runtime.generate(request())

    assert provider.calls == 2


@pytest.mark.asyncio
async def test_fallback_is_used_after_primary_failure() -> None:
    primary = SequenceProvider([AIError("down")])
    fallback = SequenceProvider([response()])
    runtime = ResilientAIProvider(
        primary,
        policy=AIResiliencePolicy(max_retries=0),
        fallbacks=(fallback,),
    )

    assert await runtime.generate(request()) == response()
    assert primary.calls == 1
    assert fallback.calls == 1


def test_circuit_opens_after_threshold() -> None:
    circuit = AICircuitBreaker(failure_threshold=2, recovery_seconds=60)

    circuit.record_failure()
    assert not circuit.is_open
    circuit.record_failure()
    assert circuit.is_open

    with pytest.raises(AICircuitOpenError):
        circuit.before_call()

    circuit.record_success()
    assert not circuit.is_open
