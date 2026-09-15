# Kubernetes deployment foundation

FastAPI Backbone includes a small Kustomize reference deployment for Kubernetes. It keeps application configuration, secrets, migrations, and workload rollout as explicit release operations.

## Layout

- `k8s/base/` — reusable Deployment, Service, and non-secret application configuration.
- `k8s/base/secret.example.yaml` — secret template; it is intentionally **not** part of the base Kustomization.
- `k8s/migration/` — Kustomize entrypoint for the explicit one-shot Alembic migration Job.
- `k8s/overlays/production/` — production image override.

## Before applying

Create the `fastapi-backbone` Secret out of band. Do not commit real credentials:

```bash
kubectl create secret generic fastapi-backbone \
  --from-literal=DATABASE_URL='postgresql+asyncpg://USER:PASSWORD@HOST:5432/DATABASE'
```

The application image is also intentionally a release input. The production overlay uses `example.invalid/fastapi-backbone:replace-me` as a visible placeholder. Replace it with the image published by your release pipeline before deployment.

## Render and validate

```bash
kubectl kustomize k8s/overlays/production
kubectl kustomize k8s/migration
```

Review the rendered manifests before applying them.

## Migration

Migrations are deliberately separate from API startup. Build/apply the workload only after the image, ConfigMap, and Secret are ready, and run the migration Job explicitly:

```bash
kubectl create -k k8s/migration
kubectl get jobs
kubectl logs job/<generated-migration-job-name>
```

The Job uses `generateName`, so each invocation creates a new one-shot Job. The migration command is exactly `alembic upgrade head`.

## Deploy the API

```bash
kubectl apply -k k8s/overlays/production
kubectl rollout status deployment/fastapi-backbone
kubectl get service fastapi-backbone
```

The Deployment exposes port 8000 through a ClusterIP Service and uses:

- liveness: `/api/health/live`
- readiness: `/api/health/ready`

The probes match the application's existing health contract. Readiness is intended to keep traffic away while startup/database readiness is unavailable; liveness does not require database access.

## Rollout and rollback

Roll out a new image by updating the production overlay image reference, then render and apply it. Observe the rollout before considering the release complete:

```bash
kubectl rollout status deployment/fastapi-backbone
```

If a rollout must be reverted:

```bash
kubectl rollout undo deployment/fastapi-backbone
kubectl rollout status deployment/fastapi-backbone
```

Database migrations remain an explicit release step and should be planned for backward compatibility with the application version being rolled out.

## Scope

This is the Phase 7 foundation only. Resource requests/limits, Ingress, HPA, and broader release automation remain later slices and are not implied by these manifests.
