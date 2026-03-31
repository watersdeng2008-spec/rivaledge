"""
RivalEdge FastAPI application entrypoint.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from rate_limit import limiter
from routers import competitors, users, webhooks
from routers import jobs
from routers import digest
from routers import billing
from routers import outreach


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    import logging
    logger = logging.getLogger(__name__)

    # Warn (but don't crash) if env vars are missing — app boots, features degrade gracefully
    warn_if_missing = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "CLERK_JWT_ISSUER",
        "CLERK_PEM_PUBLIC_KEY",
        "ANTHROPIC_API_KEY",
        "RESEND_API_KEY",
        "BRAVE_SEARCH_API_KEY",
    ]
    missing = [v for v in warn_if_missing if not os.getenv(v)]
    if missing:
        logger.warning(
            f"Missing env vars (some features will be degraded): {missing}"
        )

    yield
    # Shutdown: nothing to clean up yet


app = FastAPI(
    title="RivalEdge API",
    description="AI-powered competitor monitoring",
    version="1.0.2",
    lifespan=lifespan,
    redirect_slashes=False,  # Prevent http:// redirects on trailing slash mismatch
)

# Attach limiter to app state (required by slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS — production-ready ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for now — tighten after first users onboarded
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["competitors"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(digest.router, prefix="/api/digest", tags=["digest"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])
# outreach v1.0 — cold email proxy via Railway/Resend


@app.get("/health")
async def health():
    """Health check endpoint for Railway."""
    return {
        "status": "ok",
        "version": "1.0.2",
        "service": "rivaledge-api",
    }
