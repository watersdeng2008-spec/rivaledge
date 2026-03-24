"""
Email service — sends digests via Resend.

Day 3 feature — interface defined, stub for Day 1.
"""
import os
from typing import Optional


DIGEST_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RivalEdge Digest</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #1a1a1a;">
  <div style="border-bottom: 2px solid #6366f1; padding-bottom: 16px; margin-bottom: 24px;">
    <h1 style="margin: 0; color: #6366f1;">⚡ RivalEdge</h1>
    <p style="margin: 4px 0 0; color: #666;">Your competitor intelligence digest</p>
  </div>
  
  <div style="line-height: 1.6;">
    {digest_html}
  </div>
  
  <div style="border-top: 1px solid #e5e7eb; margin-top: 32px; padding-top: 16px; color: #9ca3af; font-size: 12px;">
    <p>You're receiving this because you track competitors on RivalEdge.</p>
    <p><a href="https://rivaledge.ai/settings" style="color: #6366f1;">Manage preferences</a> · <a href="https://rivaledge.ai/unsubscribe" style="color: #6366f1;">Unsubscribe</a></p>
  </div>
</body>
</html>
"""


async def send_digest(to_email: str, digest_markdown: str) -> dict:
    """
    Send a digest email via Resend.
    
    Args:
        to_email: Recipient email address
        digest_markdown: Markdown-formatted digest content
    
    Returns:
        Resend API response dict
    """
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set")
    
    from_email = os.environ.get("RESEND_FROM_EMAIL", "digest@rivaledge.ai")
    
    import httpx
    import markdown
    
    digest_html = markdown.markdown(digest_markdown)
    html_body = DIGEST_EMAIL_TEMPLATE.format(digest_html=digest_html)
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [to_email],
                "subject": "⚡ RivalEdge: Your Daily Competitor Digest",
                "html": html_body,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()


async def send_welcome_email(to_email: str) -> dict:
    """Send a welcome email to new users."""
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set")
    
    from_email = os.environ.get("RESEND_FROM_EMAIL", "hello@rivaledge.ai")
    
    import httpx
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [to_email],
                "subject": "Welcome to RivalEdge ⚡",
                "html": "<h1>Welcome to RivalEdge!</h1><p>Start tracking your competitors at <a href='https://rivaledge.ai'>rivaledge.ai</a></p>",
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()
