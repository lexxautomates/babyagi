#!/bin/bash
# Deploy n8n Workflow to VPS
# Usage: ./deploy_n8n_workflow.sh

N8N_URL="http://31.220.20.251:32770"
API_KEY="eyJzdWIiOiI5ODhmMzhiOS04ZjllLTQwNWYtOWM1Ny05NmYzNTQwYzAwZjgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiYjFjYmZlZGQtNmFkZi00YjM4LTgzNDgtZTZhZjYxNWFhYTY2IiwiaWF0IjoxNzcxNTAyODMwfQ.clEhh0xRoLa7xrK27kEosd1h6oP1q8kXBIlZquu0GXU"
WORKFLOW_FILE="/Users/alexandriajohn/Desktop/babyagi/n8n-workflows/CEO-MCP-Multi-Server-Telegram-VPS.json"

echo "=== n8n Workflow Deployment ==="
echo "Target: $N8N_URL"
echo ""

# Check n8n health
echo "Checking n8n health..."
HEALTH=$(curl -s "$N8N_URL/healthz")
echo "Health: $HEALTH"
echo ""

# Try to list workflows
echo "Attempting to list workflows..."
curl -s -X GET "$N8N_URL/api/v1/workflows" \
  -H "X-N8N-API-KEY: $API_KEY" \
  -H "Accept: application/json" | head -200
echo ""

echo ""
echo "=== Manual Deployment Instructions ==="
echo ""
echo "If API deployment fails, manually import the workflow:"
echo ""
echo "1. Open n8n UI: http://31.220.20.251:32770"
echo "2. Go to: Workflows → Import from File"
echo "3. Upload: $WORKFLOW_FILE"
echo "4. Configure credentials:"
echo "   - Telegram API: bottombih1bot"
echo "   - Supabase: Your project credentials"
echo "5. Activate the workflow"
echo ""
echo "Workflow file location:"
echo "$WORKFLOW_FILE"