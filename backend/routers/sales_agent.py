"""
Sales Agent Router — Autonomous lead research and outreach.

Endpoints:
- POST /admin/sales-agent/run — Run lead research
- GET /admin/sales-agent/status — Check configuration
"""
import os
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import get_current_user
from services.sales_agent.orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sales-agent", tags=["Sales Agent"])

# Admin user IDs (Clerk user IDs)
ADMIN_USER_IDS = [
    "user_3Bh6we4LE9YddryP143qpQsIcoX",  # Waters Deng
]


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin access for sales agent endpoints."""
    user_id = current_user.get("sub", "")
    if user_id not in ADMIN_USER_IDS:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


@router.post("/run")
async def run_sales_agent(
    target_count: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(require_admin),
):
    """
    Run sales agent to research companies and generate personalized emails.
    Called by cron job daily or manually via admin.
    """
    try:
        orch = get_orchestrator()
        
        # Target companies (expand this list as needed)
        targets = [
            {"domain": "anker.com", "industry": "online_retail"},
            {"domain": "belkin.com", "industry": "online_retail"},
            {"domain": "ravpower.com", "industry": "online_retail"},
            {"domain": "aukey.com", "industry": "online_retail"},
            {"domain": "mophie.com", "industry": "online_retail"},
            {"domain": "nonda.co", "industry": "online_retail"},
            {"domain": "zendure.com", "industry": "online_retail"},
            {"domain": "ugreen.com", "industry": "online_retail"},
            {"domain": "baseus.com", "industry": "online_retail"},
            {"domain": "spigen.com", "industry": "online_retail"},
        ][:target_count]
        
        results = []
        for target in targets:
            try:
                result = await orch.process_company(target["domain"], target["industry"])
                results.append({
                    "domain": target["domain"],
                    "status": "success",
                    "decision_makers": len(result.get("decision_makers", [])),
                    "emails": len(result.get("emails", [])),
                })
            except Exception as e:
                logger.error(f"Failed to process {target['domain']}: {e}")
                results.append({
                    "domain": target["domain"],
                    "status": "error",
                    "error": str(e),
                })
        
        return {
            "success": True,
            "processed": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Sales agent run failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sales agent failed: {str(e)}"
        )


@router.get("/status")
async def sales_agent_status(
    current_user: dict = Depends(require_admin),
):
    """Get sales agent status and API configuration."""
    return {
        "status": "active",
        "templates": ["online_retail", "physical_therapy", "saas"],
        "apis": {
            "firecrawl": bool(os.environ.get("FIRECRAWL_API_KEY")),
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "hunter": bool(os.environ.get("HUNTER_API_KEY")),
            "instantly": bool(os.environ.get("INSTANTLY_API_KEY")),
        },
        "targets_available": 10,
    }
