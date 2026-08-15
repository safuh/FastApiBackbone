from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for application ORM models."""



def _create_engine() -> AsyncEngine:
    kwargs: dict[str, object] = {
        "echo": settings.database_echo or settings.debug,
        "pool_pre_ping": True,
    }

    if settings.database_url.startswith("postgresql"):
        kwargs.update(
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
        )

    return create_async_engine(settings.database_url, **kwargs)


engine = _create_engine()
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield one request-scoped asynchronous SQLAlchemy session."""
    async with AsyncSessionFactory() as session:
        yield session


async def dispose_database() -> None:
    """Dispose the engine and release all pooled connections."""
    await engine.dispose()
