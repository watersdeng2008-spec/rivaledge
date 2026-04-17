"""
CEO Dashboard — Overview of RivalEdge business metrics.

Shows:
- User registrations (completed and incomplete)
- Revenue metrics
- Sales pipeline
- Key growth metrics
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from auth import get_current_user
from db.supabase import (
    get_users_since,
    get_subscriptions,
    get_leads,
    get_email_sequences,
    get_personalized_emails,
    get_sales_agent_logs,
)

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


def require_admin_or_api_key(
    current_user: dict = Depends(get_current_user),
    api_key: str = Query(None),
) -> dict:
    """Require admin access OR valid API key (for Google Apps Script)."""
    expected_api_key = os.environ.get("CEO_DASHBOARD_API_KEY", "")
    if api_key and expected_api_key and api_key == expected_api_key:
        return {"sub": "api_key_access", "api_access": True}

    return require_admin(current_user)


# ── Pydantic Models ───────────────────────────────────────────────────────────

class UserRegistration(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    plan: str
    status: str  # "completed", "incomplete", "trial", "subscribed"
    created_at: datetime
    completed_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    signup_source: Optional[str] = None

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
    recent_signups: List[Dict[str, Any]]
    incomplete_signups: List[Dict[str, Any]]
    revenue_metrics: Dict[str, Any]
    sales_pipeline: Dict[str, Any]


# ── Dashboard Endpoints ──────────────────────────────────────────────────────

@router.get("/dashboard", response_model=CEODashboardData)
def get_ceo_dashboard(
    days: int = Query(30, ge=1, le=90, description="Analysis period in days"),
    current_user: dict = Depends(require_admin_or_api_key),
):
    """
    Get CEO dashboard with all key metrics.

    Shows user registrations, revenue, sales pipeline, and growth metrics.
    """
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        registrations = _get_registrations(start_date, days)
        revenue = _get_revenue_metrics(start_date)
        pipeline = _get_sales_pipeline()

        return CEODashboardData(
            registrations=registrations["stats"],
            recent_signups=registrations["completed"][:10],
            incomplete_signups=registrations["incomplete"][:10],
            revenue_metrics=revenue,
            sales_pipeline=pipeline,
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
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        registrations = _get_registrations(start_date, days)
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
        users = get_users_since(limit=limit)

        if status:
            users = [u for u in users if u.get("status") == status]

        return {
            "success": True,
            "count": len(users),
            "users": users,
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
        users = get_users_since(limit=limit)

        # Users who haven't completed onboarding or haven't added a payment method
        incomplete = [
            u for u in users
            if not u.get("onboarding_completed", False) or not u.get("payment_method_added", False)
        ]

        return {
            "success": True,
            "count": len(incomplete),
            "users": incomplete,
        }

    except Exception as e:
        logger.error(f"Failed to get incomplete registrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
def get_revenue_metrics_endpoint(
    days: int = Query(30, ge=1, le=90),
    current_user: dict = Depends(require_admin),
):
    """
    Get revenue metrics.

    Returns MRR, new revenue, churn, and growth rate.
    """
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        metrics = _get_revenue_metrics(start_date)

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
        pipeline = _get_sales_pipeline()

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
        yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
        today = datetime.utcnow().date().isoformat()

        new_users = get_users_since(since=yesterday, until=today)
        new_leads = get_leads(since=yesterday, until=today)
        email_engagement = get_email_sequences(since=yesterday, until=today)

        replies = [e for e in email_engagement if e.get("replied_at")]

        report = {
            "date": yesterday,
            "new_signups": len(new_users),
            "new_leads": len(new_leads),
            "emails_sent": len(email_engagement),
            "email_replies": len(replies),
            "hot_leads": len(replies),
        }

        return {
            "success": True,
            "report": report,
        }

    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Internal Helper Functions ────────────────────────────────────────────────

def _get_registrations(start_date: str, period_days: int) -> Dict:
    """Get user registration data."""
    users = get_users_since(since=start_date)

    completed = [u for u in users if u.get("onboarding_completed", True)]
    incomplete = [u for u in users if not u.get("onboarding_completed", False)]
    trial = [u for u in users if u.get("subscription_status") == "trial"]
    paying = [u for u in users if u.get("subscription_status") == "active"]

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
            period_days=period_days,
        ),
        "completed": completed,
        "incomplete": incomplete,
    }


def _get_revenue_metrics(start_date: str) -> Dict[str, Any]:
    """Get revenue metrics."""
    subscriptions = get_subscriptions()

    active_subs = [s for s in subscriptions if s.get("status") == "active"]
    mrr = sum(s.get("amount", 0) for s in active_subs)

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


def _get_sales_pipeline() -> Dict[str, Any]:
    """Get sales pipeline data."""
    leads = get_leads()

    by_status: Dict[str, int] = {}
    for lead in leads:
        status = lead.get("status", "new")
        by_status[status] = by_status.get(status, 0) + 1

    recent_emails = get_personalized_emails(limit=10)

    return {
        "total_leads": len(leads),
        "by_status": by_status,
        "recent_emails": len(recent_emails),
    }


def _get_sales_agent_data() -> Dict[str, Any]:
    """Get sales agent performance data."""
    recent_runs = get_sales_agent_logs(limit=5)

    today = (datetime.utcnow() - timedelta(days=1)).isoformat()
    today_runs = get_sales_agent_logs(since=today, limit=100)

    today_stats = {
        "companies": sum(r.get("companies_processed", 0) for r in today_runs),
        "decision_makers": sum(r.get("decision_makers_found", 0) for r in today_runs),
        "emails_sent": sum(r.get("emails_added_to_instantly", 0) for r in today_runs),
    }

    return {
        "recent_runs": recent_runs[:5],
        "today_stats": today_stats,
    }


def _get_daily_report_data() -> Dict[str, Any]:
    """Get yesterday's daily report data."""
    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    today = datetime.utcnow().date().isoformat()

    new_users = get_users_since(since=yesterday, until=today)
    new_leads = get_leads(since=yesterday, until=today)
    email_engagement = get_email_sequences(since=yesterday, until=today)

    replies = [e for e in email_engagement if e.get("replied_at")]

    return {
        "date": yesterday,
        "new_signups": len(new_users),
        "new_leads": len(new_leads),
        "emails_sent": len(email_engagement),
        "email_replies": len(replies),
        "hot_leads": len(replies),
    }
