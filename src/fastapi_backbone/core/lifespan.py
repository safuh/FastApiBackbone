"""Application lifespan and resource lifecycle."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from .config import Settings
from .database import create_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create shared infrastructure at startup and dispose it at shutdown."""
    settings: Settings = app.state.settings
    engine = create_engine(settings)
    app.state.db_engine = engine
    app.state.db_session_factory = create_session_factory(engine)
    try:
        yield
    finally:
        await engine.dispose()
