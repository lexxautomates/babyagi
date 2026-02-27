#!/bin/bash

# Export n8n workflows to JSON files using Docker CLI
# Usage: ./scripts/export_workflows.sh
# Recommended: Run via cron for automatic backups

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
WORKFLOWS_DIR="$PROJECT_DIR/workflows"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create workflows directory if it doesn't exist
mkdir -p "$WORKFLOWS_DIR"

echo -e "${YELLOW}Exporting workflows from n8n container...${NC}"

# Check if n8n container is running
if ! docker compose ps | grep -q n8n; then
    echo -e "${RED}Error: n8n container is not running${NC}"
    exit 1
fi

# Export all workflows using n8n CLI
# The workflows directory is mounted to /home/node/export_dir in the container
docker exec -it -u node n8n n8n export:workflow --all --output=/home/node/export_dir/

# List exported files
echo -e "${GREEN}Exported workflows:${NC}"
ls -la "$WORKFLOWS_DIR"/*.json 2>/dev/null || echo "No workflows found"

# Count workflows
WORKFLOW_COUNT=$(find "$WORKFLOWS_DIR" -name "*.json" -type f | wc -l)
echo -e "${GREEN}Total: $WORKFLOW_COUNT workflow(s) exported to $WORKFLOWS_DIR${NC}"

# Optional: Commit to git
if [ -d "$PROJECT_DIR/.git" ]; then
    echo -e "${YELLOW}Committing changes to git...${NC}"
    cd "$PROJECT_DIR"
    git add workflows/*.json
    git diff --cached --quiet || git commit -m "chore: update workflows [skip ci]"
    echo -e "${GREEN}Changes committed${NC}"
fi