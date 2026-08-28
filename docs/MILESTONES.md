# Project Milestone Tracker

This is the living implementation tracker for FastAPI Backbone. **A checkbox means the acceptance criteria have been verified, not merely that code exists.** Update this file in the same pull request that changes milestone status.

## Status legend

- `[x]` Complete and verified
- `[~]` In progress
- `[ ]` Pending

## Phase 0 — Architecture & governance

**Status: [x] Complete**

- [x] Define domain-neutral mission and non-goals.
- [x] Choose src-layout packaging.
- [x] Define API → application → contracts → infrastructure dependency direction.
- [x] Establish MIT licensing and contribution/security policy.
- [x] Establish milestone tracker and documentation structure.
- [x] Establish production-grade acceptance definition.

**Gate:** repository can evolve without mixing product/domain code into the foundation.

## Phase 1 — Core package foundation

**Status: [~] In progress**

- [x] `fastapi_backbone` package and application factory.
- [x] Typed Pydantic settings.
- [x] Async SQLAlchemy engine/session infrastructure.
- [x] Explicit FastAPI lifespan and engine disposal.
- [x] Structured logging foundation.
- [x] Liveness/readiness endpoints.
- [x] Basic smoke tests.
- [ ] Correlation/request IDs.
- [ ] Central exception taxonomy and handlers.
- [ ] CORS/security middleware configuration.
- [ ] Integration-test fixtures.
- [ ] Full type-checking gate without ignored application errors.

**Acceptance:** package installs, app boots, tests pass, resources shut down cleanly, and public APIs are documented.

## Phase 2 — Database & migrations

**Status: [~] In progress**

- [x] SQLAlchemy 2.x async foundation.
- [x] PostgreSQL and SQLite driver support.
- [x] Alembic async environment.
- [x] Domain-neutral metadata boundary.
- [ ] Migration command helpers.
- [ ] Transaction/unit-of-work guidance.
- [ ] PostgreSQL integration tests in CI.
- [ ] Migration upgrade/downgrade test gate.
- [ ] Migration safety documentation.

**Acceptance:** a clean checkout can create a database, run migrations, execute integration tests, and recover from a migration failure using documented procedures.

## Phase 3 — Identity & JWT

**Status: [~] In progress**

- [x] Signed JWT token service.
- [x] Expiration and token-type validation.
- [x] Subject validation.
- [x] Minimum secret length guard.
- [ ] Password hashing with a modern password-hashing library.
- [ ] Login/register/refresh/logout flows.
- [ ] Refresh-token rotation and revocation.
- [ ] User persistence model as an optional identity module.
- [ ] RBAC and OAuth2 scopes.
- [ ] Rate limiting and abuse controls.
- [ ] Security-focused integration tests.
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

**Acceptance:** a new project is reproducibly generated from a clean environment and passes the same quality gates as the reference project.

## Phase 5 — Flutter client

**Status: [ ] Pending**

- [ ] Flutter application template.
- [ ] Environment configuration.
- [ ] API client abstraction.
- [ ] OpenAPI-generated client/models.
- [ ] Authentication state management.
- [ ] Secure token-storage abstraction.
- [ ] Login/logout/session refresh example.
- [ ] Flutter tests and static analysis.

**Acceptance:** generated Flutter client authenticates against a generated backend without hand-maintained duplicate API models.

## Phase 6 — Docker & local development

**Status: [ ] Pending**

- [ ] Production Dockerfile.
- [ ] Development Dockerfile/Compose.
- [ ] PostgreSQL Compose service.
- [ ] Non-root container execution.
- [ ] Health checks.
- [ ] Reproducible builds and dependency caching.
- [ ] Local one-command startup documentation.

**Acceptance:** clean checkout → container build → database → migrations → API smoke test is deterministic.

## Phase 7 — Kubernetes

**Status: [ ] Pending**

- [ ] Kustomize base.
- [ ] Development/production overlays.
- [ ] Deployment and Service.
- [ ] ConfigMap and secret templates.
- [ ] Migration Job.
- [ ] Readiness/liveness probes.
- [ ] Resource requests/limits.
- [ ] Ingress template.
- [ ] HPA as an optional overlay.
- [ ] Rollout/rollback documentation.

**Acceptance:** manifests pass static validation and a disposable cluster can deploy, migrate, become ready, and roll back using documented procedures.

## Phase 8 — Observability & security hardening

**Status: [ ] Pending**

- [ ] Correlation IDs propagated through logs.
- [ ] OpenTelemetry integration point.
- [ ] Metrics integration point.
- [ ] Structured audit events for identity operations.
- [ ] Dependency vulnerability scanning.
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
- [ ] Upgrade guide from pre-1.0 releases.
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
