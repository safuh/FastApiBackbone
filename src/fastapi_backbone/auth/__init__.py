"""Authentication primitives and extension points."""

from .login import LoginRequest, LoginResponse, LoginService
from .passwords import PasswordHasher
from .service import (
    AuthenticationError,
    AuthenticationResult,
    AuthenticationService,
    Credentials,
    CredentialStore,
)
from .tokens import TokenError, TokenService

__all__ = [
    "AuthenticationError",
    "AuthenticationResult",
    "AuthenticationService",
    "CredentialStore",
    "Credentials",
    "LoginRequest",
    "LoginResponse",
    "LoginService",
    "PasswordHasher",
    "TokenError",
    "TokenService",
]
