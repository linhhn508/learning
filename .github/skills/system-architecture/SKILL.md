---
name: system-architecture
description: "Use when: designing system architecture, reviewing Docker setup, improving docker-compose, reviewing Nginx config, planning scaling strategy, evaluating CI/CD pipelines, reviewing infrastructure, choosing between services, planning migrations, evaluating load balancing, reviewing environment management, planning Kubernetes deployment. Triggers on: review architecture, improve Docker, scale, CI/CD, infrastructure, Kubernetes, deploy, load balancer, Nginx."
---

# System Architecture Review & Design

Review, improve, and design infrastructure and deployment architecture. Always read `docker-compose.yml`, Dockerfiles, and Nginx config before proposing changes.

## Workflow

1. **Read infrastructure files** — `docker-compose.yml`, `Dockerfile.*`, `load-balancer/nginx.conf`, `.env`
2. **Map the current architecture** — services, networks, volumes, exposed ports
3. **Identify issues** — check against the references below
4. **Propose improvements** — with clear reasoning for each change

## Current Architecture

```
Browser → :8000 → Nginx → web:5000 (Flask/Gunicorn)
                                ├── mongo:27017 (MongoDB)
                                └── minio:9000 (MinIO S3)
Browser → :9000 → MinIO (image loading, public bucket)
Browser → :9001 → MinIO Console
```

Key decisions:
- `MINIO_URL` = internal Docker address (Flask → MinIO)
- `MINIO_PUBLIC_URL` = host-facing address (browser → MinIO)
- `minio-init` = one-shot container for bucket setup after healthcheck
- Nginx as reverse proxy, Flask never directly exposed

## When Reviewing Docker

- Pin image tags — never use `latest` in production
- Use healthchecks on all services; dependents use `condition: service_healthy`
- Use named volumes for persistent data (MongoDB, MinIO)
- Use `$$` for shell variables in compose `entrypoint:` (escape compose interpolation)
- Layer Dockerfile for cache efficiency: config files first, source code last

## References

- **Docker best practices**: See [references/docker.md](references/docker.md)
- **Scaling strategies**: See [references/scaling.md](references/scaling.md)
- **CI/CD patterns**: See [references/cicd.md](references/cicd.md)

## Constraints

- DO NOT remove the Nginx reverse proxy — Flask/Gunicorn must not be exposed directly
- DO NOT combine services into a single container (keep separation of concerns)
- DO NOT store secrets in `docker-compose.yml` — use `.env` file with `${VAR}` interpolation
- DO NOT remove healthchecks — they are required for proper startup ordering
