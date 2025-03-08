#!/usr/bin/env bash

# Ensure you're logged into Docker Hub
# docker login

# Tag the local image for Docker Hub
docker tag dokoola-backend intrasoft0/dokoola:backend-001

# Push to Docker Hub
docker push intrasoft0/dokoola:backend-001
