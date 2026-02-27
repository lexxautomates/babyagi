# n8n with Caddy Reverse Proxy

Automated n8n deployment with SSL via Caddy and Cloudflare DNS.

## Project Structure

```
.
├── .github/workflows/
│   └── deploy-n8n.yml      # GitHub -> VPS Sync
├── workflows/              # Workflow JSON files
├── scripts/
│   ├── import_workflows.sh # CLI Import script
│   └── export_workflows.sh # CLI Export script (Cron)
├── docker-compose.yml      # Main Infrastructure
├── Caddyfile               # Automatic HTTPS/SSL Config
└── .env.example            # Template for your secrets
```

## Quick Start

### 1. Clone & Configure

```bash
git clone <your-repo>
cd babyagi
cp .env.example .env
```

Edit `.env` with your values:
- `N8N_HOST` - Your domain (e.g., `n8n.lexxautomates.com`)
- `CLOUDFLARE_API_TOKEN` - From [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
- `N8N_ENCRYPTION_KEY` - Generate with `openssl rand -hex 32`
- `N8N_API_KEY` - Create in n8n UI after first run

### 2. Deploy

```bash
docker-compose up -d
```

Caddy will automatically:
- Obtain Let's Encrypt SSL certificates
- Configure HTTPS
- Set up proper security headers

### 3. Access n8n

Open `https://n8n.lexxautomates.com` in your browser.

## Workflow Management

### Import Workflows

```bash
./scripts/import_workflows.sh
```

Imports all JSON files from `workflows/` directory to n8n.

### Export Workflows

```bash
./scripts/export_workflows.sh
```

Exports all n8n workflows to `workflows/` directory.

### Automatic Backup (Cron)

Add to crontab for daily backups:

```bash
0 2 * * * /path/to/babyagi/scripts/export_workflows.sh
```

## GitHub Actions Deployment

The workflow `.github/workflows/deploy-n8n.yml` automatically deploys to your VPS on push to `main`.

### Required GitHub Secrets

- `VPS_HOST` - Your VPS IP or hostname
- `VPS_USER` - SSH username
- `VPS_SSH_KEY` - Private SSH key

## Troubleshooting

### Secure Cookie Error

This setup resolves the n8n secure cookie error by:
1. Using HTTPS via Caddy
2. Setting `N8N_SECURE_COOKIE=true`
3. Proper proxy headers in Caddyfile

### Check Logs

```bash
docker-compose logs caddy
docker-compose logs n8n
```

### Restart Services

```bash
docker-compose restart
```

## Security Notes

- Never commit `.env` to version control
- Rotate API keys regularly
- Use strong encryption keys
- Keep Docker images updated