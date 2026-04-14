"""
Sales Agent Analytics Router

Track performance and optimize tactics based on conversion data.
"""
import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user
from db.supabase import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sales-analytics", tags=["Sales Analytics"])

# Admin user IDs
ADMIN_USER_IDS = [
    "user_3Bh6we4LE9YddryP143qpQsIcoX",  # Waters Deng
]


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin access."""
    user_id = current_user.get("sub", "")
    if user_id not in ADMIN_USER_IDS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/performance")
async def get_performance(
    days: int = Query(30, ge=1, le=90),
    current_user: dict = Depends(require_admin),
):
    """
    Get sales agent performance metrics.
    
    Returns:
    - Total leads generated
    - Emails sent
    - Reply rates by industry
    - Best performing templates
    """
    supabase = get_supabase()
    
    # Get recent runs
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    logs_result = supabase.table("sales_agent_logs").select("*").gte("started_at", since).execute()
    logs = logs_result.data or []
    
    # Get leads
    leads_result = supabase.table("sales_leads").select("*").gte("created_at", since).execute()
    leads = leads_result.data or []
    
    # Calculate metrics
    total_companies = sum(log.get("companies_processed", 0) for log in logs)
    total_decision_makers = sum(log.get("decision_makers_found", 0) for log in logs)
    total_emails_generated = sum(log.get("emails_generated", 0) for log in logs)
    
    # By industry
    by_industry = {}
    for lead in leads:
        industry = lead.get("industry", "unknown")
        if industry not in by_industry:
            by_industry[industry] = {"sent": 0, "replies": 0}
        by_industry[industry]["sent"] += 1
        if lead.get("status") in ["replied", "positive"]:
            by_industry[industry]["replies"] += 1
    
    # Calculate reply rates
    for industry in by_industry:
        sent = by_industry[industry]["sent"]
        replies = by_industry[industry]["replies"]
        by_industry[industry]["reply_rate"] = round(replies / sent * 100, 2) if sent > 0 else 0
    
    return {
        "period_days": days,
        "total_runs": len(logs),
        "total_companies_processed": total_companies,
        "total_decision_makers_found": total_decision_makers,
        "total_emails_generated": total_emails_generated,
        "total_leads_in_system": len(leads),
        "by_industry": by_industry,
        "recommendations": generate_recommendations(by_industry),
    }


def generate_recommendations(by_industry: dict) -> list:
    """Generate actionable recommendations based on performance."""
    recommendations = []
    
    if not by_industry:
        recommendations.append("No data yet. Let the sales agent run for a few days.")
        return recommendations
    
    # Find best performing industry
    best_industry = max(by_industry.items(), key=lambda x: x[1].get("reply_rate", 0))
    worst_industry = min(by_industry.items(), key=lambda x: x[1].get("reply_rate", 0))
    
    if best_industry[1]["reply_rate"] > 10:
        recommendations.append(
            f"🎯 DOUBLE DOWN: {best_industry[0]} shows {best_industry[1]['reply_rate']}% reply rate. "
            "Add more companies in this sector."
        )
    
    if worst_industry[1]["reply_rate"] < 5 and worst_industry[1]["sent"] > 10:
        recommendations.append(
            f"⚠️ EXAMINE: {worst_industry[0]} only {worst_industry[1]['reply_rate']}% reply rate "
            "despite {worst_industry[1]['sent']} emails. Consider changing tactics or pausing."
        )
    
    # General recommendations
    avg_reply_rate = sum(i.get("reply_rate", 0) for i in by_industry.values()) / len(by_industry)
    if avg_reply_rate < 5:
        recommendations.append(
            "📉 Overall reply rate is low. Consider: A/B testing subject lines, "
            "personalizing more deeply, or targeting different company sizes."
        )
    elif avg_reply_rate > 15:
        recommendations.append(
            "🚀 Strong performance! Scale up the daily target count."
        )
    
    return recommendations


@router.get("/recent-leads")
async def get_recent_leads(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin),
):
    """Get recent leads with optional status filter."""
    supabase = get_supabase()
    
    query = supabase.table("sales_leads").select("*").order("created_at", desc=True).limit(limit)
    
    if status:
        query = query.eq("status", status)
    
    result = query.execute()
    
    return {
        "leads": result.data or [],
        "count": len(result.data or []),
    }


@router.post("/update-lead-status")
async def update_lead_status(
    lead_id: str,
    status: str,  # new, sent, replied, bounced, unsubscribed, positive
    reply_content: Optional[str] = None,
    current_user: dict = Depends(require_admin),
):
    """Update lead status (called by Instantly webhook)."""
    supabase = get_supabase()
    
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    if status == "replied" and reply_content:
        update_data["reply_received_at"] = datetime.utcnow().isoformat()
        update_data["reply_content"] = reply_content
    
    result = supabase.table("sales_leads").update(update_data).eq("id", lead_id).execute()
    
    return {"success": True, "lead": result.data[0] if result.data else None}


@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(require_admin),
):
    """Get complete sales agent dashboard."""
    supabase = get_supabase()
    
    # Last 7 days
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    # Recent runs
    runs_result = supabase.table("sales_agent_logs").select("*").gte("started_at", week_ago).order("started_at", desc=True).execute()
    
    # Recent replies
    replies_result = supabase.table("sales_leads").select("*").in_("status", ["replied", "positive"]).order("reply_received_at", desc=True).limit(10).execute()
    
    # Performance by template
    performance_result = supabase.table("sales_performance").select("*").order("reply_rate", desc=True).execute()
    
    return {
        "recent_runs": runs_result.data or [],
        "recent_replies": replies_result.data or [],
        "template_performance": performance_result.data or [],
        "summary": {
            "runs_this_week": len(runs_result.data or []),
            "replies_this_week": len(replies_result.data or []),
        }
    }
