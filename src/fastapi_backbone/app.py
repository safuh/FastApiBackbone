"""Application factory and composition root."""

from typing import cast

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ExceptionHandler

from .api.router import api_router
from .core.config import Settings, get_settings
from .core.errors import (
    BackboneError,
    backbone_error_handler,
    http_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from .core.lifespan import lifespan
from .core.logging import configure_logging
from .core.middleware import RequestContextMiddleware


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

    app.add_middleware(RequestContextMiddleware)
    if resolved.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved.cors_origins,
            allow_credentials=resolved.cors_allow_credentials,
            allow_methods=resolved.cors_allow_methods,
            allow_headers=resolved.cors_allow_headers,
        )

    app.add_exception_handler(
        BackboneError,
        cast(ExceptionHandler, backbone_error_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_error_handler),
    )
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_error_handler),
    )
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(api_router, prefix=resolved.api_prefix)
    return app
