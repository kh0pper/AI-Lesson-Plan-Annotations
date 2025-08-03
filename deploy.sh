#!/bin/bash

# AI Lesson Plan Annotator Deployment Script
set -e

echo "🚀 AI Lesson Plan Annotator Deployment Script"
echo "=" * 50

# Configuration
CONTAINER_NAME="ai-lesson-annotator"
IMAGE_NAME="lesson-annotator:latest"
PORT="3000"

# Function to check if container exists
container_exists() {
    docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"
}

# Function to check if container is running
container_running() {
    docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"
}

# Stop and remove existing container
if container_exists; then
    echo "📦 Stopping existing container..."
    docker stop $CONTAINER_NAME || true
    echo "🗑️  Removing existing container..."
    docker rm $CONTAINER_NAME || true
fi

# Build the image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

# Run the container
echo "🚀 Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --env-file .env \
    --restart unless-stopped \
    $IMAGE_NAME

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 5

# Check if container is running
if container_running; then
    echo "✅ Container started successfully!"
    echo "📍 Application available at: http://localhost:$PORT"
    echo "📊 Container status:"
    docker ps --filter "name=$CONTAINER_NAME"
else
    echo "❌ Container failed to start!"
    echo "📋 Container logs:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Optional: Start Watchtower for auto-updates
echo ""
echo "🔄 Starting Watchtower for automatic updates..."
docker run -d \
    --name watchtower \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e WATCHTOWER_CLEANUP=true \
    -e WATCHTOWER_POLL_INTERVAL=300 \
    --restart unless-stopped \
    containrrr/watchtower \
    $CONTAINER_NAME

echo ""
echo "🎉 Deployment complete!"
echo "📍 Application: http://localhost:$PORT"
echo "🔄 Auto-updates: Enabled (checks every 5 minutes)"
echo ""
echo "📋 Management commands:"
echo "  View logs: docker logs $CONTAINER_NAME"
echo "  Stop app: docker stop $CONTAINER_NAME"
echo "  Restart: docker restart $CONTAINER_NAME"