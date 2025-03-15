#!/bin/bash

remote_image_tag="intrasoft0/dokoola:$1"

docker tag dokoola-backend $remote_image_tag
docker push $remote_image_tag

# remove the tagged image
docker rmi $remote_image_tag
