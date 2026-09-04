from datetime import timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from fastapi_backbone.auth import (
    AuthenticationError,
    AuthenticationService,
    LoginRequest,
    LoginService,
    PasswordHasher,
    TokenError,
    TokenService,
)
from fastapi_backbone.core.config import Settings
from fastapi_backbone.core.database import create_engine, create_session_factory
from fastapi_backbone.identity import User, UserCredentialRepository


async def _session() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession], AsyncSession]:
    engine = create_engine(Settings.for_profile("test"))
    factory = create_session_factory(engine)
    async with engine.begin() as connection:
        await connection.run_sync(User.metadata.create_all)
    session = factory()
    return engine, factory, session


@pytest.mark.asyncio
async def test_login_authenticates_persisted_user_and_issues_access_token() -> None:
    engine, _, session = await _session()
    try:
        hasher = PasswordHasher()
        user = User(identifier="alice@example.com", password_hash=hasher.hash("secret"))
        session.add(user)
        await session.commit()

        authentication = AuthenticationService(
            UserCredentialRepository(session),
            hasher,
            TokenService("x" * 32),
            timedelta(minutes=15),
        )
        login = LoginService(authentication)

        result = await login.login(LoginRequest("alice@example.com", "secret"))

        assert result.subject == user.id
        assert result.access_token
        assert not result.password_needs_rehash
        payload = authentication.token_service.decode(
            result.access_token, expected_type="access"
        )
        assert payload["sub"] == user.id
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_login_keeps_unknown_and_wrong_password_failures_generic() -> None:
    engine, _, session = await _session()
    try:
        hasher = PasswordHasher()
        session.add(User(identifier="alice@example.com", password_hash=hasher.hash("secret")))
        await session.commit()
        login = LoginService(
            AuthenticationService(
                UserCredentialRepository(session),
                hasher,
                TokenService("x" * 32),
                timedelta(minutes=15),
            )
        )

        for request in (
            LoginRequest("missing@example.com", "secret"),
            LoginRequest("alice@example.com", "wrong"),
        ):
            with pytest.raises(AuthenticationError, match="Invalid credentials"):
                await login.login(request)
    finally:
        await session.close()
        await engine.dispose()


def test_token_service_rejects_expired_and_wrong_type_tokens() -> None:
    service = TokenService("x" * 32)

    expired = service.create("user-123", timedelta(microseconds=1), token_type="access")
    with pytest.raises(TokenError, match="Invalid or expired token"):
        service.decode(expired, expected_type="access")

    refresh = service.create("user-123", timedelta(minutes=5), token_type="refresh")
    with pytest.raises(TokenError, match="Unexpected token type"):
        service.decode(refresh, expected_type="access")


def test_token_service_rejects_missing_subject() -> None:
    service = TokenService("x" * 32)
    token = service.create("user-123", timedelta(minutes=5), token_type="access")
    payload = service.decode(token, expected_type="access")
    assert payload["sub"] == "user-123"
