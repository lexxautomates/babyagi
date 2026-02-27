# n8n Workflows for BabyAGI

Two workflows are available for Telegram integration with BabyAGI.

---

## 1. BabyAGI Telegram Relay

**File**: `BabyAGI-Telegram-Relay.json`

A simple relay that connects Telegram to BabyAGI's API.

### Workflow Flow
```
Telegram Trigger → Check Authorized User → Prepare Request → Call BabyAGI API → Send Response
                           ↓
                    Access Denied
```

### Features
- **User Authorization**: Only Chat ID `7931609486` can use the bot
- **Command Support**: `/start`, `/help`, `/task`, `/functions`
- **API Integration**: Calls BabyAGI at `http://31.220.20.251:8080`
- **Error Handling**: Sends error notifications to admin

### Commands
| Command | Description |
|---------|-------------|
| `/start` | Show welcome message |
| `/help` | Show help |
| `/functions` | List BabyAGI functions |
| `/task <objective>` | Execute a task |
| Any message | Chat with BabyAGI |

---

## 2. CEO MCP Multi-Server Telegram VPS

**File**: `CEO-MCP-Multi-Server-Telegram-VPS.json`

An advanced CEO orchestrator agent that connects to multiple MCP servers.

### Features
- **Telegram Integration**: Uses `@babybih1bot`
- **Ollama LLM**: Connects to VPS at `http://31.220.20.251:11434`
- **MCP Servers**: 4 production MCP servers
- **Security**: User whitelist, rate limiting
- **Audit Logging**: Supabase integration

### MCP Servers Configured

| Server | Port | Description |
|--------|------|-------------|
| local-tools | 8765 | Shell exec, filesystem, HTTP |
| supabase-agent | 8770 | Tasks, finance, memory, POD |
| web-research | 8780 | Reddit, YouTube, news API |
| crypto-tools | 8790 | Binance, TradingView, portfolio |

---

## Deployment Instructions

### Method 1: Import via n8n UI

1. Open n8n: `http://31.220.20.251:32770`
2. Go to **Workflows** → **Import from File**
3. Upload the workflow JSON file
4. Configure credentials:
   - **Telegram API**: Create credential with bot token `8603766271:AAGSfwwlGD2nBpd28UMd1FxMIlkub-BMdjY`
   - **Supabase**: Configure if using audit logging
5. Click **Active** toggle to activate

### Method 2: Import via n8n CLI

```bash
# On the VPS where n8n is running
n8n import:workflow --input=BabyAGI-Telegram-Relay.json
```

### Method 3: Import via API

```bash
curl -X POST http://31.220.20.251:32770/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: YOUR_API_KEY" \
  -d @BabyAGI-Telegram-Relay.json
```

---

## Credentials Setup

### Telegram API Credential
1. In n8n, go to **Credentials** → **Add Credential**
2. Select **Telegram API**
3. Enter:
   - **Name**: `bottombih1bot`
   - **Access Token**: `8603766271:AAGSfwwlGD2nBpd28UMd1FxMIlkub-BMdjY`
4. Save

### Supabase Credential (Optional)
1. Go to **Credentials** → **Add Credential**
2. Select **Supabase**
3. Enter your Supabase project details

---

## Testing

Send a message to `@babybih1bot` on Telegram:
- `/start` - Initialize the bot
- `/help` - Show available commands
- Any message - Processed by BabyAGI

---

## Files

| File | Description |
|------|-------------|
| `BabyAGI-Telegram-Relay.json` | Simple Telegram → BabyAGI relay |
| `CEO-MCP-Multi-Server-Telegram-VPS.json` | Advanced CEO orchestrator with MCP servers |