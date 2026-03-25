# RivalEdge

AI-powered competitor monitoring for teams of 1–10.

## What it does
- Add competitor URLs → auto-profiled
- Weekly AI digest of what changed (pricing, features, messaging)
- Email delivery every Monday morning
- Battle cards: how to beat each competitor
- $49/mo Solo (3 competitors) | $99/mo Pro (10 competitors)

## Tech Stack
- Backend: FastAPI (Python 3.11) → Railway
- Frontend: Next.js 14 + Tailwind → Vercel
- Database: Supabase (Postgres)
- Auth: Clerk
- AI: Anthropic Claude Sonnet
- Email: Resend
- Payments: Stripe
- Scraping: Playwright + Brave Search API

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cp .env.example .env  # fill in your keys
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local  # fill in your keys
npm run dev
```

## Environment Variables

### Backend (Railway)
See `backend/.env.example` for full list.

### Frontend (Vercel)
See `frontend/.env.local.example` for full list.

## Deployment
- Backend: Railway (auto-deploys from main branch, root: backend/)
- Frontend: Vercel (auto-deploys from main branch, root: frontend/)
