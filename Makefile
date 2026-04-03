SHELL := /bin/bash

COMPOSE := docker compose
PROD_FILES := -f docker-compose.yml
DEV_FILES := -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: help up up-prod up-dev down down-v logs logs-dev logs-prod logs-color ps restart build-prod build-dev config-prod config-dev migrate seed test-integration

help:
	@echo "Available targets:"
	@echo "  make up-prod         Start production-like stack"
	@echo "  make up-dev          Start development stack"
	@echo "  make up              Alias for up-dev"
	@echo "  make down            Stop and remove containers"
	@echo "  make down-v          Stop and remove containers + volumes"
	@echo "  make logs            Tail logs for prod compose"
	@echo "  make logs-dev        Tail logs for dev compose"
	@echo "  make logs-prod       Tail logs for prod compose"
	@echo "  make logs-color      Alias for logs-dev"
	@echo "  make ps              Show running services for prod compose"
	@echo "  make restart         Restart prod compose services"
	@echo "  make build-prod      Build prod compose images"
	@echo "  make build-dev       Build dev compose images"
	@echo "  make config-prod     Render merged prod compose config"
	@echo "  make config-dev      Render merged dev compose config"
	@echo "  make migrate         Run Alembic migrations on api"
	@echo "  make seed            Seed database using api service"
	@echo "  make test-integration Run integration tests in local venv"

up: up-dev

up-prod:
	$(COMPOSE) $(PROD_FILES) up --build -d

up-dev:
	$(COMPOSE) $(DEV_FILES) up --build -d

down:
	$(COMPOSE) $(PROD_FILES) down

down-v:
	$(COMPOSE) $(PROD_FILES) down -v

logs:
	$(COMPOSE) $(PROD_FILES) logs -f --no-log-prefix

logs-dev:
	$(COMPOSE) $(DEV_FILES) logs -f --no-log-prefix

logs-color: logs-dev

logs-prod:
	$(COMPOSE) $(PROD_FILES) logs -f --no-log-prefix

ps:
	$(COMPOSE) $(PROD_FILES) ps

restart:
	$(COMPOSE) $(PROD_FILES) restart

build-prod:
	$(COMPOSE) $(PROD_FILES) build

build-dev:
	$(COMPOSE) $(DEV_FILES) build

config-prod:
	$(COMPOSE) $(PROD_FILES) config

config-dev:
	$(COMPOSE) $(DEV_FILES) config

migrate:
	$(COMPOSE) $(PROD_FILES) exec api alembic upgrade head

seed:
	$(COMPOSE) $(PROD_FILES) exec api python seed_database.py

test-integration:
	/Users/user/advanced-ecommerce/.venv/bin/python -m pytest -q tests/integration
