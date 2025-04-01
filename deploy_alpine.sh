#!/bin/sh

# Update system
apk update && apk upgrade

# Install required packages
apk add --no-cache \
    docker \
    docker-compose \
    python3 \
    py3-pip \
    git

# Start Docker service
rc-service docker start

# Clone the repository (if not already done)
# git clone <your-repo-url>

# Build and run the container
docker-compose -f docker-compose.yml up -d --build 