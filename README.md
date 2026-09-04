# FastAPI Backbone

> **A production-grade foundation and project generator for FastAPI services.**
>
> FastAPI + SQLAlchemy 2.x + Alembic + JWT authentication + PostgreSQL + Flutter + Docker + Kubernetes.

[![CI](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml/badge.svg)](https://github.com/safuh/FastApiBackbone/actions/workflows/ci.yml)

FastAPI Backbone is an open-source, domain-neutral foundation for teams that want to start a serious Python API without rebuilding the same infrastructure every time.

## M1 Core Foundation

M1 establishes the canonical runtime and development contract. The reference application has:

- an explicit application factory;
- development, test, and production configuration profiles;
- deterministic async SQLAlchemy engine/session lifecycle;
- an explicit transaction-scoped Unit of Work;
- Alembic as the only schema migration mechanism;
- stable liveness and dependency-backed readiness endpoints;
- structured logging and request correlation IDs;
- startup/shutdown tests;
- PostgreSQL integration tests;
- a Docker Compose smoke test; and
- one documented local workflow.

The authoritative acceptance tracker is [`docs/MILESTONES.md`](docs/MILESTONES.md).

## Canonical local workflow

Use **uv** for development. This avoids mixing virtual-environment managers and dependency resolvers.

```bash
# one-time setup
uv sync --extra dev

# fast feedback loop
uv run pytest
uv run ruff check .
uv run mypy src

# all local quality gates
make check
```

The reference application is run with the same factory in every environment:

```bash
# development
make run

# production-style process
make prod
```

The factory is `fastapi_backbone.app:create_app`; the `--factory` flag is intentional.

## Configuration profiles

Configuration is environment-driven through `pydantic-settings`. The supported profiles are `development`, `test`, and `production`.

```bash
# local development
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./backbone.db

# CI/integration tests
ENVIRONMENT=test
TEST_DATABASE_URL=postgresql+asyncpg://backbone:backbone@localhost:5432/backbone

# production requires PostgreSQL and forces JSON logging
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/app
```

Production configuration rejects debug mode and non-PostgreSQL database URLs. Never commit production secrets.

## Database and migrations

PostgreSQL is the production database. SQLite is supported for lightweight local development and unit tests.

The application owns one shared async engine and session factory. Application services can use `UnitOfWork` when they need an explicit transaction boundary; repositories should use the UoW's session and must not create independent transactions.

Schema changes are made only through Alembic revisions:

```bash
make migrate
# or
uv run alembic upgrade head
```

The repository includes an initial domain-neutral revision. It intentionally creates no product tables: consuming applications own their domain metadata and migrations.

**Production rule:** application processes do not run migrations on startup. Migrations are a release operation and should run once, before the new application version becomes ready.

## Health contract

```text
GET /api/health       -> process health
GET /api/health/live  -> liveness; no database dependency
GET /api/health/ready -> readiness; startup complete + database reachable
```

Liveness is suitable for a process restart probe. Readiness is suitable for traffic routing and returns `503` when the application is not ready.

## Docker smoke test

The canonical container check builds the image, starts PostgreSQL and the API, verifies liveness/readiness, and executes the Alembic migration:

```bash
make docker-test
```

To leave the stack running for manual inspection:

```bash
make docker-up
curl -fsS http://127.0.0.1:8000/api/health/live
curl -fsS http://127.0.0.1:8000/api/health/ready
make docker-down
```

## Updating your local checkout without conflicts

Keep `main` clean and never develop directly on it:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/my-change
```

Before starting new work:

```bash
git fetch origin
git rebase origin/main
```

During development, commit small logical changes. Before pushing, run `make check`.

If `main` advances while your branch is in progress:

```bash
git fetch origin
git rebase origin/main
make check
git push --force-with-lease origin feat/my-change
```

Use `--force-with-lease`, never plain `--force`, after rebasing a private feature branch. Do not rebase a shared branch unless everyone using it agrees.

## Safe migration workflow

Never edit an already-applied migration in place. Create a new revision:

```bash
uv run alembic revision -m "describe schema change"
# edit the generated revision
uv run alembic upgrade head
```

Before opening a PR, verify both directions against a disposable PostgreSQL database:

```bash
TEST_DATABASE_URL=postgresql+asyncpg://backbone:backbone@localhost:5432/backbone uv run pytest -m integration
```

## Project vision

FastAPI Backbone remains domain-neutral. Its long-term developer experience is:

```bash
uv tool install fastapi-backbone
fastapi-backbone new myapp --frontend flutter --deployment kubernetes
cd myapp
docker compose up
```

Flutter, the CLI generator, Kubernetes assets, and complete identity/RBAC remain later milestones rather than being presented as finished features.

## Architecture

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
```

## Current status

**Version: 0.1.0-alpha**

M1 is implemented on the `feat/m1-core-foundation` branch and must be considered complete only after the CI quality gates and Docker/PostgreSQL integration checks are green.

## Production-grade definition

For this project, **production-grade does not mean “it starts successfully.”** A milestone can only be called production-ready when it has documented public behavior, automated tests, deterministic dependency/build configuration, static analysis, safe defaults, operational health behavior, migration considerations, container validation where applicable, upgrade/release documentation, and a reproducible CI gate.

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Architecture changes should include an ADR or an update to the relevant documentation when they materially affect public behavior.

## Security

Please do not disclose security vulnerabilities in public issues. Follow [`SECURITY.md`](SECURITY.md).

## License

FastAPI Backbone is released under the MIT License. See [`LICENSE`](LICENSE).
