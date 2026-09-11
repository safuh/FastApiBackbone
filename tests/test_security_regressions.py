"""Security regression tests for authentication boundaries."""

from datetime import timedelta

import pytest

from fastapi_backbone.auth.tokens import TokenError, TokenService


SECRET = "test-secret-key-that-is-at-least-32-bytes"


def test_token_protects_security_claims_from_custom_claim_override() -> None:
    service = TokenService(SECRET)

    token = service.create(
        "user-123",
        timedelta(minutes=15),
        token_type="access",
        claims={
            "sub": "attacker",
            "iat": 0,
            "exp": 0,
            "type": "refresh",
        },
    )

    payload = service.decode(token, expected_type="access")

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert payload["iat"] != 0


def test_tampered_token_is_rejected() -> None:
    service = TokenService(SECRET)
    token = service.create("user-123", timedelta(minutes=15))
    tampered_token = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(TokenError, match="Invalid or expired token"):
        service.decode(tampered_token)


def test_refresh_token_cannot_be_accepted_as_access_token() -> None:
    service = TokenService(SECRET)
    token = service.create(
        "user-123",
        timedelta(days=7),
        token_type="refresh",
    )

    with pytest.raises(TokenError, match="Unexpected token type"):
        service.decode(token, expected_type="access")


def test_access_token_cannot_be_accepted_as_refresh_token() -> None:
    service = TokenService(SECRET)
    token = service.create("user-123", timedelta(minutes=15), token_type="access")

    with pytest.raises(TokenError, match="Unexpected token type"):
        service.decode(token, expected_type="refresh")


def test_short_jwt_secret_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least 32 characters"):
        TokenService("too-short")
