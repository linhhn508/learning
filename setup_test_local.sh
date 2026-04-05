#/bin/bash
# This script sets up the local development environment for the project.

# Create a Python virtual environment

if [ -d ".venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/active

pip install uv

uv sync

export MONGODB_HOST="localhost"
export MINIO_URL="http://localhost:9000"
export MINIO_PUBLIC_URL="http://localhost:9000"
export MINIO_USR="admin"
export MINIO_PWD="password123"


docker ps -q --filter "name=test-mongo" | grep -q . && docker rm -fv test-mongo
docker run -d --name test-mongo -p 27017:27017 mongo:7.0

docker ps -q --filter "name=test-minio" | grep -q . && docker rm -fv test-minio
docker run -d -p 9000:9000 -p 9001:9001 --name test-minio -e "MINIO_ROOT_USER=${MINIO_USR}" -e "MINIO_ROOT_PASSWORD=${MINIO_PWD}" minio/minio server /data --console-address ":9001"

echo "Local development environment setup complete."

flask run -h 0.0.0.0 -p 5000 --debug