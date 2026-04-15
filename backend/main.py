"""
RivalEdge FastAPI application entrypoint.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from rate_limit import limiter
from routers import competitors, users, webhooks
from routers import jobs
from routers import digest
from routers import billing
from routers import outreach
from routers import feedback
from routers import buffer as buffer_router
from routers import ai_monitor
from routers import sales as sales_router

# Optional routers — log errors but don't crash if they fail
try:
    from routers import ceo_dashboard
    CEO_DASHBOARD_AVAILABLE = True
except Exception as e:
    import logging
    logging.warning(f"CEO dashboard not available: {e}")
    CEO_DASHBOARD_AVAILABLE = False
    ceo_dashboard = None

try:
    from routers import sales_agent
    SALES_AGENT_AVAILABLE = True
except Exception as e:
    import logging
    logging.warning(f"Sales agent not available: {e}")
    SALES_AGENT_AVAILABLE = False
    sales_agent = None

try:
    from routers import sales_analytics
    SALES_ANALYTICS_AVAILABLE = True
except Exception as e:
    import logging
    logging.warning(f"Sales analytics not available: {e}")
    SALES_ANALYTICS_AVAILABLE = False
    sales_analytics = None


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
        "OPENROUTER_API_KEY",
        "RESEND_API_KEY",
        "BRAVE_SEARCH_API_KEY",
        "BUFFER_API_KEY",
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
    version="1.0.3",
    lifespan=lifespan,
    redirect_slashes=False,  # Prevent http:// redirects on trailing slash mismatch
)

# ── CORS — must be added FIRST so it runs on ALL responses including errors ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for now — tighten after first users onboarded
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler — ensures CORS headers on ALL responses including 500s
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.getLogger(__name__).error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}"},
        headers={"Access-Control-Allow-Origin": "*"},
    )

# Attach limiter to app state (required by slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["competitors"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(digest.router, prefix="/api/digest", tags=["digest"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(buffer_router.router, prefix="/api/buffer", tags=["buffer"])
app.include_router(ai_monitor.router, prefix="/api/ai", tags=["ai_monitor"])
app.include_router(sales_router.router, prefix="/api/sales", tags=["sales"])
# Include optional routers only if available
if CEO_DASHBOARD_AVAILABLE and ceo_dashboard:
    app.include_router(ceo_dashboard.router, prefix="/api", tags=["ceo_dashboard"])

if SALES_AGENT_AVAILABLE and sales_agent:
    app.include_router(sales_agent.router, prefix="/api/admin", tags=["sales_agent"])

if SALES_ANALYTICS_AVAILABLE and sales_analytics:
    app.include_router(sales_analytics.router, prefix="/api/admin", tags=["sales_analytics"])
# outreach v1.0 — cold email proxy via Railway/Resend


@app.get("/debug/routers")
async def debug_routers():
    """Debug endpoint to check which routers are loaded."""
    return {
        "ceo_dashboard_available": CEO_DASHBOARD_AVAILABLE,
        "sales_agent_available": SALES_AGENT_AVAILABLE,
        "version": "1.0.8",
    }


@app.get("/health")
async def health():
    """Health check endpoint for Railway."""
    from services.ai import get_cache_stats, get_model_info
    import os
    return {
        "status": "ok",
        "version": "1.3.2",
        "buffer_configured": bool(os.environ.get("BUFFER_API_KEY")),
        "ai_models": get_model_info(),
        "service": "rivaledge-api",
        "ai_cache": get_cache_stats(),
        "ai_model": os.environ.get("AI_MODEL", "moonshotai/kimi-k2.5"),
    }


@app.post("/admin/cache/clear")
async def clear_cache():
    """Clear AI response cache (admin endpoint)."""
    from services.ai import clear_ai_cache
    clear_ai_cache()
    return {"status": "ok", "message": "AI cache cleared"}


@app.get("/admin/cache/stats")
async def cache_stats():
    """Get AI cache statistics."""
    from services.ai import get_cache_stats
    return get_cache_stats()
