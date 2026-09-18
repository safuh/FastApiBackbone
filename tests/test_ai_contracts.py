from collections.abc import AsyncIterator

from fastapi_backbone.ai import (
    AIModel,
    AIProvider,
    AIRequest,
    AIResponse,
    AIStreamChunk,
    AIStreamingProvider,
)


def test_ai_contracts_are_provider_neutral() -> None:
    model = AIModel(provider="example", model="example-model")
    request = AIRequest(prompt="hello", model=model)
    response = AIResponse(content="world", model=model)

    assert request.model.provider == "example"
    assert response.content == "world"


async def test_streaming_provider_contract_preserves_order_and_final_marker() -> None:
    model = AIModel(provider="example", model="example-model")
    request = AIRequest(prompt="hello", model=model)

    class FakeStreamingProvider:
        async def generate(self, request: AIRequest) -> AIResponse:
            return AIResponse(content="hello world", model=request.model)

        async def _chunks(self) -> AsyncIterator[AIStreamChunk]:
            yield AIStreamChunk(content="hello ", model=model)
            yield AIStreamChunk(content="world", model=model)
            yield AIStreamChunk(content="", model=model, is_final=True)

        def stream(self, request: AIRequest) -> AsyncIterator[AIStreamChunk]:
            return self._chunks()

    provider: AIProvider = FakeStreamingProvider()
    streaming_provider: AIStreamingProvider = FakeStreamingProvider()

    response = await provider.generate(request)
    chunks = [chunk async for chunk in streaming_provider.stream(request)]

    assert response.content == "hello world"
    assert [chunk.content for chunk in chunks] == ["hello ", "world", ""]
    assert [chunk.is_final for chunk in chunks] == [False, False, True]
    assert all(chunk.model == model for chunk in chunks)
