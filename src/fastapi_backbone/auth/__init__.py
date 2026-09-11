"""Authentication primitives and extension points."""

from .application import AuthenticationApplication
from .login import LoginRequest, LoginResponse, LoginService
from .passwords import PasswordHasher
from .refresh import RefreshResult, RefreshTokenRecord, RefreshTokenService, RefreshTokenStore
from .registration import (
    IdentifierAlreadyExistsError,
    RegistrationError,
    RegistrationRequest,
    RegistrationResponse,
    RegistrationService,
    UserRegistrationStore,
)
from .service import (
    AuthenticationError,
    AuthenticationResult,
    AuthenticationService,
    Credentials,
    CredentialStore,
)
from .tokens import TokenError, TokenService

__all__ = [
    "AuthenticationApplication",
    "AuthenticationError",
    "AuthenticationResult",
    "AuthenticationService",
    "CredentialStore",
    "Credentials",
    "IdentifierAlreadyExistsError",
    "LoginRequest",
    "LoginResponse",
    "LoginService",
    "PasswordHasher",
    "RefreshResult",
    "RefreshTokenRecord",
    "RefreshTokenService",
    "RefreshTokenStore",
    "RegistrationError",
    "RegistrationRequest",
    "RegistrationResponse",
    "RegistrationService",
    "TokenError",
    "TokenService",
    "UserRegistrationStore",
]
