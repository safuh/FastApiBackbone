# FastAPI Backbone

A production-oriented, reusable foundation for Python backend projects built with FastAPI.

FastAPI is an excellent HTTP/API framework, but a durable backend application also needs configuration management, database lifecycle management, structured logging, health checks, error handling, dependency boundaries, testing conventions, and a migration strategy. **FastApiBackbone** provides that foundation without coupling it to a particular business domain.

## Goals

- Async-first application design.
- FastAPI for the HTTP/API boundary.
- SQLAlchemy 2.x with async sessions.
- Alembic migrations from day one.
- Pydantic v2 / pydantic-settings for validation and configuration.
- PostgreSQL as the production database; SQLite remains convenient for local development.
- Structured logging with structlog.
- Explicit application lifespan and resource cleanup.
- Domain/service/repository separation.
- Dependency inversion so domain logic does not depend on HTTP or database implementation details.
- Configuration through environment variables rather than hard-coded deployment settings.
- Testable infrastructure with a small, understandable surface area.

## Architecture

```text
Client
  |
  v
FastAPI / HTTP boundary
  |
  +--> API routers
  |      |
  |      +--> application services
  |              |
  |              +--> repository interfaces / infrastructure
  |              |
  |              +--> external service interfaces
  |
  +--> cross-cutting infrastructure
         |
         +--> authentication / authorization
         +--> configuration
         +--> logging
         +--> database lifecycle
         +--> exception handling
         +--> observability

SQLAlchemy 2.x <--> PostgreSQL
        |
     Alembic
```

The backbone deliberately does **not** prescribe an application domain. A project can add `identity`, `billing`, `orders`, `ai`, `documents`, `analytics`, or other bounded contexts without changing the foundation.

## Suggested project structure

```text
app/
├── api/                 # HTTP routers and API composition
├── core/                # configuration, database, lifecycle, logging
├── domain/              # optional domain layer / shared contracts
├── services/            # application use cases
├── repositories/        # persistence abstractions
├── infrastructure/      # concrete integrations
└── main.py              # application composition root

alembic/
tests/
scripts/
docker/
.env
.env.example
pyproject.toml
```

For larger systems, prefer bounded-context packages such as `app.identity`, `app.billing`, or `app.ai`, each owning its models, schemas, repositories, services, and routers.

## Why this exists

The project is intended as a **stable backend foundation**, not as another application framework. It establishes the decisions that should remain boring and consistent across projects while leaving domain-specific decisions to the application.

The architecture was proven while building [PAssist](https://github.com/safuh/Passist), a provider-agnostic AI operating platform. PAssist extends the same foundation with identity, AI provider configuration, conversations, tools, knowledge/RAG, memory, and multi-tenant capabilities.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload
```

Health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

## Production direction

For production deployments, use PostgreSQL, a strong secret-management strategy, HTTPS at the edge, a real process supervisor/container runtime, centralized logs/metrics, connection-pool sizing appropriate to the deployment, and a migration step as part of release automation.

This repository is intentionally a foundation. Authentication, authorization, background jobs, caching, queues, tracing, and domain modules should be added according to the needs of the application rather than forced into every project.
