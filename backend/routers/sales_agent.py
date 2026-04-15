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


@router.get("/public-status")
async def sales_agent_public_status():
    """Public status check (no auth required)."""
    return {
        "status": "active",
        "version": "1.1.4",
        "apis": {
            "firecrawl": bool(os.environ.get("FIRECRAWL_API_KEY")),
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "hunter": bool(os.environ.get("HUNTER_API_KEY")),
            "instantly": bool(os.environ.get("INSTANTLY_API_KEY")),
        },
    }


CRON_SECRET = os.environ.get("SALES_AGENT_CRON_SECRET", "rivaledge-test-2024")

@router.post("/trigger-cron-public")
async def trigger_sales_agent_cron_public(
    target_count: int = Query(3, ge=1, le=10),
    secret: str = Query(...),
):
    """
    Public endpoint for cron-job.org to trigger sales agent.
    Requires secret key for authentication.
    """
    if secret != CRON_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    return await _run_sales_agent_cron(target_count)

@router.post("/trigger-cron")
async def trigger_sales_agent_cron(
    target_count: int = Query(2, ge=1, le=10),
    current_user: dict = Depends(require_admin),
):
    """
    Manually trigger the sales agent cron job v2 (self-healing).
    Use this to test or run on-demand (admin only).
    """
    return await _run_sales_agent_cron(target_count)

async def _run_sales_agent_cron(target_count: int):
    """Internal function to run the sales agent cron job."""
    import subprocess
    import sys
    
    try:
        # Run the stable cron script (v1 - no tenacity dependency)
        result = subprocess.run(
            [sys.executable, "-m", "cron.sales_agent_cron", str(target_count)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for 10 companies
            cwd="/app"  # Railway app directory
        )
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout[-3000:] if result.stdout else "",  # Last 3000 chars
            "stderr": result.stderr[-1000:] if result.stderr else "",  # Last 1000 chars
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Cron job timed out after 10 minutes",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.post("/test-run")
async def test_sales_agent_run(
    target_count: int = Query(1, ge=1, le=5),
    secret: str = Query(...),
):
    """
    Test endpoint with simple secret key (no Clerk auth required).
    Secret should match SALES_AGENT_TEST_SECRET env var.
    """
    import os
    import subprocess
    import sys
    
    expected_secret = os.environ.get("SALES_AGENT_TEST_SECRET", "")
    if not expected_secret or secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    try:
        # Use the original cron
        result = subprocess.run(
            [sys.executable, "-m", "cron.sales_agent_cron", str(target_count)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd="/app"
        )
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout[-5000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
