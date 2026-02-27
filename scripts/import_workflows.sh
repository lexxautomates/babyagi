#!/bin/bash

# Import n8n workflows from JSON files using Docker CLI
# Usage: ./scripts/import_workflows.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMPORTS_DIR="$PROJECT_DIR/imports"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Importing workflows to n8n container...${NC}"

# Check if n8n container is running
if ! docker compose ps | grep -q n8n; then
    echo -e "${RED}Error: n8n container is not running${NC}"
    exit 1
fi

# Check if imports directory exists
if [ ! -d "$IMPORTS_DIR" ]; then
    echo -e "${YELLOW}Creating imports directory...${NC}"
    mkdir -p "$IMPORTS_DIR"
fi

# Count workflows
WORKFLOW_COUNT=$(find "$IMPORTS_DIR" -name "*.json" -type f | wc -l)
echo -e "${YELLOW}Found $WORKFLOW_COUNT workflow(s) to import${NC}"

if [ "$WORKFLOW_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}No workflow files found in $IMPORTS_DIR${NC}"
    echo -e "${YELLOW}Add workflow JSON files to ./imports/ directory${NC}"
    exit 0
fi

# Import all workflows using n8n CLI
# The imports directory is mounted to /tmp/n8n_import in the container
docker exec -it -u node n8n n8n import:workflow --separate --input=/tmp/n8n_import

echo -e "${GREEN}Import complete!${NC}"
echo -e "${YELLOW}Note: Imported workflows are inactive by default. Activate them in n8n UI.${NC}"