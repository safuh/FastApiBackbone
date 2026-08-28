"""Application factory and composition root."""

from fastapi import FastAPI

from .api.router import api_router
from .core.config import Settings, get_settings
from .core.lifespan import lifespan
from .core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured FastAPI application.

    The factory is intentionally dependency-injectable so tests and consuming
    applications can provide their own Settings instance.
    """
    resolved = settings or get_settings()
    configure_logging(resolved)

    app = FastAPI(
        title=resolved.app_name,
        version=resolved.app_version,
        debug=resolved.debug,
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.include_router(api_router, prefix=resolved.api_prefix)
    return app
