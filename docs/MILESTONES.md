# Project Milestone Tracker

This is the living implementation tracker for FastAPI Backbone. **A checkbox means the acceptance criteria have been verified, not merely that code exists.** Update this file in the same pull request that changes milestone status.

## Status legend

- [x] Complete and verified
- [~] Implemented but awaiting verification / milestone in progress
- [ ] Pending

## M1 — Core Foundation

**Status: [x] Complete and verified**

- [x] Canonical development and production commands.
- [x] Application factory and explicit development/test/production profiles.
- [x] Async SQLAlchemy 2.x engine/session lifecycle and Unit of Work.
- [x] Alembic-only schema migration mechanism.
- [x] Liveness/readiness contract.
- [x] Structured logging and request correlation IDs.
- [x] Stable error envelope and explicit CORS policy.
- [x] SQLite transaction tests and PostgreSQL integration tests.
- [x] Alembic upgrade/downgrade/upgrade integration gate.
- [x] Docker Compose healthcheck and smoke-test workflow.
- [x] Python 3.11/3.12/3.13 CI gate.
- [x] Full mypy application gate.

**Acceptance gate:** all final verification requirements are green.

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
- [x] Additional migration command helpers.

## Phase 3 — Identity & JWT

**Status: [~] In progress; core authentication lifecycle and security contract verified**

- [x] Signed JWT token service.
- [x] Expiration and token-type validation.
- [x] Subject validation.
- [x] Minimum secret length guard.
- [x] Password hashing with a modern password-hashing library.
- [x] Authentication service layer with persistence-independent credential lookup and access-token issuance.
- [x] Application-level login use-case contract with transport-neutral request/result types.
- [x] User persistence model as an optional identity module.
- [x] Login/register/refresh/logout HTTP/application flows.
- [x] Refresh-token rotation and revocation.
- [x] SQLAlchemy refresh-token persistence and migration.
- [ ] RBAC and OAuth2 scopes.
- [ ] Rate limiting and abuse controls.
- [x] Security-focused integration tests.
- [x] Threat model and deployment guidance.

## Phase 4 — Project generator / CLI

**Status: [~] In progress**

### Generator core

- [x] `fastapi-backbone new` command foundation.
- [x] Non-interactive project name/output flags.
- [x] Safe refusal to overwrite non-empty directories by default.
- [x] Explicit `--force` behavior for empty/existing targets.
- [x] Deterministic generated package layout.
- [x] Generated-project smoke test template.
- [x] Dedicated template-rendering boundary.
- [x] Versioned template version metadata (`0.2.0`).
- [x] Production source template inherits verified API/auth/core/identity contracts.
- [x] Generated Alembic environment and initial identity/refresh-token migration.
- [x] Generated Dockerfile and PostgreSQL Compose path.
- [x] Generated CI quality-gate workflow.
- [x] Formal template registry and compatibility metadata.
- [x] `db` migration helper commands (`upgrade`, `downgrade`, `current`, `history`).
- [x] `doctor` environment diagnostics.
- [x] OpenAPI client generation command; default and AI projects pass genuine `openapi-python-client` generation plus the public wrapper in CI.
- [x] Generated-project quality gates; default and AI projects pass end-to-end generation, lint, type checking, tests, migration upgrade/downgrade/upgrade, Docker smoke, Kubernetes validation, security, and secret scanning in CI.

### AI application architecture

- [x] Explicit optional `--ai` profile.
- [x] Pydantic AI remains an optional dependency rather than a core runtime dependency.
- [x] Dedicated generated `ai/` boundary.
- [x] Runtime model identifier rather than provider-specific business logic.
- [x] Initial AI configuration contract.
- [x] Initial Pydantic AI agent factory.
- [x] Provider-neutral AI application contracts (`AIModel`, `AIRequest`, `AIResponse`, `AIProvider`).
- [x] Central AI settings integrated with the canonical application configuration.
- [x] Explicit provider adapter registry with normalized provider names.
- [x] Provider-neutral `provider:model` parsing and model routing boundary.
- [x] AI infrastructure error taxonomy.
- [x] Optional Pydantic AI runtime adapter with bounded async execution and retry configuration.
- [x] Generated AI profile sources the canonical AI architecture instead of maintaining a second simplified implementation.
- [x] Concrete adapter/configuration profiles for OpenAI, Gemini and Ollama/OpenAI-compatible endpoints; profiles are tested and the full CI/generated-project gate is green.
- [x] Structured-output agent templates; generated AI projects pass the structured-agent template tests and full CI/generated-project gate.
- [x] AI dependency-injection contract for application services, repositories and request context; request-scoped provider/session/repository resolution is covered by tests and the full CI/generated-project gate is green.
- [x] Tool runtime with deterministic authorization and allowlists; full CI, generated-project smoke, Security, and Secret scanning are green for commit `46dc881f06fdd848a25569ba4295898f4f218ee8` (CI run `35349459342`).
- [x] AI streaming contract; full CI, generated-project smoke, Security, and Secret scanning are green for commit `ef73612f1a7f4bd24dcdec256758034a35facd89` (CI run `35350281269`).
- [x] AI retries, timeouts, circuit breaking and fallback policy beyond the initial adapter boundary; full CI, generated-project smoke, Security, and Secret scanning are green for commit `052003b16e26df26cd058ff176399cd8dab89dc5` (CI run `35352149926`).
- [ ] Model routing policy beyond explicit provider/model resolution.
- [ ] Token, latency and estimated-cost telemetry.
- [ ] Prompt versioning and prompt test fixtures.
- [ ] AI evaluation/regression framework.
- [ ] Guardrails and prompt-injection defenses.
- [ ] Human-in-the-loop approval boundary for consequential actions.
- [ ] Optional RAG profile.
- [ ] Optional background AI job/worker profile.
- [ ] MCP/tool interoperability profile where it has a stable generated-project contract.

**Generator acceptance:** a clean installation can generate a documented project non-interactively; generated projects pass their own quality gates; AI-enabled projects remain provider-agnostic and keep authorization/execution outside the LLM.

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

## Phase 6 — Docker & local development

**Status: [~] Production container hardening and reference deployment path implemented; final deployment verification remains**

- [x] PostgreSQL Compose service.
- [x] Non-root container execution.
- [x] Health checks.
- [x] Local smoke-test workflow.
- [x] Production Dockerfile hardening and reproducible lockfile workflow.
- [~] One-command production deployment path.

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
- [x] Structured audit events for identity operations.
- [x] Dependency vulnerability scanning.
- [x] Secret scanning.
- [ ] SBOM/release provenance.
- [x] Threat model review.
- [x] Security regression suite.

## Phase 9 — Release candidate

**Status: [ ] Pending**

- [ ] Public documentation site.
- [ ] Example applications, including one AI-enabled example.
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
- [ ] Generator's optional AI architecture verified end-to-end.
- [ ] Flutter client integration verified.
- [ ] Docker and Kubernetes paths verified.
- [ ] Documentation reviewed end-to-end.
- [ ] Release candidate feedback incorporated.

## Change-control rule

If a feature is not required for the current milestone, do not silently expand the scope. Add it to a later milestone or an issue first. This tracker is intentionally conservative so that “production-grade” remains an evidence-based claim.
