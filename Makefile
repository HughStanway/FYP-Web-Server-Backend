# Default environment file
ENV_FILE ?= .env

# Project name (optional, to avoid conflicts with other projects)
PROJECT_NAME ?= fyp-prototype

build:
	docker compose down --volumes --remove-orphans
	docker compose up --build -d

# Rebuild after making changes
rebuild:
	docker compose down && docker compose up --build -d

# Restart (force recreate)
restart:
	docker compose up -d --force-recreate

# Stop containers but keep data
stop:
	docker compose stop

# Stop and remove everything (containers, networks, and volumes)
down:
	docker compose down --volumes --remove-orphans

# Show logs
logs:
	docker compose logs -f