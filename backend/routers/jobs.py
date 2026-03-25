"""
Jobs router — background scraping endpoints.

POST /api/jobs/scrape/{competitor_id}  — scrape a single competitor
POST /api/jobs/scrape-all              — scrape all competitors for the user
"""
import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth import get_current_user
from rate_limit import limiter
import db.supabase as db
from services.scraper import scrape_url
from services.differ import diff_snapshots

logger = logging.getLogger(__name__)
router = APIRouter()


# ── DB helpers (thin wrappers for easy mocking in tests) ──────────────────────

def get_competitor_for_user(competitor_id: str, user_id: str) -> Optional[dict]:
    """Fetch a competitor by ID, scoped to the authenticated user."""
    client = db.get_client()
    result = (
        client.table("competitors")
        .select("*")
        .eq("id", competitor_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return result.data


def get_user_competitors(user_id: str) -> list[dict]:
    """Fetch all competitors for a user."""
    return db.get_competitors(user_id)


def get_latest_snapshot(competitor_id: str) -> Optional[dict]:
    """Fetch the most recent snapshot for a competitor."""
    return db.get_latest_snapshot(competitor_id)


def save_snapshot(competitor_id: str, content: dict, diff: Optional[dict] = None) -> dict:
    """Save a new snapshot to Supabase."""
    return db.create_snapshot(competitor_id, content, diff)


# ── Scrape single competitor ───────────────────────────────────────────────────

@router.post("/scrape/{competitor_id}")
async def scrape_competitor(
    competitor_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Scrape a single competitor and save a snapshot.

    Returns:
        {"snapshot_id": str, "changes": diff_result}
    """
    user_id = current_user["sub"]

    # Verify the competitor belongs to this user
    competitor = get_competitor_for_user(competitor_id, user_id)
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competitor {competitor_id} not found",
        )

    url = competitor["url"]

    # Scrape
    try:
        new_content = await scrape_url(url)
    except Exception as e:
        logger.error(f"Scrape failed for {url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to scrape {url}: {str(e)}",
        )

    # Diff against previous snapshot
    previous = get_latest_snapshot(competitor_id)
    if previous:
        old_content = previous.get("content", {})
        diff_result = diff_snapshots(old_content, new_content)
    else:
        diff_result = {
            "has_changes": True,
            "changes": [],
            "summary": "Initial snapshot — no previous data to compare.",
        }

    # Save snapshot
    try:
        snapshot = save_snapshot(
            competitor_id=competitor_id,
            content=new_content,
            diff=diff_result,
        )
    except Exception as e:
        logger.error(f"Failed to save snapshot for {competitor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save snapshot: {str(e)}",
        )

    return {
        "snapshot_id": snapshot["id"],
        "changes": diff_result,
    }


# ── Scrape all competitors ─────────────────────────────────────────────────────

@router.post("/scrape-all")
@limiter.limit("10/hour")
async def scrape_all_competitors(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Scrape all competitors for the authenticated user concurrently.

    Returns:
        {"scraped": int, "failed": int, "results": list}
    """
    user_id = current_user["sub"]
    competitors = get_user_competitors(user_id)

    if not competitors:
        return {"scraped": 0, "failed": 0, "results": []}

    async def scrape_one(competitor: dict) -> dict:
        cid = competitor["id"]
        url = competitor["url"]
        try:
            new_content = await scrape_url(url)
            previous = get_latest_snapshot(cid)
            if previous:
                diff_result = diff_snapshots(previous.get("content", {}), new_content)
            else:
                diff_result = {
                    "has_changes": True,
                    "changes": [],
                    "summary": "Initial snapshot.",
                }
            snapshot = save_snapshot(cid, new_content, diff_result)
            return {
                "competitor_id": cid,
                "url": url,
                "status": "ok",
                "snapshot_id": snapshot["id"],
                "has_changes": diff_result["has_changes"],
            }
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return {
                "competitor_id": cid,
                "url": url,
                "status": "error",
                "error": str(e),
            }

    results = await asyncio.gather(*[scrape_one(c) for c in competitors])

    scraped = sum(1 for r in results if r.get("status") == "ok")
    failed = sum(1 for r in results if r.get("status") == "error")

    return {
        "scraped": scraped,
        "failed": failed,
        "results": list(results),
    }
