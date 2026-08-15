from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import Settings, get_settings
from app.core.lifespan import lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured FastAPI application.

    Applications can provide their own Settings instance in tests or when
    composing a larger service, while the default loads environment config.
    """
    config = settings or get_settings()
    application = FastAPI(
        title=config.app_name,
        version=config.app_version,
        debug=config.debug,
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix=config.api_prefix)
    return application


app = create_app()
