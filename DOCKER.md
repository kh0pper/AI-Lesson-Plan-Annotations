# Docker Deployment Guide

This guide explains how to deploy the AI Lesson Plan Annotator using Docker with automatic updates.

## Quick Start

### Option 1: Automated Deployment Script (Recommended)
```bash
./deploy.sh
```

This script will:
- Build the Docker image
- Stop any existing containers
- Start the application container
- Set up Watchtower for automatic updates
- Display management commands

### Option 2: Manual Docker Commands
```bash
# Build the image
docker build -t lesson-annotator:latest .

# Run the container
docker run -d \
  --name ai-lesson-annotator \
  -p 3000:3000 \
  --env-file .env \
  --restart unless-stopped \
  lesson-annotator:latest

# Start Watchtower for auto-updates
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e WATCHTOWER_CLEANUP=true \
  -e WATCHTOWER_POLL_INTERVAL=300 \
  --restart unless-stopped \
  containrrr/watchtower \
  ai-lesson-annotator
```

## Configuration

### Environment Variables
Create a `.env` file with:
```
LLAMA_API_KEY=your_api_key_here
```

### Port Configuration
The application runs on port 3000 by default. To change:
```bash
docker run -d \
  --name ai-lesson-annotator \
  -p 8080:3000 \  # Host port 8080, container port 3000
  --env-file .env \
  lesson-annotator:latest
```

## Automatic Updates with Watchtower

Watchtower monitors your containers and automatically updates them when new images are available.

### Configuration Options
- `WATCHTOWER_POLL_INTERVAL=300` - Check for updates every 5 minutes
- `WATCHTOWER_CLEANUP=true` - Remove old images after updating
- `WATCHTOWER_NOTIFICATIONS=slack` - Send notifications to Slack

### Manual Update Trigger
```bash
# Force immediate update check
docker exec watchtower /watchtower --run-once
```

## Management Commands

### View Application Logs
```bash
docker logs ai-lesson-annotator
docker logs -f ai-lesson-annotator  # Follow logs
```

### Container Management
```bash
# Stop the application
docker stop ai-lesson-annotator

# Start the application
docker start ai-lesson-annotator

# Restart the application
docker restart ai-lesson-annotator

# Remove the container
docker rm ai-lesson-annotator
```

### Image Management
```bash
# List images
docker images | grep lesson-annotator

# Remove old images
docker image prune

# Rebuild image
docker build -t lesson-annotator:latest .
```

## Production Deployment

### With Nginx Reverse Proxy
```bash
# Run with production profile (includes Nginx)
docker-compose --profile production up -d
```

### Health Checks
The container includes built-in health checks:
```bash
# Check container health
docker ps
# Look for "healthy" status

# Manual health check
curl http://localhost:3000/
```

### Resource Limits
```bash
docker run -d \
  --name ai-lesson-annotator \
  -p 3000:3000 \
  --memory=2g \
  --cpus="1.5" \
  --env-file .env \
  lesson-annotator:latest
```

## Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker logs ai-lesson-annotator

# Check if port is in use
ss -tlnp | grep :3000

# Run container interactively for debugging
docker run -it --rm lesson-annotator:latest /bin/bash
```

### Watchtower Issues
```bash
# Check Watchtower logs
docker logs watchtower

# Restart Watchtower
docker restart watchtower
```

### API Key Issues
```bash
# Verify environment variables
docker exec ai-lesson-annotator env | grep LLAMA_API_KEY

# Update environment variables
docker stop ai-lesson-annotator
docker rm ai-lesson-annotator
# Update .env file then run deploy.sh again
```

## Security Considerations

1. **API Keys**: Never include API keys in Docker images
2. **Network**: Use Docker networks for container communication
3. **Updates**: Regular security updates via Watchtower
4. **Logs**: Ensure logs don't contain sensitive information

## CI/CD Integration

The included GitHub Actions workflow automatically builds and pushes Docker images to GitHub Container Registry when you push to the main branch. Watchtower will automatically pull and deploy these updates.