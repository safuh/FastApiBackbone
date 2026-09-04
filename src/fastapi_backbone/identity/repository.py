"""Persistence adapter for authentication credentials."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_backbone.auth import Credentials

from .models import User


class UserCredentialRepository:
    """Adapt persisted users to the authentication credential contract."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_identifier(self, identifier: str) -> Credentials | None:
        """Return authentication credentials for an identifier, if present."""
        result = await self.session.execute(
            select(User.id, User.password_hash).where(User.identifier == identifier)
        )
        row = result.one_or_none()
        if row is None:
            return None
        return Credentials(subject=row.id, password_hash=row.password_hash)
