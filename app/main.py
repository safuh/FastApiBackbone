from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import settings
from app.core.lifespan import lifespan


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.api_prefix)
