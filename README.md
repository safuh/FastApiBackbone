# FastAPI Backbone

**FastAPI Backbone** is a reusable, production-oriented foundation for Python backend projects.

FastAPI solves the HTTP/API layer well, but a durable backend also needs configuration management, database lifecycle, migrations, structured logging, health checks, dependency boundaries, and a predictable application composition model. This project provides those foundations without coupling them to a business domain.

> **Status: v0.1.0 Beta** — the core foundation is packaged and usable; production hardening continues through the tracked milestones.

## What it provides

- Async-first FastAPI application composition
- Pydantic v2 / pydantic-settings configuration
- Async SQLAlchemy 2.x sessions and engine management
- PostgreSQL and SQLite support
- Alembic migration configuration with an async environment
- Structured logging with structlog
- Explicit application lifespan and database cleanup
- Liveness and readiness health endpoints
- Environment-driven configuration
- Reusable application factory
- Clear separation between infrastructure and product/domain code
- Development tooling configuration for pytest, Ruff, mypy, build, and Twine

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
  |              +--> external service interfaces
  |
  +--> cross-cutting infrastructure
         |
         +--> configuration
         +--> logging
         +--> database lifecycle
         +--> exception handling owned by the application
         +--> observability hooks

SQLAlchemy 2.x <--> PostgreSQL / SQLite
        |
     Alembic
```

The backbone intentionally remains **domain-neutral**. Consuming applications can add bounded contexts such as `identity`, `billing`, `orders`, `ai`, `documents`, or `analytics` without changing the foundation.

## Repository layout

```text
FastApiBackbone/
├── app/
│   ├── api/              # HTTP routers and system endpoints
│   ├── core/             # settings, database, lifespan, logging
│   └── main.py           # reusable application factory + default app
├── alembic/              # migration environment
├── docs/
│   └── MILESTONES.md     # completion and hardening tracker
├── .github/workflows/
│   └── release.yml       # build + Trusted Publishing to PyPI
├── .env.example
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Installation

### From source

```bash
git clone https://github.com/safuh/FastApiBackbone.git
cd FastApiBackbone
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### From PyPI

Once the `v0.1.0` release has been published:

```bash
pip install fastapi-backbone
```

The package metadata uses the distribution name `fastapi-backbone` and requires Python 3.11+.

### Package build

Build source and wheel distributions locally:

```bash
python -m build
twine check dist/*
```

## Publishing

Releases use **PyPI Trusted Publishing** through GitHub Actions. The workflow at `.github/workflows/release.yml` builds and validates the source distribution and wheel, then publishes them using GitHub's OIDC identity rather than a long-lived PyPI API token.

To enable the first release, configure a PyPI Trusted Publisher with:

| Setting | Value |
|---|---|
| Owner | `safuh` |
| Repository | `FastApiBackbone` |
| Workflow | `release.yml` |
| GitHub environment | `pypi` |

Then create/publish the `v0.1.0` Git tag. The workflow will build, validate, and publish the package automatically.

For security, the workflow's publishing job has only `id-token: write` permission. PyPI's Trusted Publishing mechanism issues a short-lived credential to the verified GitHub workflow instead of requiring a stored API token.

## Create an application

The default application is available as `app.main:app`.

```bash
uvicorn app.main:app --reload
```

For composition in another service, use the application factory:

```python
from app.main import create_app

app = create_app()
```

The factory accepts a `Settings` instance, which makes configuration substitution straightforward for tests and consuming applications.

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Core settings include:

```text
APP_NAME
APP_VERSION
ENVIRONMENT
DEBUG
API_PREFIX
DATABASE_URL
DATABASE_ECHO
DATABASE_POOL_SIZE
DATABASE_MAX_OVERFLOW
LOG_LEVEL
LOG_JSON
```

Production deployments should use PostgreSQL and inject secrets/configuration through the deployment environment or a dedicated secret manager rather than committing `.env` files.

## Database

The backbone exposes an async SQLAlchemy `Base`, an engine, an async session factory, and a FastAPI dependency for request-scoped sessions.

```python
from app.core.database import Base, get_db
```

PostgreSQL is the intended production database. SQLite with `aiosqlite` is supported for lightweight local development.

Run migrations through Alembic:

```bash
alembic upgrade head
```

Generate a migration after adding application models:

```bash
alembic revision --autogenerate -m "describe change"
```

The backbone does not ship product-specific tables. The consuming application owns its models and migration revisions.

## Health endpoints

With the default `/api` prefix:

```text
GET /api/health/live
GET /api/health/ready
GET /api/health
```

`/health/live` is a lightweight process-level liveness check. `/health/ready` exposes application identity and environment information suitable for basic readiness monitoring. Product-specific dependency checks should be added by the consuming application.

## Design principles

### Domain neutrality

The backbone provides infrastructure rather than business rules. Authentication, authorization, billing, AI providers, conversations, documents, and tool execution should be implemented by the consuming application's bounded contexts or optional modules.

### Dependency inversion

Application/domain code should depend on contracts rather than directly coupling business logic to FastAPI, SQLAlchemy, or external service implementations.

### Configuration over hard-coding

Deployment-specific behavior belongs in configuration. The settings layer supports local `.env` development while remaining compatible with environment-based production configuration.

### Async-first

The foundation uses asynchronous FastAPI and SQLAlchemy primitives so consuming applications can scale I/O-heavy workloads without replacing the infrastructure layer.

## Relationship to PAssist

FastAPI Backbone is the **reusable infrastructure foundation**. PAssist is a concrete AI application built on the same architectural ideas and extends them with identity, AI provider configuration, conversations, tools, knowledge/RAG, memory, and other domain capabilities.

This separation is intentional:

```text
FastAPI Backbone
       |
       | reusable infrastructure
       v
PAssist / other applications
       |
       +--> identity
       +--> AI
       +--> conversations
       +--> documents
       +--> tools
       +--> domain-specific capabilities
```

## Development status

The package is at **v0.1.0 Beta**. The core foundation is packaged and documented, while the hardening roadmap tracks additional concerns such as correlation IDs, centralized exception handling, optional authentication, generic repository contracts, integration-test infrastructure, CI, Docker examples, observability hooks, and security validation.

See [`docs/MILESTONES.md`](docs/MILESTONES.md) for the current tracker.

## License

MIT License. Copyright © 2026 Safu Harry.
