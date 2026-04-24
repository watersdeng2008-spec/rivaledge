"""
PostHog analytics integration for RivalEdge
Tracks user events, page views, and funnel metrics
"""
import os
from typing import Optional, Dict, Any
import posthog

# Initialize PostHog
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")

# Configure PostHog
if POSTHOG_API_KEY:
    posthog.api_key = POSTHOG_API_KEY
    posthog.host = POSTHOG_HOST
    posthog.debug = os.getenv("POSTHOG_DEBUG", "false").lower() == "true"


def track_event(
    event_name: str,
    user_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    distinct_id: Optional[str] = None
) -> None:
    """
    Track a custom event in PostHog
    
    Args:
        event_name: Name of the event (e.g., "user_signed_up", "report_generated")
        user_id: User ID (optional, uses distinct_id if not provided)
        properties: Event properties dictionary
        distinct_id: Distinct ID for the user (falls back to user_id or "anonymous")
    """
    if not POSTHOG_API_KEY:
        return
    
    distinct_id = distinct_id or user_id or "anonymous"
    props = properties or {}
    
    posthog.capture(
        distinct_id=distinct_id,
        event=event_name,
        properties=props
    )


def identify_user(
    user_id: str,
    properties: Optional[Dict[str, Any]] = None
) -> None:
    """
    Identify a user with traits
    
    Args:
        user_id: Unique user identifier
        properties: User properties (email, name, plan, etc.)
    """
    if not POSTHOG_API_KEY:
        return
    
    posthog.identify(
        distinct_id=user_id,
        properties=properties or {}
    )


def track_page_view(
    user_id: Optional[str] = None,
    page_path: str = "",
    page_title: str = "",
    referrer: str = "",
    properties: Optional[Dict[str, Any]] = None
) -> None:
    """
    Track a page view event
    
    Args:
        user_id: User ID (optional)
        page_path: URL path (e.g., "/dashboard")
        page_title: Page title
        referrer: Referrer URL
        properties: Additional properties
    """
    props = {
        "$current_url": page_path,
        "$pathname": page_path,
        "$page_title": page_title,
        "$referrer": referrer,
        **(properties or {})
    }
    
    track_event(
        event_name="$pageview",
        user_id=user_id,
        properties=props
    )


# Pre-defined event tracking functions for common RivalEdge events

def track_user_signup(user_id: str, email: str, signup_source: str = "organic") -> None:
    """Track when a user signs up"""
    track_event(
        event_name="user_signed_up",
        user_id=user_id,
        properties={
            "email": email,
            "signup_source": signup_source,
            "$set": {"email": email, "signup_date": "now()"}
        }
    )


def track_user_login(user_id: str, method: str = "email") -> None:
    """Track when a user logs in"""
    track_event(
        event_name="user_logged_in",
        user_id=user_id,
        properties={"login_method": method}
    )


def track_report_generated(
    user_id: str,
    report_type: str,
    competitor_count: int = 0,
    generation_time_ms: Optional[int] = None
) -> None:
    """Track when a competitor report is generated"""
    track_event(
        event_name="report_generated",
        user_id=user_id,
        properties={
            "report_type": report_type,
            "competitor_count": competitor_count,
            "generation_time_ms": generation_time_ms
        }
    )


def track_competitor_added(
    user_id: str,
    competitor_name: str,
    competitor_domain: str
) -> None:
    """Track when a user adds a competitor"""
    track_event(
        event_name="competitor_added",
        user_id=user_id,
        properties={
            "competitor_name": competitor_name,
            "competitor_domain": competitor_domain
        }
    )


def track_subscription_created(
    user_id: str,
    plan: str,
    amount: float,
    currency: str = "USD"
) -> None:
    """Track when a user subscribes"""
    track_event(
        event_name="subscription_created",
        user_id=user_id,
        properties={
            "plan": plan,
            "amount": amount,
            "currency": currency,
            "$set": {"plan": plan, "is_paying": True}
        }
    )


def track_email_sent(
    user_id: str,
    email_type: str,
    recipient_count: int = 1
) -> None:
    """Track when an email is sent"""
    track_event(
        event_name="email_sent",
        user_id=user_id,
        properties={
            "email_type": email_type,
            "recipient_count": recipient_count
        }
    )


def track_sales_outreach_sent(
    leads_count: int,
    campaign_id: str,
    success_rate: float
) -> None:
    """Track daily sales outreach automation"""
    track_event(
        event_name="sales_outreach_sent",
        distinct_id="system",
        properties={
            "leads_count": leads_count,
            "campaign_id": campaign_id,
            "success_rate": success_rate,
            "source": "autonomous_agent"
        }
    )


def track_api_error(
    endpoint: str,
    error_code: str,
    error_message: str,
    user_id: Optional[str] = None
) -> None:
    """Track API errors for monitoring"""
    track_event(
        event_name="api_error",
        user_id=user_id,
        properties={
            "endpoint": endpoint,
            "error_code": error_code,
            "error_message": error_message
        }
    )
