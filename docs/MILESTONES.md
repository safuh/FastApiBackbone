# MVP Acceptance Tracker

This tracker describes the supported FastAPI Backbone MVP. A checkbox means the criterion has been verified; implementation alone is not verification.

## Product scope

**Included:** FastAPI, Pydantic/Pydantic Settings, SQLAlchemy 2.x, Alembic, PostgreSQL, optional JWT identity, Docker, Docker Compose, Kubernetes/Kustomize.

**Excluded:** PydanticAI, AI agents/providers, Flutter/mobile clients, frontend, project generator/CLI, and product-specific business modules.

## M1 — Application foundation

**Implementation status: complete; final branch verification required after scope cleanup.**

- [x] Python src-layout package and application factory.
- [x] Development, test, and production configuration profiles.
- [x] Pydantic Settings validation and environment overrides.
- [x] FastAPI exception handling and stable error envelope.
- [x] Request correlation IDs in middleware and response headers.
- [x] Structured logging.
- [x] Explicit CORS configuration.
- [x] Liveness and database-backed readiness endpoints.
- [x] Deterministic application lifespan and engine disposal.

## M2 — Persistence and migrations

**Implementation status: complete; final branch verification required.**

- [x] Async SQLAlchemy 2.x engine and session factory.
- [x] PostgreSQL/asyncpg production driver.
- [x] SQLite/aiosqlite development and test driver.
- [x] Transaction-scoped session helper.
- [x] Explicit Unit of Work transaction boundary.
- [x] Async Alembic environment.
- [x] Versioned foundation and identity migrations.
- [x] Migration upgrade/downgrade integration tests.
- [x] PostgreSQL integration test in CI.
- [x] Explicit migration-before-rollout deployment contract.

## M3 — Optional identity and JWT

**Implementation status: implemented; consumers must explicitly configure it.**

- [x] Password hashing with Argon2.
- [x] Generic invalid-credential behavior.
- [x] Signed JWT access and refresh tokens.
- [x] Token expiration, subject, and token-type validation.
- [x] Refresh-token persistence, rotation, replay rejection, and revocation.
- [x] Registration, login, refresh, and logout HTTP endpoints.
- [x] Structured authentication audit events.
- [x] SQLAlchemy identity repositories and composition helper.
- [x] Security regression and integration tests.
- [ ] RBAC/OAuth2 scopes — intentionally excluded from MVP.
- [ ] Built-in rate limiting — intentionally excluded; apply at the edge or in the consuming application.

Authentication remains optional at the composition root. Production applications must provide high-entropy signing secrets and deliberate token lifetimes.

## M4 — Docker and local development

**Implementation status: implemented; final smoke verification required.**

- [x] Locked dependency installation using uv.lock.
- [x] Non-root runtime container.
- [x] Production Dockerfile.
- [x] PostgreSQL-backed development Compose stack.
- [x] Container health check.
- [x] Production Compose definition with external database credentials.
- [x] Explicit one-shot Alembic migration before API startup.
- [x] Docker smoke-test script.
- [ ] Successful Docker smoke test on this release branch.

## M5 — Kubernetes deployment

**Implementation status: manifests and deployment documentation implemented; final CI verification required.**

- [x] Canonical Kustomize base under k8s/base.
- [x] API Deployment and ClusterIP Service.
- [x] ConfigMap and non-committed Secret example.
- [x] Liveness and readiness probes.
- [x] Resource requests and limits.
- [x] Explicit migration Job.
- [x] Production overlay and migration overlay.
- [x] Optional Ingress example.
- [x] Optional HPA overlay.
- [x] Rollout and rollback instructions.
- [ ] Successful render of all overlays on this release branch.

## M6 — Release verification

**Status: pending final CI evidence.**

- [ ] Ruff passes.
- [ ] Mypy passes with no application errors.
- [ ] Full test suite passes on Python 3.11, 3.12, and 3.13.
- [ ] PostgreSQL integration and migration tests pass.
- [ ] Package build and Twine validation pass.
- [ ] Docker smoke test passes.
- [ ] Production, migration, and HPA Kustomize overlays render successfully.
- [ ] Secret scanning and dependency security workflows pass.
- [ ] Documentation commands match the actual repository.
- [ ] No PydanticAI, Flutter, or stale duplicate Kubernetes implementation remains.

## MVP release definition

The MVP is ready for release when every M6 gate is green on the release commit. Do not mark a gate complete based only on the existence of a workflow or manifest.

The MVP does not promise that every consuming application is automatically production-secure. Applications must still configure secrets, TLS, database access, CORS, backups, monitoring, rate limits, and authorization policy for their deployment environment.

## Change control

Keep this project backend-focused. New features must not expand the MVP silently. PydanticAI, Flutter, frontend work, generators, RBAC, and observability extensions require a separate decision and acceptance criteria.
