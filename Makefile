# Makefile for ChatBot Project
# Makes deployment commands shorter and more convenient

.PHONY: help install deploy start stop restart status logs clean init-kb backup

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "ChatBot Project - Make Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install system dependencies (requires sudo)
	@echo "Installing dependencies..."
	@sudo ./deploy.sh install_dependencies

deploy: ## Full deployment of the system
	@./deploy.sh deploy

start: ## Start all services
	@./deploy.sh start

stop: ## Stop all services
	@./deploy.sh stop

restart: ## Restart all services
	@./deploy.sh restart

status: ## Show status of all services
	@./deploy.sh status

logs: ## Show logs (use: make logs SERVICE=agent1_student)
	@if [ -z "$(SERVICE)" ]; then \
		./deploy.sh logs; \
	else \
		./deploy.sh logs $(SERVICE); \
	fi

init-kb: ## Initialize/refresh knowledge base
	@./deploy.sh init-kb

clean: ## Remove all containers and volumes (WARNING: deletes data!)
	@./deploy.sh cleanup

# Convenience aliases
up: start ## Alias for 'start'

down: stop ## Alias for 'stop'

ps: status ## Alias for 'status'

# Service-specific logs shortcuts
logs-agent1: ## Show Agent1 logs
	@./deploy.sh logs agent1_student

logs-qdrant: ## Show Qdrant logs
	@./deploy.sh logs qdrant

logs-ollama: ## Show Ollama logs
	@./deploy.sh logs ollama

logs-nodered: ## Show Node-RED logs
	@./deploy.sh logs node-red

# Development shortcuts
dev-agent1: ## Start only Agent1 and dependencies
	@docker compose up -d qdrant ollama node-red agent1_student

dev-stop: ## Stop development services
	@docker compose stop agent1_student node-red

# Backup shortcuts
backup: ## Create backup of all volumes
	@echo "Creating backups..."
	@mkdir -p backups
	@docker run --rm -v qdrant_data:/data -v $$(pwd)/backups:/backup \
		ubuntu tar czf /backup/qdrant-backup-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@docker run --rm -v ollama_data:/data -v $$(pwd)/backups:/backup \
		ubuntu tar czf /backup/ollama-backup-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@docker run --rm -v nodered_data:/data -v $$(pwd)/backups:/backup \
		ubuntu tar czf /backup/nodered-backup-$$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "Backups created in ./backups/"

# Quick health checks
health: ## Quick health check of all services
	@echo "Checking service health..."
	@curl -sf http://localhost:8001/health && echo "✓ Agent1: OK" || echo "✗ Agent1: FAIL"
	@curl -sf http://localhost:6333/health && echo "✓ Qdrant: OK" || echo "✗ Qdrant: FAIL"
	@curl -sf http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama: OK" || echo "✗ Ollama: FAIL"
	@curl -sf http://localhost:1880/ > /dev/null && echo "✓ Node-RED: OK" || echo "✗ Node-RED: FAIL"

# Test queries
test-query: ## Send a test query to Agent1
	@curl -X POST http://localhost:8001/api/chat \
		-H "Content-Type: application/json" \
		-d '{"message": "Jakie stypendia są dostępne?", "conversation_id": "test123"}' \
		| python3 -m json.tool

test-qdrant: ## Test Qdrant connection
	@curl -s http://localhost:6333/collections | python3 -m json.tool

test-ollama: ## Test Ollama models
	@docker exec ollama ollama list
