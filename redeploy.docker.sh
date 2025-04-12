#!/bin/bash
set -e  # Fail on error

host_port=8000
container_port=8000
container_name="dokoola-backend"
image_tag="intrasoft0/dokoola-backend:latest"

sudo docker pull $image_tag

sudo docker stop $container_name
sudo docker rm $container_name

sudo docker run -d \
    --restart unless-stopped \
    -p $host_port:$container_port \
    --name "$container_name" \
    "$image_tag"

sudo docker system prune
