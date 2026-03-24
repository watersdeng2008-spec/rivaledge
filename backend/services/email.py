"""
Email service — sends digests and transactional emails via Resend API.

Day 3: Full implementation of send_digest and send_welcome_email.
Uses synchronous httpx (not async) so it works in both sync and async contexts.
"""
import os
import logging
import re
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

RESEND_BASE_URL = "https://api.resend.com"
FROM_DIGEST = "RivalEdge <digests@rivaledge.ai>"
FROM_WELCOME = "RivalEdge <hello@rivaledge.ai>"


def _get_api_key() -> str:
    key = os.environ.get("RESEND_API_KEY", "")
    if not key:
        raise RuntimeError("RESEND_API_KEY not set")
    return key


def _extract_subject_from_html(html_content: str) -> Optional[str]:
    """Extract subject from <!-- SUBJECT: ... --> comment in HTML."""
    match = re.search(r'<!--\s*SUBJECT:\s*(.+?)\s*-->', html_content)
    if match:
        return match.group(1).strip()
    return None


# ── send_digest ────────────────────────────────────────────────────────────────

def send_digest(to_email: str, html_content: str, subject: str) -> bool:
    """
    Send a digest email via Resend API.
    
    Args:
        to_email: Recipient email address
        html_content: Full HTML email body
        subject: Email subject line
    
    Returns:
        True on success, False on failure (logs error, doesn't raise).
    """
    try:
        api_key = _get_api_key()
        
        response = httpx.post(
            f"{RESEND_BASE_URL}/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": FROM_DIGEST,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "headers": {
                    "X-Unsubscribe": "{{unsubscribe_url}}",
                },
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Digest sent to {to_email}, Resend ID: {data.get('id')}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send digest to {to_email}: {e}")
        return False


# ── send_welcome_email ─────────────────────────────────────────────────────────

def send_welcome_email(to_email: str, first_competitor: str) -> bool:
    """
    Send a welcome/onboarding email when a user adds their first competitor.
    
    Args:
        to_email: Recipient email address
        first_competitor: Name or URL of the first competitor they added
    
    Returns:
        True on success, False on failure.
    """
    try:
        api_key = _get_api_key()
        
        html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Welcome to RivalEdge</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f9fafb;">
  <div style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 32px 40px;">
      <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">⚡ RivalEdge</h1>
      <p style="margin: 8px 0 0; color: rgba(255,255,255,0.85); font-size: 16px;">Your AI competitor intelligence platform</p>
    </div>
    
    <!-- Body -->
    <div style="padding: 40px;">
      <h2 style="margin: 0 0 16px; color: #111827; font-size: 22px;">You're all set! 🎉</h2>
      
      <p style="color: #374151; line-height: 1.6; font-size: 15px;">
        We're now monitoring <strong>{first_competitor}</strong> for you. Every week, you'll receive a curated briefing with:
      </p>
      
      <ul style="color: #374151; line-height: 1.8; font-size: 15px; padding-left: 20px;">
        <li>🔍 Pricing changes and new tiers</li>
        <li>✨ New features and product updates</li>
        <li>💬 Messaging and positioning shifts</li>
        <li>🎯 AI-powered "what this means" analysis</li>
      </ul>
      
      <p style="color: #374151; line-height: 1.6; font-size: 15px;">
        Your first digest will arrive next Monday at 7am CT. You can also generate one on-demand from your dashboard.
      </p>
      
      <!-- CTA Button -->
      <div style="text-align: center; margin: 32px 0;">
        <a href="https://rivaledge.ai/dashboard" 
           style="display: inline-block; background: #6366f1; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 15px; font-weight: 600;">
          Go to Dashboard →
        </a>
      </div>
      
      <p style="color: #6b7280; font-size: 14px; line-height: 1.5;">
        Questions? Reply to this email or visit our <a href="https://rivaledge.ai/docs" style="color: #6366f1;">documentation</a>.
      </p>
    </div>
    
    <!-- Footer -->
    <div style="background: #f9fafb; border-top: 1px solid #e5e7eb; padding: 24px 40px; text-align: center;">
      <p style="margin: 0; color: #9ca3af; font-size: 12px;">
        RivalEdge · AI Competitor Intelligence<br>
        <a href="{{{{unsubscribe_url}}}}" style="color: #6366f1;">Unsubscribe</a> · 
        <a href="https://rivaledge.ai/settings" style="color: #6366f1;">Manage preferences</a>
      </p>
    </div>
  </div>
</body>
</html>"""
        
        response = httpx.post(
            f"{RESEND_BASE_URL}/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": FROM_WELCOME,
                "to": [to_email],
                "subject": "Welcome to RivalEdge ⚡ — We're watching your competitors",
                "html": html_body,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Welcome email sent to {to_email}, Resend ID: {data.get('id')}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False
