from datetime import timedelta
from uuid import UUID

import pytest

from fastapi_backbone.auth import (
    RefreshTokenRecord,
    RefreshTokenService,
    TokenError,
    TokenService,
)


class InMemoryRefreshTokenStore:
    def __init__(self) -> None:
        self.records: dict[UUID, RefreshTokenRecord] = {}

    async def create(self, record: RefreshTokenRecord) -> None:
        self.records[record.token_id] = record

    async def consume(self, token_id: UUID) -> RefreshTokenRecord | None:
        record = self.records.get(token_id)
        if record is None or record.revoked:
            return None
        self.records[token_id] = RefreshTokenRecord(
            record.token_id,
            record.subject,
            record.expires_in,
            revoked=True,
        )
        return record


@pytest.fixture
def service() -> RefreshTokenService:
    return RefreshTokenService(
        TokenService("x" * 32),
        InMemoryRefreshTokenStore(),
        timedelta(minutes=15),
        timedelta(days=7),
    )


@pytest.mark.asyncio
async def test_refresh_token_rotates_once(service: RefreshTokenService) -> None:
    issued = await service.issue("user-123")
    rotated = await service.rotate(issued.refresh_token)

    assert rotated.subject == "user-123"
    assert rotated.access_token != issued.access_token
    assert rotated.refresh_token != issued.refresh_token

    with pytest.raises(TokenError, match="Invalid refresh token"):
        await service.rotate(issued.refresh_token)


@pytest.mark.asyncio
async def test_access_token_cannot_be_used_for_refresh(
    service: RefreshTokenService,
) -> None:
    issued = await service.issue("user-123")
    with pytest.raises(TokenError, match="Invalid refresh token"):
        await service.rotate(issued.access_token)


@pytest.mark.asyncio
async def test_refresh_subject_mismatch_is_rejected(
    service: RefreshTokenService,
) -> None:
    issued = await service.issue("user-123")
    token_id = next(iter(service.refresh_token_store.records))
    token = service.token_service.create(
        "attacker",
        timedelta(days=7),
        token_type="refresh",
        claims={"jti": str(token_id)},
    )

    with pytest.raises(TokenError, match="Invalid refresh token"):
        await service.rotate(token)
