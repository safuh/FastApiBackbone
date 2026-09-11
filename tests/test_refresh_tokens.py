"""Tests for application-level refresh-token rotation."""

from datetime import timedelta
from uuid import UUID

import pytest

from fastapi_backbone.auth.refresh import RefreshTokenService
from fastapi_backbone.auth.tokens import TokenError, TokenService


class InMemoryRefreshTokenStore:
    """Minimal refresh-token store used by application-level tests."""

    def __init__(self) -> None:
        self.records: dict[UUID, object] = {}

    async def save(self, record: object) -> None:
        self.records[record.id] = record  # type: ignore[attr-defined]

    async def consume(self, token_id: UUID) -> object | None:
        record = self.records.get(token_id)
        if record is None or getattr(record, "consumed_at", None) is not None:
            return None
        return record

    async def mark_consumed(self, token_id: UUID) -> None:
        record = self.records[token_id]
        record.consumed_at = object()  # type: ignore[attr-defined]


@pytest.fixture
def service() -> RefreshTokenService:
    """Build a refresh-token service backed by an in-memory store."""
    store = InMemoryRefreshTokenStore()
    token_service = TokenService("test-secret-key-that-is-at-least-32-bytes")
    return RefreshTokenService(
        refresh_token_store=store,
        token_service=token_service,
        refresh_token_lifetime=timedelta(days=7),
        access_token_lifetime=timedelta(minutes=15),
    )


@pytest.mark.asyncio
async def test_access_token_cannot_be_used_for_refresh(
    service: RefreshTokenService,
) -> None:
    await service.issue("user-123")
    with pytest.raises(TokenError, match="Invalid refresh token"):
        await service.rotate(
            service.token_service.create(
                "user-123", timedelta(minutes=15), token_type="access"
            )
        )


@pytest.mark.asyncio
async def test_refresh_subject_mismatch_is_rejected(
    service: RefreshTokenService,
) -> None:
    await service.issue("user-123")
    token_id = next(iter(service.refresh_token_store.records))
    token = service.token_service.create(
        "attacker",
        timedelta(days=7),
        token_type="refresh",
        claims={"jti": str(token_id)},
    )

    with pytest.raises(TokenError, match="Invalid refresh token"):
        await service.rotate(token)
