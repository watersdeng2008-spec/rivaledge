# Camofox Deployment Guide

## Overview
Camofox replaces Apollo.io for LinkedIn lead research. It runs as a separate Docker container.

## Deployment Options

### Option 1: Railway (Recommended)

1. **Add to Railway:**
   ```bash
   cd /Users/openclaw/.openclaw/workspace/rivaledge/services/camofox
   railway link
   railway up
   ```

2. **Set environment variables in Railway dashboard:**
   - `CAMOFOX_API_KEY` — Generate with: `openssl rand -hex 32`
   - `PORT` — 9377

3. **Get public URL:**
   - Railway will provide a public URL like `https://camofox-production.up.railway.app`
   - Add to backend env: `CAMOFOX_URL=https://camofox-production.up.railway.app`

### Option 2: Local Development

```bash
cd /Users/openclaw/.openclaw/workspace/rivaledge/services/camofox
docker-compose up -d
```

Access at: `http://localhost:9377`

### Option 3: Fly.io

```bash
cd /Users/openclaw/.openclaw/workspace/rivaledge/services/camofox
fly deploy
```

## LinkedIn Cookie Setup (Required)

Camofox needs your LinkedIn cookies to scrape profiles.

### 1. Export Cookies from Browser

**Chrome:**
1. Install "cookies.txt" extension
2. Go to linkedin.com and log in
3. Click extension → "Export" → "Netscape format"
4. Save as `linkedin_cookies.txt`

**Firefox:**
1. Install "cookies.txt" extension
2. Go to linkedin.com and log in
3. Export cookies in Netscape format

### 2. Import to Camofox

**Via API:**
```bash
curl -X POST https://your-camofox-url/cookies/import \
  -H "Authorization: Bearer YOUR_CAMOFOX_API_KEY" \
  -H "Content-Type: text/plain" \
  --data-binary @linkedin_cookies.txt
```

**Or via RivalEdge API:**
```bash
curl -X POST https://rivaledge.ai/api/camofox/import-cookies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d "cookie_content=$(cat linkedin_cookies.txt)"
```

## Testing

### Check Status
```bash
curl https://your-camofox-url/health
```

### Test LinkedIn Search
```bash
curl -X POST https://rivaledge.ai/api/camofox/search/linkedin \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "titles": ["VP Product", "CEO"],
    "industries": ["SaaS"],
    "limit": 10
  }'
```

## Cost Comparison

| Tool | Monthly Cost | Notes |
|------|--------------|-------|
| Apollo.io | $59+ | API blocked, not working |
| Evaboot | ~$50 | LinkedIn export only |
| Camofox | $0-5 | Self-hosted, one-time setup |
| **Total Savings** | **~$100/mo** | |

## Troubleshooting

### Camofox not available
- Check if container is running: `docker ps`
- Check health endpoint: `curl http://localhost:9377/health`
- Check Railway logs: `railway logs`

### LinkedIn blocking
- Cookies expired — re-export and re-import
- Too many requests — add delays between scrapes
- Account flagged — use different LinkedIn account

### Rate limits
- LinkedIn has strict rate limits
- Add delays: 5-10 seconds between profile scrapes
- Use proxy rotation for scale (not needed initially)

## Next Steps

1. Deploy Camofox container
2. Export LinkedIn cookies
3. Import cookies to Camofox
4. Test search endpoint
5. Update sales agent to use Camofox instead of Apollo
