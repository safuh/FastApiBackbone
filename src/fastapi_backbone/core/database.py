"""Async SQLAlchemy engine, session factory, and dependency."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import Settings


class Base(DeclarativeBase):
    """Base class for consuming application's ORM models."""


def create_engine(settings: Settings) -> AsyncEngine:
    """Create an async SQLAlchemy engine from application settings."""
    kwargs: dict[str, object] = {"echo": settings.database_echo}
    if settings.database_url.startswith("postgresql"):
        kwargs.update(
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
        )
    return create_async_engine(settings.database_url, **kwargs)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a request-scoped async session factory."""
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """Yield one database session and roll back on failed requests."""
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
