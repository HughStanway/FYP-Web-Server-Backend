# Default environment file
ENV_FILE ?= .env

# Project name (optional, to avoid conflicts with other projects)
PROJECT_NAME ?= fyp-prototype

build:
	docker compose down --volumes --remove-orphans
	docker compose up --build -d

# Rebuild only if FastAPI code changes (without rebuilding dependencies)
reload:
	docker compose restart fastapi

# Rebuild if dependencies or Dockerfile change
rebuild:
	docker compose down && docker compose up --build -d

# Stop containers but keep data
stop:
	docker compose stop

# Stop and remove everything (containers, networks, and volumes)
down:
	docker compose down --volumes --remove-orphans