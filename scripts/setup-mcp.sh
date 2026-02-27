#!/bin/bash

# CEO MCP Suite Setup Script
# Run this on your VPS to install MCP tools

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== CEO MCP Suite Setup ===${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo -e "${GREEN}Node.js already installed: $(node --version)${NC}"
fi

# Install MCP CLI
echo -e "${YELLOW}Installing MCP CLI...${NC}"
if ! command -v mcp &> /dev/null; then
    curl -sSL https://raw.githubusercontent.com/modelcontextprotocol/quickstart/main/install.sh | bash
else
    echo -e "${GREEN}MCP CLI already installed${NC}"
fi

# Initialize the CEO context nodes
echo -e "${YELLOW}Installing MCP servers...${NC}"

# Local tools server
echo -e "${YELLOW}Installing local-tools on port 8765...${NC}"
mcp install local-tools --port 8765 || echo -e "${YELLOW}local-tools may already be installed${NC}"

# Supabase agent
echo -e "${YELLOW}Installing supabase-agent on port 8770...${NC}"
mcp install supabase-agent --port 8770 || echo -e "${YELLOW}supabase-agent may already be installed${NC}"

# Web research
echo -e "${YELLOW}Installing web-research on port 8780...${NC}"
mcp install web-research --port 8780 || echo -e "${YELLOW}web-research may already be installed${NC}"

echo ""
echo -e "${GREEN}=== MCP Suite Setup Complete ===${NC}"
echo ""
echo "Installed MCP servers:"
echo "  - local-tools:    http://localhost:8765"
echo "  - supabase-agent: http://localhost:8770"
echo "  - web-research:   http://localhost:8780"
echo ""
echo "Next: Configure n8n to connect to these MCP servers"