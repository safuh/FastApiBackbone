from fastapi_backbone.ai import AIModel, AIRequest, AIResponse


def test_ai_contracts_are_provider_neutral() -> None:
    model = AIModel(provider="example", model="example-model")
    request = AIRequest(prompt="hello", model=model)
    response = AIResponse(content="world", model=model)

    assert request.model.provider == "example"
    assert response.content == "world"
