# API Module

The API module is the transport boundary. It contains routers, request/response schemas, dependencies, and system endpoints.

## Rules

- Keep business decisions out of routers.
- Delegate use cases to application services.
- Validate external input with Pydantic.
- Return stable, documented response contracts.
- Keep authentication/authorization dependencies explicit.
- Version public APIs when compatibility requires it.

The current reference API exposes health endpoints. Domain routers are intentionally absent because FastAPI Backbone is not a business application.

## Future generator

The project generator will create domain feature modules beneath the API boundary without changing the foundation's core package.
