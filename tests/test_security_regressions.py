"""Security regression tests for authentication boundaries."""

import base64
import json
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
    header, _, signature = token.split(".")
    tampered_payload = base64.urlsafe_b64encode(
        json.dumps(
            {"sub": "attacker", "iat": 0, "exp": 4102444800, "type": "access"},
            separators=(",", ":"),
        ).encode()
    ).rstrip(b"=").decode()

    with pytest.raises(TokenError, match="Invalid or expired token"):
        service.decode(f"{header}.{tampered_payload}.{signature}")


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
