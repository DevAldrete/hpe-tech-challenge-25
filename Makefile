# ============================================================================
# Project AEGIS - Docker Management Makefile
# Convenient shortcuts for common Docker operations
# ============================================================================

.PHONY: help build up down restart logs ps clean dev-up dev-down scale backup test

# Default target
.DEFAULT_GOAL := help

# Docker Compose file location
COMPOSE_FILE := docker/docker-compose.yml

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# ============================================================================
# Help
# ============================================================================

help: ## Show this help message
	@echo "$(BLUE)Project AEGIS - Docker Management$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Basic Operations

build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Start all services (detached)
	@echo "$(GREEN)Starting AEGIS services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services started. Use 'make logs' to view logs$(NC)"
	@echo "$(BLUE)Orchestrator:$(NC) http://localhost:8000"
	@echo "$(BLUE)Dashboard:$(NC)    http://localhost:3000"

down: ## Stop all services
	@echo "$(YELLOW)Stopping AEGIS services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart: down up ## Restart all services

logs: ## View logs from all services (follow mode)
	docker-compose -f $(COMPOSE_FILE) logs -f

ps: ## Show status of all services
	docker-compose -f $(COMPOSE_FILE) ps

##@ Development

dev-up: ## Start services with dev tools (Redis Commander, PgAdmin)
	@echo "$(GREEN)Starting AEGIS with development tools...$(NC)"
	docker-compose -f $(COMPOSE_FILE) --profile dev up -d
	@echo "$(GREEN)Services started with dev tools:$(NC)"
	@echo "$(BLUE)Orchestrator:$(NC)     http://localhost:8000"
	@echo "$(BLUE)Dashboard:$(NC)        http://localhost:3000"
	@echo "$(BLUE)Redis Commander:$(NC)  http://localhost:8081"
	@echo "$(BLUE)PgAdmin:$(NC)          http://localhost:5050"

dev-down: ## Stop services including dev tools
	docker-compose -f $(COMPOSE_FILE) --profile dev down

rebuild: ## Rebuild and restart (no cache)
	@echo "$(GREEN)Rebuilding from scratch...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	docker-compose -f $(COMPOSE_FILE) up -d

##@ Maintenance

clean: ## Stop services and remove volumes (CAUTION: deletes data)
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f $(COMPOSE_FILE) down -v; \
		echo "$(GREEN)Cleanup complete$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

clean-images: ## Remove all AEGIS Docker images
	@echo "$(YELLOW)Removing AEGIS Docker images...$(NC)"
	docker images | grep aegis | awk '{print $$3}' | xargs -r docker rmi -f
	docker images | grep hpe-tech-challenge | awk '{print $$3}' | xargs -r docker rmi -f

prune: ## Remove unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	docker volume prune -f

##@ Scaling

scale-vehicles: ## Scale vehicle agents (usage: make scale-vehicles N=5)
	@if [ -z "$(N)" ]; then \
		echo "$(YELLOW)Usage: make scale-vehicles N=<number>$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Scaling vehicle agents to $(N) instances...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d --scale vehicle-agent-1=$(N)

##@ Monitoring

logs-orchestrator: ## View orchestrator logs
	docker-compose -f $(COMPOSE_FILE) logs -f orchestrator

logs-vehicles: ## View all vehicle agent logs
	docker-compose -f $(COMPOSE_FILE) logs -f vehicle-agent-1 vehicle-agent-2 vehicle-agent-3

logs-redis: ## View Redis logs
	docker-compose -f $(COMPOSE_FILE) logs -f redis

logs-postgres: ## View PostgreSQL logs
	docker-compose -f $(COMPOSE_FILE) logs -f postgres

stats: ## Show resource usage statistics
	docker stats --no-stream

##@ Database Operations

db-shell: ## Open PostgreSQL shell
	docker exec -it aegis-postgres psql -U aegis_user -d aegis_db

db-backup: ## Backup PostgreSQL database
	@mkdir -p backups
	@echo "$(GREEN)Creating database backup...$(NC)"
	docker exec aegis-postgres pg_dump -U aegis_user aegis_db > backups/aegis_db_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup complete: backups/aegis_db_$$(date +%Y%m%d_%H%M%S).sql$(NC)"

db-restore: ## Restore PostgreSQL database (usage: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(YELLOW)Usage: make db-restore FILE=<backup-file>$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	docker exec -i aegis-postgres psql -U aegis_user aegis_db < $(FILE)
	@echo "$(GREEN)Restore complete$(NC)"

db-query: ## Run SQL query (usage: make db-query SQL="SELECT * FROM vehicles")
	@if [ -z "$(SQL)" ]; then \
		echo "$(YELLOW)Usage: make db-query SQL=\"<your-query>\"$(NC)"; \
		exit 1; \
	fi
	docker exec aegis-postgres psql -U aegis_user -d aegis_db -c "$(SQL)"

##@ Redis Operations

redis-cli: ## Open Redis CLI
	docker exec -it aegis-redis redis-cli

redis-keys: ## Show all Redis keys
	docker exec aegis-redis redis-cli KEYS "*"

redis-info: ## Show Redis server info
	docker exec aegis-redis redis-cli INFO

redis-backup: ## Backup Redis data
	@mkdir -p backups
	@echo "$(GREEN)Creating Redis backup...$(NC)"
	docker exec aegis-redis redis-cli SAVE
	docker cp aegis-redis:/data/dump.rdb backups/redis_dump_$$(date +%Y%m%d_%H%M%S).rdb
	@echo "$(GREEN)Backup complete$(NC)"

##@ Testing & Debugging

shell-orchestrator: ## Open shell in orchestrator container
	docker exec -it aegis-orchestrator bash

shell-vehicle: ## Open shell in vehicle container (usage: make shell-vehicle ID=1)
	@if [ -z "$(ID)" ]; then \
		echo "$(YELLOW)Usage: make shell-vehicle ID=<1|2|3>$(NC)"; \
		exit 1; \
	fi
	docker exec -it aegis-vehicle-agent-$(ID) bash

health: ## Check health status of all services
	@echo "$(GREEN)Service Health Status:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps --format json | jq -r '.[] | "\(.Name): \(.Health)"'

test-api: ## Test orchestrator API health
	@echo "$(GREEN)Testing orchestrator API...$(NC)"
	@curl -sf http://localhost:8000/health && echo "$(GREEN)✓ Orchestrator is healthy$(NC)" || echo "$(YELLOW)✗ Orchestrator is not responding$(NC)"

test-redis: ## Test Redis connectivity
	@echo "$(GREEN)Testing Redis connectivity...$(NC)"
	@docker exec aegis-redis redis-cli PING > /dev/null && echo "$(GREEN)✓ Redis is responding$(NC)" || echo "$(YELLOW)✗ Redis is not responding$(NC)"

test-postgres: ## Test PostgreSQL connectivity
	@echo "$(GREEN)Testing PostgreSQL connectivity...$(NC)"
	@docker exec aegis-postgres pg_isready -U aegis_user > /dev/null && echo "$(GREEN)✓ PostgreSQL is ready$(NC)" || echo "$(YELLOW)✗ PostgreSQL is not ready$(NC)"

test-all: test-api test-redis test-postgres ## Test all service connectivity

##@ Documentation

docs: ## Open documentation in browser
	@echo "$(GREEN)Opening documentation...$(NC)"
	@open docker/README.md 2>/dev/null || xdg-open docker/README.md 2>/dev/null || echo "Please open docker/README.md manually"

api-docs: ## Open API documentation
	@echo "$(GREEN)Opening API docs...$(NC)"
	@open http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null || echo "Open http://localhost:8000/docs in your browser"

##@ Environment

env-check: ## Verify .env file exists
	@if [ ! -f .env ]; then \
		echo "$(YELLOW).env file not found. Creating from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN).env created. Please review and update values.$(NC)"; \
	else \
		echo "$(GREEN).env file exists$(NC)"; \
	fi

init: env-check build up ## Initial setup (create .env, build, start)
	@echo "$(GREEN)AEGIS initialization complete!$(NC)"
	@echo "$(BLUE)Access points:$(NC)"
	@echo "  Orchestrator: http://localhost:8000"
	@echo "  Dashboard:    http://localhost:3000"
	@echo ""
	@echo "$(BLUE)Use 'make logs' to view service logs$(NC)"
