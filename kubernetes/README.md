# Kubernetes

Kubernetes is an optional production deployment target.

The planned implementation uses a small Kustomize base and environment overlays. It will provide an application Deployment, Service, configuration, secret templates, probes, resource controls, and an explicit database migration Job.

## Migration rule

Database migrations must run as an explicit deployment operation rather than inside every application container startup.

```text
release → migration Job → application rollout
```

Real credentials must never be committed to this directory. The repository will contain safe examples and placeholders only.

The Kubernetes milestone is pending; manifests are not yet claimed to be production-validated.
