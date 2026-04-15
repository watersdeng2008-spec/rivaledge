"""
CEO Dashboard — Overview of RivalEdge business metrics.

Shows:
- User registrations (completed and incomplete)
- Revenue metrics
- Sales pipeline
- Key growth metrics
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user
from services.sales_db import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ceo", tags=["CEO Dashboard"])

# Admin user IDs (Clerk user IDs)
ADMIN_USER_IDS = [
    "user_3Bh6we4LE9YddryP143qpQsIcoX",  # Waters Deng
]


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin access for CEO dashboard endpoints."""
    user_id = current_user.get("sub", "")
    if user_id not in ADMIN_USER_IDS:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


# ── Pydantic Models ───────────────────────────────────────────────────────────

class UserRegistration(BaseModel):
    id: str
    email: str
    name: Optional[str]
    company: Optional[str]
    plan: str
    status: str  # "completed", "incomplete", "trial", "subscribed"
    created_at: datetime
    completed_at: Optional[datetime]
    last_activity: Optional[datetime]
    signup_source: Optional[str]
    
    class Config:
        from_attributes = True


class RegistrationStats(BaseModel):
    total_registrations: int
    completed_signups: int
    incomplete_signups: int
    trial_users: int
    paying_customers: int
    conversion_rate: float
    period_days: int


class CEODashboardData(BaseModel):
    registrations: RegistrationStats
    recent_signups: List[UserRegistration]
    incomplete_signups: List[UserRegistration]
    revenue_metrics: Dict[str, Any]
    sales_pipeline: Dict[str, Any]


# ── Helper Functions ─────────────────────────────────────────────────────────

def get_supabase_client():
    """Get Supabase client."""
    return get_supabase()


# ── Dashboard Endpoints ──────────────────────────────────────────────────────

@router.get("/dashboard", response_model=CEODashboardData)
def get_ceo_dashboard(
    days: int = Query(30, ge=1, le=90, description="Analysis period in days"),
    current_user: dict = Depends(require_admin),
):
    """
    Get CEO dashboard with all key metrics.
    
    Shows user registrations, revenue, sales pipeline, and growth metrics.
    """
    try:
        supabase = get_supabase_client()
        
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get user registrations
        registrations = _get_registrations(supabase, start_date)
        
        # Get revenue metrics
        revenue = _get_revenue_metrics(supabase, start_date)
        
        # Get sales pipeline
        pipeline = _get_sales_pipeline(supabase)
        
        # Get sales agent data
        sales_agent = _get_sales_agent_data(supabase)
        
        # Get daily report
        daily_report = _get_daily_report_data(supabase)
        
        return CEODashboardData(
            registrations=registrations["stats"],
            recent_signups=registrations["completed"][:10],
            incomplete_signups=registrations["incomplete"][:10],
            revenue_metrics=revenue,
            sales_pipeline=pipeline,
            sales_agent=sales_agent,
            daily_report=daily_report,
        )
        
    except Exception as e:
        logger.error(f"Failed to get CEO dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registrations", response_model=RegistrationStats)
def get_registration_stats(
    days: int = Query(30, ge=1, le=90),
    current_user: dict = Depends(require_admin),
):
    """
    Get user registration statistics.
    
    Returns counts of completed, incomplete, trial, and paying users.
    """
    try:
        supabase = get_supabase_client()
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        registrations = _get_registrations(supabase, start_date)
        return registrations["stats"]
        
    except Exception as e:
        logger.error(f"Failed to get registration stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registrations/recent")
def get_recent_registrations(
    status: Optional[str] = Query(None, description="Filter by status: completed, incomplete, trial, subscribed"),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin),
):
    """
    Get recent user registrations.
    
    Optional filter by status. Shows most recent first.
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("users").select("*").order("created_at", desc=True).limit(limit)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "count": len(result.data),
            "users": result.data,
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent registrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registrations/incomplete")
def get_incomplete_registrations(
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_admin),
):
    """
    Get users who started but didn't complete registration.
    
    Shows users with incomplete profiles or who abandoned signup.
    """
    try:
        supabase = get_supabase_client()
        
        # Users who created account but haven't completed onboarding
        # or haven't added payment method
        result = supabase.table("users")\
            .select("*")\
            .or_("onboarding_completed.eq.false,payment_method_added.eq.false")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "count": len(result.data),
            "users": result.data,
        }
        
    except Exception as e:
        logger.error(f"Failed to get incomplete registrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
def get_revenue_metrics(
    days: int = Query(30, ge=1, le=90),
    current_user: dict = Depends(require_admin),
):
    """
    Get revenue metrics.
    
    Returns MRR, new revenue, churn, and growth rate.
    """
    try:
        supabase = get_supabase_client()
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        metrics = _get_revenue_metrics(supabase, start_date)
        
        return {
            "success": True,
            "metrics": metrics,
        }
        
    except Exception as e:
        logger.error(f"Failed to get revenue metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/pipeline")
def get_sales_pipeline_summary(
    current_user: dict = Depends(require_admin),
):
    """
    Get sales pipeline summary.
    
    Shows leads by stage and conversion rates.
    """
    try:
        supabase = get_supabase_client()
        pipeline = _get_sales_pipeline(supabase)
        
        return {
            "success": True,
            "pipeline": pipeline,
        }
        
    except Exception as e:
        logger.error(f"Failed to get sales pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-report")
def get_daily_report(
    current_user: dict = Depends(require_admin),
):
    """
    Get daily summary report for CEO review.
    
    Formatted for quick morning review.
    """
    try:
        supabase = get_supabase_client()
        
        # Yesterday's date
        yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
        today = datetime.utcnow().date().isoformat()
        
        # New signups yesterday
        new_users = supabase.table("users")\
            .select("*")\
            .gte("created_at", yesterday)\
            .lt("created_at", today)\
            .execute()
        
        # New leads
        new_leads = supabase.table("leads")\
            .select("*")\
            .gte("created_at", yesterday)\
            .lt("created_at", today)\
            .execute()
        
        # Email engagement
        email_engagement = supabase.table("email_sequences")\
            .select("*")\
            .gte("created_at", yesterday)\
            .lt("created_at", today)\
            .execute()
        
        replies = [e for e in email_engagement.data if e.get("replied_at")]
        
        report = {
            "date": yesterday,
            "new_signups": len(new_users.data),
            "new_leads": len(new_leads.data),
            "emails_sent": len(email_engagement.data),
            "email_replies": len(replies),
            "hot_leads": len(replies),  # Replies = hot leads
        }
        
        return {
            "success": True,
            "report": report,
        }
        
    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Internal Helper Functions ────────────────────────────────────────────────

def _get_registrations(supabase, start_date: str) -> Dict:
    """Get user registration data."""
    
    # Get all users created since start_date
    result = supabase.table("users")\
        .select("*")\
        .gte("created_at", start_date)\
        .execute()
    
    users = result.data or []
    
    # Categorize users
    completed = [u for u in users if u.get("onboarding_completed", True)]
    incomplete = [u for u in users if not u.get("onboarding_completed", False)]
    trial = [u for u in users if u.get("subscription_status") == "trial"]
    paying = [u for u in users if u.get("subscription_status") == "active"]
    
    # Calculate conversion rate
    total = len(users)
    conversion_rate = (len(paying) / total * 100) if total > 0 else 0
    
    return {
        "stats": RegistrationStats(
            total_registrations=total,
            completed_signups=len(completed),
            incomplete_signups=len(incomplete),
            trial_users=len(trial),
            paying_customers=len(paying),
            conversion_rate=round(conversion_rate, 2),
            period_days=30,
        ),
        "completed": completed,
        "incomplete": incomplete,
    }


def _get_revenue_metrics(supabase, start_date: str) -> Dict[str, Any]:
    """Get revenue metrics."""
    
    # Get subscriptions
    subs = supabase.table("subscriptions")\
        .select("*")\
        .execute()
    
    subscriptions = subs.data or []
    
    # Calculate MRR
    active_subs = [s for s in subscriptions if s.get("status") == "active"]
    mrr = sum(s.get("amount", 0) for s in active_subs)
    
    # New subscriptions in period
    new_subs = [s for s in subscriptions if s.get("created_at", "") >= start_date]
    new_revenue = sum(s.get("amount", 0) for s in new_subs)
    
    return {
        "mrr": mrr,
        "mrr_formatted": f"${mrr:,.2f}",
        "active_subscriptions": len(active_subs),
        "new_subscriptions_period": len(new_subs),
        "new_revenue_period": new_revenue,
        "new_revenue_formatted": f"${new_revenue:,.2f}",
    }


def _get_sales_pipeline(supabase) -> Dict[str, Any]:
    """Get sales pipeline data."""
    
    # Get leads by status
    result = supabase.table("leads").select("*").execute()
    leads = result.data or []
    
    # Count by status
    by_status = {}
    for lead in leads:
        status = lead.get("status", "new")
        by_status[status] = by_status.get(status, 0) + 1
    
    # Get recent activity
    recent_emails = supabase.table("personalized_emails")\
        .select("*")\
        .order("created_at", desc=True)\
        .limit(10)\
        .execute()
    
    return {
        "total_leads": len(leads),
        "by_status": by_status,
        "recent_emails": len(recent_emails.data),
    }


def _get_sales_agent_data(supabase) -> Dict[str, Any]:
    """Get sales agent performance data."""
    
    # Get recent runs
    runs = supabase.table("sales_agent_logs")\
        .select("*")\
        .order("started_at", desc=True)\
        .limit(5)\
        .execute()
    
    # Get today's stats (last 24 hours)
    today = (datetime.utcnow() - timedelta(days=1)).isoformat()
    today_runs = supabase.table("sales_agent_logs")\
        .select("*")\
        .gte("started_at", today)\
        .execute()
    
    today_stats = {
        "companies": sum(r.get("companies_processed", 0) for r in today_runs.data),
        "decision_makers": sum(r.get("decision_makers_found", 0) for r in today_runs.data),
        "emails_sent": sum(r.get("emails_added_to_instantly", 0) for r in today_runs.data),
    }
    
    return {
        "recent_runs": runs.data[:5] if runs.data else [],
        "today_stats": today_stats,
    }


def _get_daily_report_data(supabase) -> Dict[str, Any]:
    """Get yesterday's daily report data."""
    
    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    today = datetime.utcnow().date().isoformat()
    
    # New signups yesterday
    new_users = supabase.table("users")\
        .select("*")\
        .gte("created_at", yesterday)\
        .lt("created_at", today)\
        .execute()
    
    # New leads
    new_leads = supabase.table("leads")\
        .select("*")\
        .gte("created_at", yesterday)\
        .lt("created_at", today)\
        .execute()
    
    # Email engagement
    email_engagement = supabase.table("email_sequences")\
        .select("*")\
        .gte("created_at", yesterday)\
        .lt("created_at", today)\
        .execute()
    
    replies = [e for e in email_engagement.data if e.get("replied_at")]
    
    return {
        "date": yesterday,
        "new_signups": len(new_users.data),
        "new_leads": len(new_leads.data),
        "emails_sent": len(email_engagement.data),
        "email_replies": len(replies),
        "hot_leads": len(replies),
    }
