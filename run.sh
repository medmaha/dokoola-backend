#!/bin/bash

env_file=.env.prod
image=dokoola-backend


# check if container exists
if [ "$(docker ps -q -f name=$image)" ]; then
    echo "Container $image exists. Restarting instead..."
    docker restart $image
    exit 0
fi

docker run -d \
    -p 8000:8000 \
    --name $image \
    $image
