# Scaling Strategies

## Current: Single Instance

```
Nginx (1) → Flask (1) → MongoDB (1) + MinIO (1)
```

### Horizontal Scaling with Docker Compose

Scale Flask instances behind Nginx:
```bash
docker compose up --scale web=3
```

Nginx upstream auto-discovers with Docker DNS:
```nginx
upstream flask_app {
    server web:5000;    # Docker resolves to all 3 containers
}
```

**Requirements for stateless scaling:**
- [ ] No in-memory session state — use server-side sessions (MongoDB or Redis)
- [ ] No local file storage — all files go to MinIO ✓
- [ ] `SECRET_KEY` must be identical across all instances (from env var)
- [ ] Sticky sessions OR stateless auth (JWT) if using login

## Next Level: Docker Swarm

```yaml
deploy:
  replicas: 3
  update_config:
    parallelism: 1
    delay: 10s
  restart_policy:
    condition: on-failure
```

Benefits over plain compose:
- Rolling updates (zero-downtime deploys)
- Automatic restart on failure
- Built-in service discovery
- Secrets management (`docker secret`)

## Production: Kubernetes

```
Ingress → Service → Deployment (N pods)
                         ├── MongoDB (StatefulSet or managed Atlas)
                         └── MinIO (StatefulSet or managed S3)
```

Migration path:
1. Replace `docker-compose.yml` with Kubernetes manifests
2. Use `ConfigMap` for env vars, `Secret` for credentials
3. Use `PersistentVolumeClaim` for MongoDB and MinIO data
4. Use `HorizontalPodAutoscaler` for auto-scaling Flask pods
5. Consider managed services: MongoDB Atlas, AWS S3 (drop MinIO)

## Database Scaling

### MongoDB
- **Replica Set** — 3-node for high availability (automatic failover)
- **Read replicas** — offload read queries from primary
- **Sharding** — only at very high scale (millions of documents)
- **Managed**: MongoDB Atlas (free tier available)

### MinIO
- **Erasure coding** — distribute across 4+ drives for fault tolerance
- **Multi-node** — MinIO cluster for high availability
- **Managed**: Switch to AWS S3 / DigitalOcean Spaces for zero-ops
