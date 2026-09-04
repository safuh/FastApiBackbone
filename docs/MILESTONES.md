# Project Milestone Tracker

This is the living implementation tracker for FastAPI Backbone. **A checkbox means the acceptance criteria have been verified, not merely that code exists.** Update this file in the same pull request that changes milestone status.

## Status legend

- `[x]` Complete and verified
- `[~]` Implemented but awaiting verification
- `[ ]` Pending

## M1 — Core Foundation

**Status: [~] Implemented; final verification is the release gate**

### Runtime contract

- [x] Canonical development command: `make run` / `uv run uvicorn fastapi_backbone.app:create_app --factory --reload`
- [x] Canonical production command: `make prod` / `uv run uvicorn fastapi_backbone.app:create_app --factory --host 0.0.0.0 --port 8000`
- [x] Application factory at `fastapi_backbone.app:create_app`
- [x] Explicit configuration profiles: `development`, `test`, `production`
- [x] Production rejects debug mode and non-PostgreSQL database URLs
- [x] Structured logging with configurable human-readable/JSON output
- [x] Request correlation IDs propagated through responses and logs

### Database contract

- [x] Async SQLAlchemy 2.x engine and session factory
- [x] Shared engine/session lifecycle owned by FastAPI lifespan
- [x] Engine connectivity checked during non-test startup
- [x] Engine disposed deterministically during shutdown
- [x] Transaction-scoped `session_scope`
- [x] Explicit `UnitOfWork` transaction boundary
- [x] Alembic is the only schema migration mechanism
- [x] Initial domain-neutral migration revision exists
- [x] Production rule: migrations run as an explicit release operation, not per API process

### Operational contract

- [x] `/api/health/live` is process liveness and does not require database access
- [x] `/api/health/ready` returns `503` until startup is complete or the database is unavailable
- [x] Stable error envelope includes request ID
- [x] CORS policy is explicitly configured

### Verification contract

- [x] Application smoke tests
- [x] Startup/shutdown lifecycle tests
- [x] SQLite session/UoW transaction tests
- [x] PostgreSQL integration test with CI service container
- [x] Alembic upgrade/downgrade/upgrade integration gate
- [x] Docker Compose healthcheck
- [x] Docker smoke-test script covering build, startup, health, readiness, and migration
- [x] CI runs Python 3.11, 3.12, and 3.13
- [ ] Final CI run is green on the branch
- [ ] Final Docker smoke test is green in CI/local verification
- [ ] Full mypy gate has zero application errors

**M1 acceptance gate:** the final three verification items must be green before this milestone changes to `[x]`.

## Phase 2 — Database & migrations

**Status: [~] M1 database contract complete; advanced database tooling remains**

- [x] SQLAlchemy 2.x async foundation.
- [x] PostgreSQL and SQLite driver support.
- [x] Alembic async environment.
- [x] Domain-neutral metadata boundary.
- [x] Transaction/unit-of-work guidance.
- [x] PostgreSQL integration tests in CI.
- [x] Migration upgrade/downgrade test gate.
- [x] Migration safety documentation.
- [ ] Additional migration command helpers.

**Acceptance:** a clean checkout can create a database, run migrations, execute integration tests, and recover from a migration failure using documented procedures.

## Phase 3 — Identity & JWT

**Status: [~] In progress; authentication service layer and integration coverage verified**

- [x] Signed JWT token service.
- [x] Expiration and token-type validation.
- [x] Subject validation.
- [x] Minimum secret length guard.
- [x] Password hashing with a modern password-hashing library.
- [x] Authentication service layer with persistence-independent credential lookup and access-token issuance.
- [x] Application-level login use-case contract with transport-neutral request/result types.
- [x] User persistence model as an optional identity module.
- [ ] Login/register/refresh/logout HTTP/application flows.
- [~] Refresh-token rotation and revocation; awaiting CI verification.
- [ ] RBAC and OAuth2 scopes.
- [ ] Rate limiting and abuse controls.
- [x] Security-focused integration tests.
- [ ] Threat model and deployment guidance.

**Acceptance:** authentication has documented security properties, automated abuse/security tests, and safe production defaults.

## Phase 4 — Project generator / CLI

**Status: [ ] Pending**

- [ ] `fastapi-backbone new` command.
- [ ] Non-interactive flags for CI and automation.
- [ ] Template versioning.
- [ ] Generated backend smoke test.
- [ ] Generated project quality gates.
- [ ] `db` migration helper commands.
- [ ] `doctor` environment diagnostics.
- [ ] OpenAPI client generation command.

## Phase 5 — Flutter client

**Status: [ ] Pending

- [ ] Flutter application template.
- [ ] Environment configuration.
- [ ] API client abstraction.
- [ ] OpenAPI-generated client/models.
- [ ] Authentication state management.
- [ ] Secure token-storage abstraction.
- [ ] Login/logout/session refresh example.
- [ ] Flutter tests and static analysis.

## Phase 6 — Docker & local development

**Status: [~] M1 Docker smoke contract implemented; production container hardening remains**

- [x] PostgreSQL Compose service.
- [x] Non-root container execution.
- [x] Health checks.
- [x] Local smoke-test workflow.
- [ ] Production Dockerfile hardening and reproducible lockfile workflow.
- [ ] One-command production deployment path.

## Phase 7 — Kubernetes

**Status: [ ] Pending**

- [ ] Kustomize base and overlays.
- [ ] Deployment, Service, ConfigMap and secret templates.
- [ ] Migration Job.
- [ ] Readiness/liveness probes.
- [ ] Resource requests/limits.
- [ ] Ingress template.
- [ ] Optional HPA overlay.
- [ ] Rollout/rollback documentation.

## Phase 8 — Observability & security hardening

**Status: [~] In progress**

- [x] Correlation IDs propagated through responses and structured logging context.
- [ ] OpenTelemetry integration point.
- [ ] Metrics integration point.
- [ ] Structured audit events for identity operations.
- [x] Dependency vulnerability scanning.
- [ ] Secret scanning.
- [ ] SBOM/release provenance.
- [ ] Threat model review.
- [ ] Security regression suite.

## Phase 9 — Release candidate

**Status: [ ] Pending**

- [ ] Public documentation site.
- [ ] Example applications.
- [ ] API stability policy.
- [ ] Semantic versioning policy.
- [ ] Changelog/release automation.
- [ ] PyPI Trusted Publishing.
- [ ] Generated-project compatibility matrix.
- [ ] Upgrade guide.
- [ ] External contributor review.

## Phase 10 — v1.0

**Status: [ ] Pending**

- [ ] All required production gates green.
- [ ] No known critical/high security issues.
- [ ] Reference application deployed successfully.
- [ ] Generator produces a complete documented stack.
- [ ] Flutter client integration verified.
- [ ] Docker and Kubernetes paths verified.
- [ ] Documentation reviewed end-to-end.
- [ ] Release candidate feedback incorporated.

## Change-control rule

If a feature is not required for the current milestone, do not silently expand the scope. Add it to a later milestone or an issue first. This tracker is intentionally conservative so that “production-grade” remains an evidence-based claim.
