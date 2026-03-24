# RivalEdge

**AI-powered competitor monitoring SaaS** — built by DengAI / Aether Holding LLC.

Track competitor websites, get daily AI-generated digests, and stay ahead of the market.

## Stack

- **Backend:** FastAPI (Python 3.11)
- **Database:** Supabase (Postgres)
- **Auth:** Clerk (JWT validation)
- **Hosting:** Railway
- **Frontend:** Next.js 14 + Tailwind (Day 5)
- **AI:** Anthropic Claude Sonnet
- **Scraping:** Playwright + Brave Search API fallback
- **Email:** Resend
- **Payments:** Stripe

## Getting Started

### Prerequisites

- Python 3.11+
- Supabase project
- Clerk application
- Railway account

### Local Dev

```bash
cd backend
cp .env.example .env
# Fill in your env vars
pip install -r requirements.txt
uvicorn main:app --reload
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Deploy to Railway

```bash
railway up
```

## Environment Variables

See `backend/.env.example` for required variables.

## Schema

See `backend/db/schema.sql` for Supabase schema.

## Day 1 Status: ✅ Scaffolded

- [x] FastAPI backend structure
- [x] Supabase schema (SQL)
- [x] Clerk JWT validation middleware
- [x] Railway Dockerfile + railway.toml
- [x] TDD test suite
- [ ] GitHub repo (needs manual setup — see below)

## Manual Setup Required

1. **GitHub:** Create repo `rivaledge` under `watersdeng2008-spec` and push
2. **Supabase:** Create project, run `backend/db/schema.sql`
3. **Clerk:** Create application, get publishable key + secret key
4. **Railway:** Link repo, set env vars
5. **Resend:** Get API key for email delivery
6. **Stripe:** Get API keys for payments
