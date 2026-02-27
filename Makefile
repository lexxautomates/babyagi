# n8n Management Commands
# Usage: make <command>

.PHONY: help up down restart logs status export import rebuild clean

# Default: show help
help:
	@echo "n8n Management Commands"
	@echo "======================="
	@echo "make up        - Start all containers"
	@echo "make down      - Stop all containers"
	@echo "make restart   - Restart all containers"
	@echo "make status    - Check container status + recent logs"
	@echo "make logs      - View n8n logs (follow mode)"
	@echo "make export    - Export workflows from n8n"
	@echo "make import    - Import workflows to n8n"
	@echo "make rebuild   - Full rebuild (emergency)"
	@echo "make clean     - Remove unused Docker resources"

# Start containers
up:
	docker compose up -d

# Stop containers
down:
	docker compose down

# Restart containers
restart:
	docker compose restart

# Check status + logs
status:
	docker compose ps && docker compose logs --tail=20 n8n

# View logs (follow mode)
logs:
	docker compose logs -f --tail=100 n8n

# Export workflows
export:
	./scripts/export_workflows.sh

# Import workflows
import:
	./scripts/import_workflows.sh

# Full rebuild
rebuild:
	docker compose down
	docker compose up -d --build

# Clean up Docker
clean:
	docker system prune -f