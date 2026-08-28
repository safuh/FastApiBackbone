# FastAPI Backbone

> **A production-grade foundation and project generator for FastAPI services.**
>
> FastAPI + SQLAlchemy 2.x + Alembic + JWT authentication + PostgreSQL + Flutter + Docker + Kubernetes.

[![CI](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml/badge.svg)](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml)

FastAPI Backbone is an open-source, domain-neutral foundation for teams that want to start a serious Python API without rebuilding the same infrastructure every time.

The project is deliberately **not a business application** and not a monolithic framework. It provides reusable infrastructure, secure authentication primitives, conventions, deployment assets, documentation, and—over the roadmap—a project generator that creates an application developers own and can extend normally.

## Vision

```text
                         FastAPI Backbone
                                |
             +------------------+------------------+
             |                  |                  |
          Backend            Client          Deployment
             |                  |                  |
          FastAPI            Flutter          Docker
          Pydantic             |            Kubernetes
             |             OpenAPI               |
       Application             |              CI/CD
          layer                |
             |                 |
      SQLAlchemy 2.x <---------+
             |
          Alembic
             |
        PostgreSQL
```

The long-term developer experience is:

```bash
uv tool install fastapi-backbone
fastapi-backbone new myapp --frontend flutter --deployment kubernetes
cd myapp
docker compose up
```

The generated project should be a complete, testable application—not a code dump that users are forced to understand before they can run it.

## Goals

### Core goals

- Async-first FastAPI application composition.
- SQLAlchemy 2.x as the ORM and PostgreSQL as the production database.
- Alembic as the migration system.
- Pydantic v2 and `pydantic-settings` for typed configuration.
- Secure JWT/OAuth2 authentication primitives, with refresh-token rotation and revocation on the roadmap.
- Clear separation of API, application/service, domain, repository, and infrastructure concerns.
- Flutter as an optional first-class client generated from the backend's OpenAPI contract.
- Docker for reproducible local and production builds.
- Kubernetes manifests suitable for production hardening.
- Automated testing of both the foundation and generated projects.
- Security, type checking, linting, packaging, documentation, and release automation from the beginning.
- Domain neutrality: consuming applications own their business models and bounded contexts.

### Non-goals

FastAPI Backbone will not become a kitchen-sink platform. Redis, Celery, Kafka, cloud-specific services, GraphQL, service meshes, and other integrations should remain optional extensions unless a strong ecosystem need justifies inclusion.

## Architecture

The reference architecture is:

```text
Client(s)
  |
  v
FastAPI HTTP boundary
  |
  +--> API routers / dependencies
  |       |
  |       v
  |   Application services
  |       |
  |       +--> Domain contracts / policies
  |       |
  |       +--> Repository interfaces
  |                 |
  |                 v
  |          Infrastructure adapters
  |                 |
  |              SQLAlchemy
  |                 |
  |             PostgreSQL
  |
  +--> Cross-cutting infrastructure
          |
          +--> Configuration
          +--> Logging / correlation context
          +--> Error handling
          +--> Security
          +--> Health / readiness
          +--> Observability

OpenAPI ----------------------> Flutter API client

Application artifact ----------> Docker ----------> Kubernetes
                                      |
                                      +--> migration Job
```

### Dependency direction

Business/application code should depend on abstractions, not on transport or infrastructure details:

```text
API -> application -> domain/contracts <- infrastructure
```

FastAPI and SQLAlchemy are implementation details at the boundaries. This keeps generated applications testable and makes it possible to replace an adapter without rewriting business logic.

## Repository layout

```text
FastApiBackbone/
├── src/
│   └── fastapi_backbone/
│       ├── api/                 # HTTP boundary and system endpoints
│       ├── auth/                # JWT primitives and auth extension points
│       ├── core/                # settings, DB lifecycle, logging, lifespan
│       └── app.py               # composition root / application factory
│
├── tests/                       # foundation-level unit and smoke tests
├── alembic/                     # migration environment
├── templates/                   # generated project assets (roadmap)
│   ├── backend/
│   ├── flutter/
│   └── kubernetes/
│
├── docker/                      # container and Compose assets
├── kubernetes/                  # production deployment base/overlays
├── docs/
│   ├── architecture/            # architectural decisions and boundaries
│   ├── modules/                  # module-specific documentation
│   ├── security/                 # threat model and security practices
│   └── MILESTONES.md             # living implementation tracker
│
├── .github/
│   ├── workflows/               # CI, security, release automation
│   └── ...
├── .env.example
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── pyproject.toml
└── README.md
```

## Current status

**Version: 0.1.0-alpha**

The repository is being rebuilt around the production architecture described above. The current release establishes the package layout, application factory, async SQLAlchemy infrastructure, Alembic integration, structured logging, operational health endpoints, JWT token primitives, test foundation, and project governance. Flutter, the CLI generator, Docker, Kubernetes, full identity/RBAC, and generated-project contract tests are staged milestones rather than falsely presented as complete features.

See **[`docs/MILESTONES.md`](docs/MILESTONES.md)** for the authoritative tracker. Every milestone records what is complete, what remains, acceptance criteria, and the next gate.

## Quick start

### Install from source

```bash
git clone https://github.com/safuh/FastApiBackbone.git
cd FastApiBackbone
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

### Run the reference application

```bash
uvicorn fastapi_backbone.app:create_app --factory --reload
```

The default application exposes:

```text
GET /api/health
GET /api/health/live
GET /api/health/ready
```

Interactive API documentation is available from FastAPI's normal `/docs` endpoint while running in development.

### Run tests and quality checks

```bash
pytest
ruff check .
mypy src
python -m build
twine check dist/*
```

## Database and migrations

PostgreSQL is the production target. SQLite with `aiosqlite` is supported for lightweight local development and tests.

```bash
alembic upgrade head
```

The backbone does not ship product-specific database tables. Consuming applications own their models and migration revisions.

A production deployment must treat migrations as an explicit release operation. Kubernetes deployments will use a migration Job rather than running `alembic upgrade head` in every application process.

See [`docs/modules/database/README.md`](docs/modules/database/README.md).

## Authentication

The current authentication module provides a small, testable JWT token service with:

- signed tokens;
- expiration validation;
- token type validation;
- required subject validation; and
- a minimum secret length guard.

The complete identity layer is intentionally staged separately. Before a production identity release, the project must add password hashing, OAuth2 flows, refresh-token rotation/revocation, secure cookie/mobile storage guidance, user persistence, RBAC/scopes, rate limiting, audit events, and comprehensive security tests.

See [`docs/modules/auth/README.md`](docs/modules/auth/README.md) and [`SECURITY.md`](SECURITY.md).

## Flutter strategy

Flutter is a **first-class optional client**, not a backend dependency. The backend remains standards-based and useful to any client.

```text
FastAPI
   |
 OpenAPI
   |
   +----> Flutter generated API client
   +----> Web client
   +----> CLI / integrations
```

The roadmap will provide a small Flutter shell with authentication state, secure token storage abstraction, API client, environment configuration, and generated models. The generated client should be derived from OpenAPI rather than duplicating backend schemas manually.

See [`docs/modules/flutter/README.md`](docs/modules/flutter/README.md).

## Docker and Kubernetes strategy

Docker provides reproducible application artifacts. Kubernetes is an optional production deployment target.

The intended deployment flow is:

```text
CI
 |
 +--> test
 +--> build wheel
 +--> build Docker image
 |
 v
registry
 |
 v
Kubernetes
 |
 +--> migration Job
 +--> Deployment
 +--> Service
 +--> Ingress
 +--> readiness/liveness probes
 +--> HPA (optional)
```

The Kubernetes layer will use a small base plus environment overlays and will avoid embedding real secrets in source control.

## Production-grade definition

For this project, **production-grade does not mean “it starts successfully.”** A milestone can only be called production-ready when it has:

1. documented public behavior;
2. automated tests at the appropriate unit/integration level;
3. deterministic dependency and build configuration;
4. static analysis and type checking;
5. security validation and safe defaults;
6. operational health/readiness behavior;
7. migration and rollback considerations;
8. container/deployment validation where applicable;
9. upgrade/release documentation; and
10. a reproducible CI gate.

No feature is marked complete merely because its source file exists.

## Open-source roadmap

```text
Phase 0  Architecture & governance       [DONE]
Phase 1  Core package foundation         [IN PROGRESS]
Phase 2  Database & migrations            [IN PROGRESS]
Phase 3  Identity & JWT                   [PLANNED]
Phase 4  Project generator / CLI          [PLANNED]
Phase 5  Flutter client                   [PLANNED]
Phase 6  Docker & local development       [PLANNED]
Phase 7  Kubernetes production assets     [PLANNED]
Phase 8  Observability & security         [PLANNED]
Phase 9  Release candidate                [PLANNED]
Phase 10 Public v1.0                     [PLANNED]
```

The exact checklist and acceptance criteria live in [`docs/MILESTONES.md`](docs/MILESTONES.md).

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Architecture changes should include an ADR or an update to the relevant documentation when they materially affect public behavior or dependency boundaries.

## Security

Please do not disclose security vulnerabilities in public issues. Follow [`SECURITY.md`](SECURITY.md).

## License

FastAPI Backbone is released under the MIT License. See [`LICENSE`](LICENSE).
