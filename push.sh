#!/bin/bash
set -e  # Exit immediately on error

# Add commit hash validation
if [ -z "$1" ]; then
    echo "Error: Commit hash not provided" >&2
    exit 1
fi

commit_hash=$(echo "$1" | cut -c 1-7)
local_image="dokoola-backend"
remote_repo="intrasoft0/dokoola-backend"
remote_image_tag="$remote_repo:$commit_hash"
remote_latest_image_tag="$remote_repo:latest"

echo "Pushing image to $remote_image_tag"

# Tag the local image to a remote image
docker tag $local_image $remote_image_tag
docker push $remote_image_tag

# Tag the remote image to another remote image as :latest
docker tag $remote_image_tag $remote_latest_image_tag
docker push $remote_latest_image_tag

# remove the tagged image
# This is only for the local dev-env
docker rmi $remote_image_tag
docker rmi $remote_latest_image_tag

echo "Image pushed to $remote_image_tag"
