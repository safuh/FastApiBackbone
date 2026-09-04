"""Authentication primitives and extension points."""

from .passwords import PasswordHasher
from .service import (
    AuthenticationError,
    AuthenticationResult,
    AuthenticationService,
    CredentialStore,
    Credentials,
)
from .tokens import TokenError, TokenService

__all__ = [
    "AuthenticationError",
    "AuthenticationResult",
    "AuthenticationService",
    "CredentialStore",
    "Credentials",
    "PasswordHasher",
    "TokenError",
    "TokenService",
]
