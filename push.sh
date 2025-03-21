#!/bin/bash

get_seven_chars_hash() {
    chars=$1
    echo $chars | cut -c 1-7
}

commit_hash=$(get_seven_chars_hash $1)
remote_image_tag="intrasoft0/dokoola-backend:$commit_hash"

echo "Pushing image to $remote_image_tag"

docker tag dokoola-backend $remote_image_tag
docker push $remote_image_tag

# remove the tagged image
docker rmi $remote_image_tag

echo "Image pushed to $remote_image_tag"
