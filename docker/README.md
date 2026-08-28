# Docker

Docker assets will provide reproducible development and production application images.

## Requirements for the production image

- multi-stage build where useful;
- non-root runtime user;
- deterministic dependency installation;
- no development dependencies in production;
- process-level health endpoint;
- graceful signal handling; and
- no secrets baked into image layers.

The Docker milestone is pending. Do not treat the current repository as having a validated production container until the Docker acceptance checklist in `docs/MILESTONES.md` is complete.
