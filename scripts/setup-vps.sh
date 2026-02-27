#!/bin/bash

# VPS Setup Script - Run this on your VPS first
# Usage: ./scripts/setup-vps.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== VPS Setup for n8n ===${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt-get update

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. You may need to log out and back in for group changes to take effect.${NC}"
else
    echo -e "${GREEN}Docker already installed${NC}"
fi

# Install Docker Compose if not present
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo apt-get install -y docker-compose-plugin
else
    echo -e "${GREEN}Docker Compose already installed${NC}"
fi

# Install Git if not present
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Installing Git...${NC}"
    sudo apt-get install -y git
else
    echo -e "${GREEN}Git already installed${NC}"
fi

# Install Make if not present
if ! command -v make &> /dev/null; then
    echo -e "${YELLOW}Installing Make...${NC}"
    sudo apt-get install -y make
else
    echo -e "${GREEN}Make already installed${NC}"
fi

# Create project directory
echo -e "${YELLOW}Creating project directory...${NC}"
mkdir -p ~/n8n
mkdir -p ~/n8n/imports
mkdir -p ~/n8n/workflows

# Set permissions for n8n imports (n8n runs as user 1000)
sudo chown -R 1000:1000 ~/n8n/imports
sudo chown -R 1000:1000 ~/n8n/workflows

# Open firewall ports
echo -e "${YELLOW}Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 22/tcp
    echo -e "${GREEN}Firewall ports 80, 443, 22 opened${NC}"
else
    echo -e "${YELLOW}ufw not found. Make sure ports 80 and 443 are open on your firewall.${NC}"
fi

echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo "Installed:"
echo "  - Docker: $(docker --version)"
echo "  - Docker Compose: $(docker compose version)"
echo "  - Git: $(git --version)"
echo "  - Make: $(make --version | head -1)"
echo ""
echo "Next steps:"
echo "  1. Clone your repo: cd ~/n8n && git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git ."
echo "  2. Copy .env: cp .env.example .env"
echo "  3. Edit .env: nano .env"
echo "  4. Start: docker compose up -d"