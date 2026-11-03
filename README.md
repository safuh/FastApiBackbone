# FastAPI Backbone

> A reusable backend foundation for production-oriented FastAPI services.
>
> **FastAPI · Pydantic · SQLAlchemy 2.x · Alembic · PostgreSQL · Docker · Kubernetes**

[![CI](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml/badge.svg)](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml)

FastAPI Backbone provides the repeatable backend infrastructure that application teams otherwise rebuild for every service: configuration, HTTP boundaries, persistence, migrations, authentication primitives, operational health checks, containerization, and Kubernetes deployment manifests.

The project is intentionally backend-only. **Pydantic remains part of the application and validation architecture. PydanticAI and Flutter are not part of this MVP.** No AI runtime, agent framework, mobile client, or frontend is required to use the project.

## MVP architecture

| Layer | Technology | Responsibility |
|---|---|---|
| HTTP/API | FastAPI | Application factory, routers, middleware, OpenAPI |
| Validation/configuration | Pydantic v2, Pydantic Settings | Request/response schemas and typed environment configuration |
| Application/security | Python services, PyJWT, pwdlib | Optional identity and JWT authentication lifecycle |
| Persistence | SQLAlchemy 2.x async | Engine, sessions, repositories, transactions |
| Schema management | Alembic | Versioned, explicit database migrations |
| Production database | PostgreSQL + asyncpg | Persistent application data |
| Local/test database | SQLite + aiosqlite | Lightweight development and isolated tests |
| Container runtime | Docker | Reproducible non-root application image |
| Local orchestration | Docker Compose | API + PostgreSQL development stack |
| Cluster deployment | Kubernetes + Kustomize | Deployment, Service, probes, migration Job, optional HPA |

~~~text
HTTP client
    |
    v
FastAPI application
    |-- Pydantic request/response validation
    |-- middleware, error handling, correlation IDs
    |-- health and readiness endpoints
    |
    v
Application services
    |-- optional authentication use cases
    |-- repository / Unit of Work boundaries
    |
    v
SQLAlchemy async sessions
    |
    v
PostgreSQL
    ^
    |
Alembic migrations (explicit release operation)

Docker image -> Docker Compose (local)
             -> Kubernetes / Kustomize (deployment)
~~~

## Included in the MVP

- FastAPI application factory and explicit development/test/production profiles.
- Typed configuration using Pydantic Settings.
- Async SQLAlchemy engine, session factory, transaction scope, and Unit of Work.
- Alembic migration environment and versioned identity schema.
- PostgreSQL production support and SQLite development/test support.
- Liveness and database-backed readiness endpoints.
- Structured logging, request correlation IDs, and stable error responses.
- Optional password authentication with Argon2 hashing, signed JWTs, refresh-token rotation, and revocation.
- Multi-stage-compatible, non-root Docker runtime using the committed uv.lock.
- Docker Compose development stack and production deployment script.
- Kubernetes Kustomize base, production overlay, explicit migration Job, example Ingress, and optional HPA.
- Automated unit, integration, migration, Docker, and Kubernetes manifest checks in CI.

## Explicitly out of scope

- PydanticAI, agents, model providers, and AI orchestration.
- Flutter, Dart clients, and mobile application code.
- Frontend/UI implementation.
- Project generator/CLI and template distribution.
- Product-specific business domains, billing, or RBAC.

These can be considered independently in future projects or milestones. They are not dependencies of this backend foundation.

## Quick start

Requirements: Python 3.11+, uv, and Docker with the Compose plugin.

~~~bash
git clone https://github.com/safuh/FastApiBackbone.git
cd FastApiBackbone
uv sync --extra dev
cp .env.example .env

# Run static analysis and tests
make check

# Run the API directly (SQLite by default)
make run
~~~

API documentation is available at http://127.0.0.1:8000/docs.

## Local PostgreSQL with Docker Compose

~~~bash
make docker-up
~~~

Apply migrations against the Compose database:

~~~bash
docker compose -f docker/compose.yml exec api alembic upgrade head
~~~

Check the service:

~~~bash
curl -fsS http://127.0.0.1:8000/api/health/live
curl -fsS http://127.0.0.1:8000/api/health/ready
~~~

Stop the stack with make docker-down. The development Compose file uses disposable local credentials and must not be used as a production deployment configuration.

## Configuration

Configuration is environment-driven through Pydantic Settings. Supported profiles are development, test, and production.

| Variable | Purpose | Default |
|---|---|---|
| ENVIRONMENT | Configuration profile | development |
| DATABASE_URL | Async SQLAlchemy URL | Local SQLite |
| APP_NAME | OpenAPI/service name | FastAPI Backbone |
| APP_VERSION | Service version | 0.1.0 |
| DEBUG | FastAPI debug mode | false |
| LOG_LEVEL | Logging threshold | INFO |
| LOG_JSON | JSON log output | false |
| CORS_ORIGINS | Explicit browser origins | Empty |
| DATABASE_POOL_SIZE | PostgreSQL pool size | 5 |
| DATABASE_MAX_OVERFLOW | PostgreSQL overflow | 10 |

Production configuration rejects debug mode and requires a PostgreSQL asyncpg URL. Production logging is JSON. Never commit production credentials.

## Database and migrations

PostgreSQL is the production database. SQLite is supported for local development and isolated tests.

The application owns one async engine and session factory through FastAPI lifespan. Use session_scope or UnitOfWork to make transaction boundaries explicit. Repositories must use the supplied session rather than creating independent sessions or transactions.

Alembic is the only schema migration mechanism:

~~~bash
make migrate-up
make migrate-current
make migrate-history
make migrate-down
~~~

Review every autogenerated migration before committing. Never edit a migration that has already been applied to a shared environment.

**Production rule:** migrations are a release operation. Run them once before the application rollout; never run migrations automatically in every API process.

## Health contract

| Endpoint | Meaning |
|---|---|
| GET /api/health | Human-friendly process health |
| GET /api/health/live | Liveness; does not require the database |
| GET /api/health/ready | Readiness; requires completed startup and a reachable database |

Readiness returns HTTP 503 when startup is incomplete or the database is unavailable. Use liveness for process restart probes and readiness for traffic routing.

## Optional authentication

The reference package includes password registration/login, access and refresh JWTs, refresh rotation, revocation, and SQLAlchemy persistence. Authentication composition is deliberately explicit: consuming applications supply the JWT secret and token lifetimes when constructing the application.

The HTTP routes are mounted under /api/auth; if no authentication application factory is supplied, they return a controlled service-unavailable response rather than silently using an insecure default.

See Security & Deployment Guidance (docs/SECURITY.md) before enabling authentication in a production application.

## Docker

Build and run the local API/PostgreSQL stack:

~~~bash
make docker-up
make docker-down
~~~

Run the full Docker smoke test:

~~~bash
make docker-test
~~~

The smoke test builds the image, starts PostgreSQL and the API, verifies liveness/readiness, applies migrations, and cleans up its test stack.

For the reference production Compose workflow, provide an externally managed PostgreSQL URL:

~~~bash
export DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE'
make docker-prod
~~~

The production script builds the locked image, runs Alembic as a one-shot operation, starts the API, and waits for readiness. It does not provision a production database or manage secrets.

## Kubernetes

Kubernetes manifests live only under k8s/; this is the canonical deployment tree.

1. Create the fastapi-backbone Secret out of band.
2. Replace the production image placeholder with the published image.
3. Render and review the Kustomize overlays.
4. Run the migration Job.
5. Apply the application overlay and observe rollout health.

See docs/KUBERNETES.md for the complete commands, resource policy, optional Ingress/HPA, and rollback procedure.

## Quality gates

~~~bash
uv sync --extra dev
make lint
make typecheck
make test
make check
make docker-test
kubectl kustomize k8s/overlays/production
kubectl kustomize k8s/overlays/production/migration
kubectl kustomize k8s/overlays/production/hpa
~~~

CI runs Python 3.11, 3.12, and 3.13, PostgreSQL integration tests, package build checks, Docker smoke tests, and Kubernetes manifest rendering.

## Repository map

~~~text
src/fastapi_backbone/
  api/          HTTP routers and schemas
  auth/         Authentication use cases and security primitives
  core/         Configuration, database, lifecycle, errors, logging
  identity/     SQLAlchemy identity persistence and composition
alembic/        Versioned schema migrations
docker/         Dockerfile and Compose definitions
k8s/            Canonical Kustomize base and overlays
docs/           Architecture, operations, modules, and security
tests/          Unit, integration, migration, and security tests
~~~

## Project status

The MVP is scoped to the backend stack in this README. A feature is considered complete only when its automated checks and operational instructions have been verified. See docs/MILESTONES.md for implementation and verification status.

## Contributing

Read CONTRIBUTING.md before opening a pull request. Material architecture changes should include an Architecture Decision Record.

## Security

Do not disclose security vulnerabilities in public issues. Follow SECURITY.md.

## License

MIT. See LICENSE.
