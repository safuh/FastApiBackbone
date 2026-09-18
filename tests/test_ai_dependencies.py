from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_backbone.ai.dependencies import AIRequestContext, AIServiceDependencies


class FakeProvider:
    async def generate(self, request):  # type: ignore[no-untyped-def]
        raise NotImplementedError


class FakeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


def test_request_context_preserves_explicit_dependencies() -> None:
    session = SimpleNamespace()
    provider = FakeProvider()

    def repository_factory(repository_type, bound_session):  # type: ignore[no-untyped-def]
        return repository_type(bound_session)

    context = AIServiceDependencies(
        provider=provider,
        repository_factory=repository_factory,
    ).for_request(
        request_id="req-123",
        session=session,  # type: ignore[arg-type]
        subject="user-123",
        metadata={"source": "test"},
    )

    assert isinstance(context, AIRequestContext)
    assert context.request_id == "req-123"
    assert context.session is session
    assert context.provider is provider
    assert context.subject == "user-123"
    assert context.metadata == {"source": "test"}
    assert context.repository(FakeRepository).session is session


def test_request_context_rejects_repository_resolution_without_factory() -> None:
    context = AIRequestContext(
        request_id="req-123",
        session=SimpleNamespace(),  # type: ignore[arg-type]
        provider=FakeProvider(),
    )

    with pytest.raises(RuntimeError, match="repository factory is not configured"):
        context.repository(FakeRepository)


def test_request_metadata_is_copied() -> None:
    metadata = {"source": "test"}
    context = AIServiceDependencies(provider=FakeProvider()).for_request(
        request_id="req-123",
        session=SimpleNamespace(),  # type: ignore[arg-type]
        metadata=metadata,
    )

    metadata["source"] = "changed"
    assert context.metadata == {"source": "test"}
