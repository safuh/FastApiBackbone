# Kubernetes deployment foundation

FastAPI Backbone includes a small Kustomize reference deployment for Kubernetes. It keeps application configuration, secrets, migrations, workload sizing, and rollout as explicit release operations.

## Layout

- `k8s/base/` — reusable Deployment, Service, and non-secret application configuration.
- `k8s/base/secret.example.yaml` — secret template; it is intentionally **not** part of the base Kustomization.
- `k8s/base/ingress.example.yaml` — optional Ingress template; it is intentionally not part of the base Kustomization.
- `k8s/base/migration/` — reusable Kustomize base for the one-shot migration Job.
- `k8s/overlays/production/` — production image override with baseline resource requests/limits.
- `k8s/overlays/production/migration/` — production image override for the migration Job.
- `k8s/overlays/production/hpa/` — optional CPU-based HorizontalPodAutoscaler overlay.

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
kubectl kustomize k8s/overlays/production/migration
kubectl kustomize k8s/overlays/production/hpa
```

Review the rendered manifests before applying them.

## Resource policy

The API Deployment has explicit baseline resources:

- requests: `100m` CPU and `128Mi` memory
- limits: `500m` CPU and `512Mi` memory

These are deliberately conservative defaults for the reference deployment. Production environments should tune them from observed workload and capacity data rather than treating them as universal sizing guidance.

## Ingress

The Ingress is an example template and is not included automatically. It assumes an NGINX Ingress controller and uses `api.example.com` as a placeholder host. Copy or customize it for the cluster's ingress controller, hostname, TLS policy, and annotations before applying it.

```bash
kubectl apply -f k8s/base/ingress.example.yaml
```

Do not apply the template unchanged to a production cluster.

## Optional HPA

The HPA is opt-in because it requires a metrics pipeline such as Metrics Server. It targets CPU utilization at 70%, with 1–3 replicas and conservative scale-down stabilization:

```bash
kubectl apply -k k8s/overlays/production/hpa
kubectl get hpa fastapi-backbone
```

If the cluster does not provide the required resource metrics, the HPA will not be able to make scaling decisions. The baseline production overlay remains usable without the HPA.

## Migration

Migrations are deliberately separate from API startup. Build/apply the workload only after the image, ConfigMap, and Secret are ready, and run the migration Job explicitly:

```bash
kubectl create -k k8s/overlays/production/migration
kubectl get jobs
kubectl logs job/fastapi-backbone-migrate
```

The migration Job has a stable name because Kustomize requires named resources. It is a one-shot Job running exactly `alembic upgrade head`. Before rerunning it, remove the completed/failed Job:

```bash
kubectl delete job fastapi-backbone-migrate
kubectl create -k k8s/overlays/production/migration
```

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

This slice adds baseline resource requests/limits, an opt-in Ingress template, and an opt-in HPA overlay. Broader release automation remains a later slice.
