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

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from auth import get_current_user, get_optional_user
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
    api_key: str = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user),
) -> dict:
    """Require admin access OR valid API key (for Google Apps Script)."""
    expected_api_key = os.environ.get("CEO_DASHBOARD_API_KEY", "")

    # Check API key first — allows access without Clerk auth (e.g. Google Apps Script)
    if api_key and expected_api_key and api_key == expected_api_key:
        return {"sub": "api_key_access", "api_access": True}

    # No valid API key — fall back to requiring an authenticated admin user
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

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


@router.get("/dashboard-html", response_class=HTMLResponse)
def get_ceo_dashboard_html(
    days: int = Query(30, ge=1, le=90, description="Analysis period in days"),
    current_user: dict = Depends(require_admin_or_api_key),
):
    """
    Get CEO dashboard as a formatted HTML page.

    Returns the same data as /dashboard but rendered as a styled HTML view
    for easy reading directly in a browser.
    """
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        registrations = _get_registrations(start_date, days)
        revenue = _get_revenue_metrics(start_date)
        pipeline = _get_sales_pipeline()

        stats = registrations["stats"]
        recent_signups = registrations["completed"][:10]
        incomplete_signups = registrations["incomplete"][:10]

        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        def _row(user: Dict[str, Any]) -> str:
            email = user.get("email", "—")
            company = user.get("company") or user.get("company_name") or "—"
            plan = user.get("plan") or user.get("subscription_status") or "—"
            created = user.get("created_at", "")
            if created and "T" in str(created):
                created = str(created).split("T")[0]
            return (
                f"<tr>"
                f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;'>{email}</td>"
                f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;'>{company}</td>"
                f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;'>{plan}</td>"
                f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;'>{created}</td>"
                f"</tr>"
            )

        recent_rows = "".join(_row(u) for u in recent_signups) or (
            "<tr><td colspan='4' style='padding:12px;text-align:center;color:#6b7280;'>No signups in this period</td></tr>"
        )
        incomplete_rows = "".join(_row(u) for u in incomplete_signups) or (
            "<tr><td colspan='4' style='padding:12px;text-align:center;color:#6b7280;'>No incomplete signups</td></tr>"
        )

        pipeline_by_status_rows = "".join(
            f"<tr>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #e5e7eb;text-transform:capitalize;'>{status_name}</td>"
            f"<td style='padding:6px 12px;border-bottom:1px solid #e5e7eb;font-weight:600;'>{count}</td>"
            f"</tr>"
            for status_name, count in pipeline.get("by_status", {}).items()
        ) or "<tr><td colspan='2' style='padding:12px;text-align:center;color:#6b7280;'>No pipeline data</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CEO Dashboard — RivalEdge</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f3f4f6;
      color: #111827;
      padding: 32px 16px;
    }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    h1 {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 4px; }}
    .subtitle {{ color: #6b7280; font-size: 0.875rem; margin-bottom: 32px; }}
    .section {{ margin-bottom: 32px; }}
    .section-title {{
      font-size: 1rem; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.05em; color: #374151; margin-bottom: 12px;
      padding-bottom: 6px; border-bottom: 2px solid #e5e7eb;
    }}
    .cards {{ display: flex; flex-wrap: wrap; gap: 16px; }}
    .card {{
      background: #fff; border-radius: 10px; padding: 20px 24px;
      flex: 1 1 140px; box-shadow: 0 1px 3px rgba(0,0,0,.08);
    }}
    .card-label {{ font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }}
    .card-value {{ font-size: 1.5rem; font-weight: 700; color: #111827; }}
    .card-value.green {{ color: #059669; }}
    .card-value.blue {{ color: #2563eb; }}
    table {{
      width: 100%; border-collapse: collapse; background: #fff;
      border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08);
    }}
    thead {{ background: #f9fafb; }}
    th {{
      padding: 10px 12px; text-align: left; font-size: 0.75rem;
      font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280;
    }}
    tr:last-child td {{ border-bottom: none !important; }}
    @media (max-width: 600px) {{
      .card {{ flex: 1 1 100%; }}
      table {{ font-size: 0.85rem; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>CEO Dashboard</h1>
    <p class="subtitle">Last {days} days &nbsp;·&nbsp; Generated {generated_at}</p>

    <!-- Registration Stats -->
    <div class="section">
      <div class="section-title">Registration Stats</div>
      <div class="cards">
        <div class="card">
          <div class="card-label">Total Registrations</div>
          <div class="card-value">{stats.total_registrations}</div>
        </div>
        <div class="card">
          <div class="card-label">Completed Signups</div>
          <div class="card-value blue">{stats.completed_signups}</div>
        </div>
        <div class="card">
          <div class="card-label">Incomplete Signups</div>
          <div class="card-value">{stats.incomplete_signups}</div>
        </div>
        <div class="card">
          <div class="card-label">Trial Users</div>
          <div class="card-value">{stats.trial_users}</div>
        </div>
        <div class="card">
          <div class="card-label">Paying Customers</div>
          <div class="card-value green">{stats.paying_customers}</div>
        </div>
        <div class="card">
          <div class="card-label">Conversion Rate</div>
          <div class="card-value green">{stats.conversion_rate}%</div>
        </div>
      </div>
    </div>

    <!-- Recent Signups -->
    <div class="section">
      <div class="section-title">Recent Signups (last 10)</div>
      <table>
        <thead>
          <tr>
            <th>Email</th><th>Company</th><th>Plan</th><th>Created At</th>
          </tr>
        </thead>
        <tbody>{recent_rows}</tbody>
      </table>
    </div>

    <!-- Incomplete Signups -->
    <div class="section">
      <div class="section-title">Incomplete Signups (last 10)</div>
      <table>
        <thead>
          <tr>
            <th>Email</th><th>Company</th><th>Plan</th><th>Created At</th>
          </tr>
        </thead>
        <tbody>{incomplete_rows}</tbody>
      </table>
    </div>

    <!-- Revenue Metrics -->
    <div class="section">
      <div class="section-title">Revenue Metrics</div>
      <div class="cards">
        <div class="card">
          <div class="card-label">MRR</div>
          <div class="card-value green">{revenue.get("mrr_formatted", "$0.00")}</div>
        </div>
        <div class="card">
          <div class="card-label">Active Subscriptions</div>
          <div class="card-value blue">{revenue.get("active_subscriptions", 0)}</div>
        </div>
        <div class="card">
          <div class="card-label">New Revenue (period)</div>
          <div class="card-value green">{revenue.get("new_revenue_formatted", "$0.00")}</div>
        </div>
        <div class="card">
          <div class="card-label">New Subscriptions</div>
          <div class="card-value">{revenue.get("new_subscriptions_period", 0)}</div>
        </div>
      </div>
    </div>

    <!-- Sales Pipeline -->
    <div class="section">
      <div class="section-title">Sales Pipeline</div>
      <div class="cards" style="margin-bottom:16px;">
        <div class="card">
          <div class="card-label">Total Leads</div>
          <div class="card-value">{pipeline.get("total_leads", 0)}</div>
        </div>
        <div class="card">
          <div class="card-label">Recent Emails</div>
          <div class="card-value">{pipeline.get("recent_emails", 0)}</div>
        </div>
      </div>
      <table>
        <thead>
          <tr><th>Status</th><th>Count</th></tr>
        </thead>
        <tbody>{pipeline_by_status_rows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>"""

        return HTMLResponse(content=html, status_code=200)

    except Exception as e:
        logger.error(f"Failed to render CEO dashboard HTML: {e}")
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
