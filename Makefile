# Default environment file
ENV_FILE ?= .env

# Project name
PROJECT_NAME ?= fyp-prototype

# Build and start server
build:
	docker compose down
	docker compose up --build -d

# Rebuild after making changes
rebuild:
	docker compose down && docker compose up --build -d

# Restart (force recreate)
restart:
	docker compose up -d --force-recreate

# Stop and remove containers
down:
	docker compose down

# Stop and remove everything (containers, networks, and volumes)
prune:
	docker compose down --volumes --remove-orphans

# Show Docker logs
logs:
	docker compose logs -f

#############
# Dev Tools #
#############

install-dev-tools:
	pip install -r requirements-dev.txt

black:
	black src/

isort:
	isort .