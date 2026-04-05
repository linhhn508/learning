Web reference: https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-2-creating-a-base-application

## Local dev (no containers)

```
flask run -p 5000 -h 0.0.0.0
```

## Run with Docker Compose (recommended)

```
docker compose --env-file .env up --build -d
```

First-time MinIO bucket setup (run once after `docker compose up`):
```
mc alias set local http://localhost:9000 admin password123
mc mb local/blog-image
mc anonymous set public local/blog-image
```

## Run manually with individual containers

```
docker network create mynetwork

docker run -d --name test-mongo --network=mynetwork mongo:7.0.32-rc1

docker run -d -p 9000:9000 -p 9001:9001 --name test-minio --network=mynetwork -e "MINIO_ROOT_USER=admin" -e "MINIO_ROOT_PASSWORD=password123" minio/minio server /data --console-address ":9001"

docker run -p 8000:5000 -d --name test_web_app --network=mynetwork -e MONGODB_HOST="test-mongo" -e MINIO_URL="http://test-minio:9000" -e MINIO_PUBLIC_URL="http://localhost:9000" -e MINIO_USR="admin" -e MINIO_PWD="password123" web_app:latest
```

MinIO bucket setup:
```
mc alias set local http://localhost:9000 admin password123
mc mb local/blog-image
mc anonymous set public local/blog-image
```