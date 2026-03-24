"""
Weekly Digest Cron Job

Runs every Monday at 7am CT via Railway cron.
Scrapes all competitors for all active users, generates digest, and sends.

Idempotent: safe to run multiple times (each run creates a new digest record
but doesn't re-send already-sent digests for the same window).

Usage:
    python -m cron.weekly_digest
    
Railway cron schedule: 0 13 * * 1  (7am CT = 1pm UTC on Mondays)
"""
import os
import sys
import logging
from datetime import datetime, timezone
from typing import Optional

# Ensure backend/ is on the path when run as a script
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

import db.supabase as db
from services.ai import generate_weekly_digest
from services.email import send_digest
from services.differ import diff_snapshots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def _build_competitors_with_diffs(competitors: list[dict]) -> list[dict]:
    """
    For each competitor, fetch latest + prior snapshots and compute diff.
    Returns list of {competitor_name, url, diff_result, current_profile}.
    """
    result = []
    for comp in competitors:
        comp_id = comp["id"]
        latest = db.get_latest_snapshot(comp_id)
        prior = db.get_prior_snapshot(comp_id)
        
        if latest and prior:
            diff_result = diff_snapshots(prior["content"], latest["content"])
        elif latest:
            diff_result = {
                "has_changes": False,
                "changes": [],
                "significance_summary": "none",
            }
        else:
            diff_result = {
                "has_changes": False,
                "changes": [],
                "significance_summary": "none",
            }
        
        current_profile = comp.get("profile") or ""
        if isinstance(current_profile, dict):
            current_profile = str(current_profile)
        
        result.append({
            "competitor_name": comp.get("name") or comp.get("url"),
            "url": comp.get("url"),
            "diff_result": diff_result,
            "current_profile": current_profile,
        })
    
    return result


def process_user(user: dict) -> dict:
    """
    Process a single user: generate and send their weekly digest.
    
    Returns:
        {"user_id": str, "success": bool, "error": Optional[str], "digest_id": Optional[str]}
    """
    user_id = user["id"]
    user_email = user.get("email", "")
    
    logger.info(f"Processing user {user_id} ({user_email})")
    
    try:
        # 1. Get competitors
        competitors = db.get_competitors(user_id)
        if not competitors:
            logger.info(f"User {user_id} has no competitors — skipping")
            return {"user_id": user_id, "success": True, "error": None, "digest_id": None, "skipped": True}
        
        logger.info(f"User {user_id} has {len(competitors)} competitors")
        
        # 2. Build diffs
        competitors_with_diffs = _build_competitors_with_diffs(competitors)
        
        # 3. Generate digest via Claude
        html_content = generate_weekly_digest(user_email, competitors_with_diffs)
        
        # 4. Save digest to DB
        digest_record = db.create_digest(user_id=user_id, content=html_content)
        digest_id = digest_record["id"]
        
        logger.info(f"Digest {digest_id} created for user {user_id}")
        
        # 5. Send email
        from services.email import _extract_subject_from_html
        subject = _extract_subject_from_html(html_content) or "Your RivalEdge Weekly Brief"
        
        sent = send_digest(
            to_email=user_email,
            html_content=html_content,
            subject=subject,
        )
        
        if sent:
            db.mark_digest_sent(digest_id)
            logger.info(f"Digest {digest_id} sent to {user_email}")
        else:
            logger.warning(f"Failed to send digest {digest_id} to {user_email}")
        
        return {
            "user_id": user_id,
            "success": True,
            "error": None,
            "digest_id": digest_id,
            "sent": sent,
            "skipped": False,
        }
    
    except Exception as e:
        logger.error(f"Error processing user {user_id}: {e}", exc_info=True)
        return {
            "user_id": user_id,
            "success": False,
            "error": str(e),
            "digest_id": None,
            "skipped": False,
        }


def run_weekly_digest() -> dict:
    """
    Main entry point for the weekly digest cron job.
    
    Processes all active users, handles errors per-user (one failure
    doesn't stop the rest).
    
    Returns:
        Summary dict: {total_users, success_count, skip_count, error_count, errors: list}
    """
    logger.info("=== RivalEdge Weekly Digest Cron Starting ===")
    started_at = datetime.now(timezone.utc)
    
    # 1. Get all users
    users = db.get_all_active_users()
    total = len(users)
    logger.info(f"Found {total} users to process")
    
    results = []
    errors = []
    success_count = 0
    skip_count = 0
    
    # 2. Process each user — failures are isolated
    for user in users:
        result = process_user(user)
        results.append(result)
        
        if result.get("skipped"):
            skip_count += 1
        elif result["success"]:
            success_count += 1
        else:
            errors.append({
                "user_id": result["user_id"],
                "error": result.get("error"),
            })
    
    # 3. Summary
    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    error_count = len(errors)
    
    summary = {
        "total_users": total,
        "success_count": success_count,
        "skip_count": skip_count,
        "error_count": error_count,
        "errors": errors,
        "elapsed_seconds": elapsed,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    
    logger.info(
        f"=== Cron Complete === "
        f"{success_count}/{total} succeeded, "
        f"{skip_count} skipped, "
        f"{error_count} errors in {elapsed:.1f}s"
    )
    
    if errors:
        logger.warning(f"Errors: {errors}")
    
    return summary


if __name__ == "__main__":
    summary = run_weekly_digest()
    print(f"\nSummary: {summary}")
    # Exit with error code if any failures
    if summary["error_count"] > 0:
        sys.exit(1)
