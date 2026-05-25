# Makefile for common commands

.PHONY: help build up down logs test clean seed

## Variables
DOCKER_COMPOSE := docker-compose
BACKEND_DIR := backend
FRONTEND_DIR := frontend

help:
	@echo "Vehicle Rental SaaS - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make build              Build Docker images"
	@echo "  make up                 Start all services"
	@echo "  make down               Stop all services"
	@echo "  make clean              Remove volumes and containers"
	@echo ""
	@echo "Database:"
	@echo "  make seed               Seed database with demo data"
	@echo "  make db-shell           Connect to MongoDB shell"
	@echo ""
	@echo "Logs & Debugging:"
	@echo "  make logs               View all service logs"
	@echo "  make logs-backend       View backend logs"
	@echo "  make logs-frontend      View frontend logs"
	@echo ""
	@echo "Development:"
	@echo "  make test               Run backend tests"
	@echo "  make lint               Run code linting"
	@echo "  make format             Format code"
	@echo ""

# Setup & Installation
build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d
	@echo "✅ All services started"

down:
	$(DOCKER_COMPOSE) down
	@echo "✅ All services stopped"

clean:
	$(DOCKER_COMPOSE) down -v
	@echo "✅ Containers and volumes removed"

restart: down up
	@echo "✅ Services restarted"

# Database
seed:
	$(DOCKER_COMPOSE) exec backend python scripts/seed_db.py

db-shell:
	$(DOCKER_COMPOSE) exec -it vehicle_rental_mongodb mongosh

db-backup:
	@mkdir -p backups
	$(DOCKER_COMPOSE) exec vehicle_rental_mongodb mongodump --uri="mongodb://admin:password123@localhost:27017/vehicle_rental_saas?authSource=admin" --out=/backups/backup_$$(date +%Y%m%d_%H%M%S)

db-stats:
	$(DOCKER_COMPOSE) exec vehicle_rental_mongodb mongosh --eval "db.stats()"

# Logs & Debugging
logs:
	$(DOCKER_COMPOSE) logs -f

logs-backend:
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend:
	$(DOCKER_COMPOSE) logs -f frontend

logs-mongodb:
	$(DOCKER_COMPOSE) logs -f mongodb

logs-redis:
	$(DOCKER_COMPOSE) logs -f redis

stats:
	$(DOCKER_COMPOSE) stats

# Development
test:
	cd $(BACKEND_DIR) && pytest

lint:
	cd $(BACKEND_DIR) && flake8 app

format:
	cd $(BACKEND_DIR) && black app

install-backend:
	cd $(BACKEND_DIR) && pip install -r requirements.txt

install-frontend:
	cd $(FRONTEND_DIR) && npm install

.PHONY: help build up down logs test clean seed db-shell logs-backend logs-frontend
