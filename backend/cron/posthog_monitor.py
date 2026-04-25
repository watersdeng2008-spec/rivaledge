"""
PostHog Monitor - Track signups and incomplete onboarding
Polls PostHog API for new signups who haven't completed onboarding
"""
import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from db.supabase import get_users, get_user_onboarding_status
from services.email import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostHog config
POSTHOG_API_KEY = os.environ.get("POSTHOG_PERSONAL_API_KEY")
POSTHOG_PROJECT_ID = os.environ.get("POSTHOG_PROJECT_ID", "rivaledge")
POSTHOG_HOST = "https://us.posthog.com"

# Telegram config for alerts
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Onboarding questions (for reference)
ONBOARDING_QUESTIONS = [
    "What's your company name?",
    "Who are your top 3 competitors?",
    "What industry are you in?",
    "What's your primary use case for competitor monitoring?"
]


def send_telegram_alert(message: str) -> bool:
    """Send alert to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured, skipping alert")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False


def get_recent_signups(hours: int = 24) -> list[dict]:
    """
    Get users who signed up in the last N hours but haven't completed onboarding.
    
    This queries Supabase for users with:
    - created_at within last N hours
    - onboarding_completed = false or null
    - no recent follow-up email sent
    """
    try:
        from db.supabase import supabase
        
        cutoff_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        
        # Query for recent signups without completed onboarding
        response = supabase.table("users").select(
            "id, email, created_at, onboarding_completed, company_name"
        ).gte("created_at", cutoff_time).or_("onboarding_completed.is.null,onboarding_completed.eq.false").execute()
        
        users = response.data or []
        
        # Filter out users who already received follow-up in last 24h
        result = []
        for user in users:
            user_id = user.get("id")
            
            # Check if we already sent a follow-up email
            email_check = supabase.table("emails_sent").select("id").eq(
                "user_id", user_id
            ).eq("email_type", "onboarding_followup").gte(
                "sent_at", cutoff_time
            ).execute()
            
            if not email_check.data:
                result.append(user)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get recent signups: {e}")
        return []


def draft_followup_email(user_email: str, company_name: Optional[str]) -> str:
    """Draft a personalized follow-up email offering to complete onboarding."""
    
    company_greeting = f" at {company_name}" if company_name else ""
    
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(ONBOARDING_QUESTIONS)])
    
    email_body = f"""Hi there{company_greeting},

I noticed you started signing up for RivalEdge but didn't complete the onboarding process. No worries — I can help you get set up quickly!

To get your competitor monitoring dashboard ready, I just need you to answer these quick questions:

{questions_text}

Simply reply to this email with your answers, and I'll:
✓ Set up your competitor tracking
✓ Configure your first monitoring report
✓ Have everything ready within 24 hours

No need to log in and fill out forms — just hit reply and I'll handle the rest.

Best,
Ben D
CEO, RivalEdge

P.S. If you have any questions about how RivalEdge works, just ask. I'm here to help!
"""
    
    return email_body


def send_onboarding_followup(user: dict) -> bool:
    """Send follow-up email to user who hasn't completed onboarding."""
    try:
        user_id = user.get("id")
        email = user.get("email")
        company_name = user.get("company_name")
        
        if not email:
            logger.warning(f"User {user_id} has no email, skipping")
            return False
        
        # Draft the email
        body = draft_followup_email(email, company_name)
        
        # Send via your email service (Resend)
        subject = "Let me complete your RivalEdge setup for you"
        
        # Use the existing email service
        success = send_email(
            to_email=email,
            subject=subject,
            body=body,
            from_email="ben.d@rivaledge.ai"
        )
        
        if success:
            # Log that we sent this email
            from db.supabase import supabase
            supabase.table("emails_sent").insert({
                "user_id": user_id,
                "email_type": "onboarding_followup",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "subject": subject
            }).execute()
            
            logger.info(f"Sent onboarding follow-up to {email}")
            return True
        else:
            logger.error(f"Failed to send email to {email}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending onboarding followup: {e}")
        return False


def check_incomplete_onboarding():
    """Main function to check for incomplete onboarding and send follow-ups."""
    logger.info("Checking for incomplete onboarding...")
    
    # Get recent signups who haven't completed onboarding
    users = get_recent_signups(hours=48)  # Check last 48 hours
    
    if not users:
        logger.info("No incomplete onboarding found")
        return
    
    logger.info(f"Found {len(users)} users with incomplete onboarding")
    
    alerts_sent = 0
    emails_sent = 0
    
    for user in users:
        email = user.get("email", "Unknown")
        company = user.get("company_name", "Not provided")
        created_at = user.get("created_at", "Unknown")
        
        # Send Telegram alert to you
        alert_message = f"""🚨 *Incomplete Onboarding Detected*

📧 Email: {email}
🏢 Company: {company}
🕐 Signed up: {created_at}

Follow-up email {'sent' if send_onboarding_followup(user) else 'FAILED to send'}.
"""
        
        if send_telegram_alert(alert_message):
            alerts_sent += 1
        
        # Small delay to avoid rate limits
        import time
        time.sleep(1)
    
    logger.info(f"Processed {len(users)} users, sent {alerts_sent} alerts")


if __name__ == "__main__":
    check_incomplete_onboarding()
