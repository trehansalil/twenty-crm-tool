.PHONY: help setup dev-build dev-up dev-start dev-stop dev-restart dev-down dev-logs dev-logs-fastapi dev-logs-server dev-clean dev-ps dev-shell-fastapi

help:
	@echo "Available commands:"
	@echo "  setup             - Initial setup: copy .env.example to .env (if needed) and build"
	@echo "  dev-build         - Build all Docker services"
	@echo "  dev-up            - Build and start all services in detached mode"
	@echo "  dev-start         - Start existing services without rebuilding"
	@echo "  dev-stop          - Stop all running services"
	@echo "  dev-restart       - Restart all services"
	@echo "  dev-down          - Stop and remove all containers, networks"
	@echo "  dev-logs          - Show logs from all services (follow mode)"
	@echo "  dev-logs-fastapi  - Show logs from FastAPI service only"
	@echo "  dev-logs-server   - Show logs from Twenty server only"
	@echo "  dev-ps            - List all running containers"
	@echo "  dev-shell-fastapi - Open a shell in the FastAPI container"
	@echo "  dev-clean         - Stop and remove all containers, networks, volumes, and images"

setup:
	@echo "Setting up the project..."
	@if [ ! -f .env ]; then \
		if [ -f .env.example ]; then \
			cp .env.example .env; \
			echo ".env file created from .env.example"; \
		else \
			echo "Warning: No .env.example found. Please create .env manually."; \
		fi; \
	else \
		echo ".env file already exists"; \
	fi
	@echo "Building Docker services..."
	@docker-compose build

dev-build:
	@echo "Building all Docker services..."
	@docker-compose build

dev-up:
	@echo "Starting all services..."
	@docker-compose up -d --build
	@echo "Services are running. Access:"
	@echo "  - Twenty CRM: http://localhost:3000"
	@echo "  - FastAPI: http://localhost:1000"
	@echo "  - FastAPI Docs: http://localhost:1000/docs"

dev-start:
	@echo "Starting existing services..."
	@docker-compose start

dev-stop:
	@echo "Stopping all services..."
	@docker-compose stop

dev-restart:
	@echo "Restarting all services..."
	@docker-compose restart

dev-down:
	@echo "Stopping and removing containers and networks..."
	@docker-compose down

dev-logs:
	@echo "Showing logs from all services (Ctrl+C to exit)..."
	@docker-compose logs -f

dev-logs-fastapi:
	@echo "Showing logs from FastAPI service (Ctrl+C to exit)..."
	@docker-compose logs -f fastapi

dev-logs-server:
	@echo "Showing logs from Twenty server (Ctrl+C to exit)..."
	@docker-compose logs -f server

dev-ps:
	@echo "Listing all running containers..."
	@docker-compose ps

dev-shell-fastapi:
	@echo "Opening shell in FastAPI container..."
	@docker-compose exec fastapi /bin/bash

dev-clean:
	@echo "Cleaning up all Docker resources..."
	@docker-compose down -v --remove-orphans
	@docker-compose rm -f
	@echo "Cleanup complete!"
