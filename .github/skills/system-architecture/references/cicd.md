# CI/CD Pipeline Patterns

## GitHub Actions: Build & Test

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongo:
        image: mongo:7.0
        ports: [27017:27017]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install uv && uv sync
      - run: uv run pytest --tb=short
        env:
          MONGODB_HOST: localhost:27017

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check . && ruff format --check .
```

## Docker Image CI

```yaml
  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: Dockerfile.web_app
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ghcr.io/${{ github.repository }}/web:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Deployment Strategies

### Blue-Green (Recommended for this project)
1. Build new image → push to registry
2. Deploy new containers alongside old ones
3. Switch Nginx upstream to new containers
4. Remove old containers

### Rolling Update (Docker Swarm / Kubernetes)
```yaml
deploy:
  update_config:
    parallelism: 1     # Update one at a time
    delay: 10s          # Wait between updates
    failure_action: rollback
```

### Canary (Advanced)
- Route 10% of traffic to new version
- Monitor error rates
- Gradually increase to 100%

## Environment Promotion

```
dev (local docker-compose)
  → staging (docker compose on VPS, separate MongoDB)
    → production (Swarm/K8s, managed MongoDB Atlas)
```

### Secrets Management
- **Local**: `.env` file (gitignored)
- **CI**: GitHub Actions Secrets (`${{ secrets.MINIO_PWD }}`)
- **Production**: Docker Secrets, Kubernetes Secrets, or Vault

### Environment Variables per Stage
```yaml
# Use GitHub Environments for stage-specific vars
jobs:
  deploy:
    environment: production  # Requires approval
    steps:
      - run: docker compose up -d
        env:
          MINIO_URL: ${{ vars.MINIO_URL }}
          MONGODB_HOST: ${{ vars.MONGODB_HOST }}
```

## Pre-Deployment Checklist
- [ ] All tests pass
- [ ] Linting clean (ruff check + ruff format)
- [ ] Docker image builds successfully
- [ ] No hardcoded secrets in code
- [ ] Database migrations applied (if any)
- [ ] Health endpoints respond correctly
- [ ] Rollback plan documented
