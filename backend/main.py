"""
RivalEdge FastAPI application entrypoint.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import competitors, users, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # On startup: verify required env vars are set
    required = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "CLERK_JWT_ISSUER",
        "CLERK_PEM_PUBLIC_KEY",
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {missing}")
    yield
    # Shutdown: nothing to clean up yet


app = FastAPI(
    title="RivalEdge API",
    description="AI-powered competitor monitoring",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(competitors.router, prefix="/api/competitors", tags=["competitors"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


@app.get("/health")
def health():
    """Health check endpoint for Railway."""
    return {"status": "ok", "service": "rivaledge-api"}
