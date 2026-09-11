"""Application facade for the complete password authentication lifecycle."""

from dataclasses import dataclass

from .login import LoginRequest, LoginService
from .refresh import RefreshResult, RefreshTokenService
from .registration import RegistrationRequest, RegistrationResponse, RegistrationService


@dataclass(frozen=True, slots=True)
class AuthenticationApplication:
    """Compose registration, login, refresh, and logout use cases."""

    registration_service: RegistrationService
    login_service: LoginService
    refresh_token_service: RefreshTokenService

    async def register(self, request: RegistrationRequest) -> RegistrationResponse:
        """Register a new password-authenticated identity."""
        return await self.registration_service.register(request)

    async def login(self, request: LoginRequest) -> RefreshResult:
        """Authenticate credentials and issue an access/refresh-token pair."""
        login = await self.login_service.login(request)
        return await self.refresh_token_service.issue(login.subject)

    async def refresh(self, refresh_token: str) -> RefreshResult:
        """Rotate a refresh token and issue its replacement pair."""
        return await self.refresh_token_service.rotate(refresh_token)

    async def logout(self, refresh_token: str) -> bool:
        """Revoke the supplied refresh token."""
        return await self.refresh_token_service.revoke(refresh_token)
