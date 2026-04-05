# Docker Best Practices

## Dockerfile

### Layer Caching
```dockerfile
# 1. Base + system deps (rarely changes)
FROM python:3.12-slim
RUN pip install uv

# 2. Dependency manifest (changes when deps change)
COPY pyproject.toml ./
RUN uv sync

# 3. Source code (changes frequently)
COPY . .
```
Order layers from least to most frequently changing.

### Security
- Use non-root user: `RUN adduser --disabled-password app && USER app`
- Use `.dockerignore` to exclude `.env`, `.git`, `.venv`, `node_modules`
- Don't install unnecessary packages — use `--no-install-recommends`
- Scan images for vulnerabilities: `docker scout cves <image>`

### Size Optimization
- Use `-slim` or `-alpine` base images
- Combine RUN commands to reduce layers
- Multi-stage builds for compiled dependencies
- Remove cache after package install: `rm -rf /var/lib/apt/lists/*`

## Docker Compose

### Service Dependencies
```yaml
# Bad — only waits for container to start
depends_on:
  - mongo

# Good — waits for service to be healthy
depends_on:
  mongo:
    condition: service_healthy
```

### Environment Variables
- Use `.env` file for all config — never inline secrets in compose
- Use `${VAR}` syntax for interpolation
- Use `$$` to escape dollar signs in shell commands inside `entrypoint:`
- Provide defaults where safe: `${MINIO_PUBLIC_URL:-http://localhost:9000}`

### Volumes
- Use named volumes for databases: `mongo_data:/data/db`
- Use bind mounts only for config files: `./nginx.conf:/etc/nginx/nginx.conf:ro`
- Add `:ro` for read-only mounts where possible

### Networking
- Don't expose internal-only services (MongoDB doesn't need port mapping)
- Only expose what the browser needs (Nginx:8000, MinIO:9000 for images)
- Services communicate by name on the default compose network

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 512m
      cpus: '0.5'
```

### Logging
```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```
