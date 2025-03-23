#!/bin/bash
set -e  # Fail on error

exposed_port=8000
container_port=8000
container_name="dokoola-backend"
image_tag="intrasoft0/dokoola-backend:latest"

# Check if container exists
if sudo docker compose ps | grep -q "$container_name"; then
    sudo docker compose pull
    sudo docker compose up -d --force-recreate
    echo "Updated using docker compose ✅"
else
    # Existing container logic with safety checks
    if sudo docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        sudo docker rm -f "$container_name" || true
    fi

    sudo docker run -d \
        --restart unless-stopped \
        -p $exposed_port:$container_port \
        --name "$container_name" \
        "$image_tag"
fi
