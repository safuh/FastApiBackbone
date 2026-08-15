from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import dispose_database
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure shared infrastructure at startup and release it at shutdown."""
    configure_logging()
    yield
    await dispose_database()
