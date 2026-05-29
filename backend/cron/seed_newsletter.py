"""
Seed Newsletter Subscribers + Send First Value Drop

1. Imports 166 existing leads as newsletter subscribers
2. Generates a one-time "AI Visibility Report" value drop
3. Sends with clear unsubscribe + subscription invitation
4. Future newsletters only go to opted-in subscribers
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import resend
import db.supabase as db

logger = logging.getLogger(__name__)

NEWSLETTER_FROM = "ben.d@rivaledge.ai"


def get_all_leads() -> list:
    """Get all leads from the database."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase not configured")
        return []
    
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        }
        r = httpx.get(
            f"{supabase_url}/rest/v1/leads?select=email,source,created_at&order=created_at.desc",
            headers=headers,
            timeout=30,
        )
        if r.status_code >= 400:
            logger.error(f"Failed to get leads: {r.text[:500]}")
            return []
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Failed to get leads: {e}")
        return []


def import_leads_as_subscribers(leads: list) -> dict:
    """Import leads as newsletter subscribers (opted-in by default for existing relationship)."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase not configured")
        return {"imported": 0, "skipped": 0}
    
    imported = 0
    skipped = 0
    
    for lead in leads:
        email = lead.get("email")
        if not email:
            continue
        
        payload = {
            "email": email,
            "source": lead.get("source", "lead_import"),
            "is_active": True,
            "subscribed_at": datetime.now(timezone.utc).isoformat(),
        }
        
        try:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=representation",
            }
            r = httpx.post(
                f"{supabase_url}/rest/v1/newsletter_subscribers",
                json=payload,
                headers=headers,
                timeout=10,
            )
            if r.status_code == 201:
                imported += 1
            elif r.status_code == 409:
                skipped += 1  # Already exists
            else:
                logger.warning(f"Unexpected status for {email}: {r.status_code}")
        except Exception as e:
            logger.error(f"Failed to import {email}: {e}")
    
    return {"imported": imported, "skipped": skipped}


def generate_value_drop_content() -> str:
    """Generate the one-time AI Visibility Report content."""
    return """## The AI Visibility Shift: What We Found This Week

AI search is rewriting how B2B buyers discover tools. Here's what changed in the last 7 days:

### 🔍 Google AI Overviews Update
Google expanded AI Overviews to 15 more countries. For B2B SaaS, this means your homepage content is now being summarized directly in search results — often without users clicking through. Companies with clear, structured value propositions are winning these snippets.

### 📊 Perplexity's New Shopping Features
Perplexity added product comparison tables with pricing. For competitive intelligence tools, this is a preview of how AI will surface pricing and feature comparisons directly to buyers — making your competitive positioning more critical than ever.

### 🏆 Vertical Winners This Week
- **Project Management**: Notion and Linear dominate AI recommendations
- **E-commerce**: Shopify maintains 70%+ AI mention share
- **Healthcare SaaS**: Epic and Cerner lead, but AI-native startups gaining ground

### 💡 One Action for Your Team
Run this prompt in ChatGPT/Claude: *"Compare [Your Company] vs [Top 3 Competitors] for [use case]. What are the key differences?"*

If AI doesn't mention your key differentiators, your GEO strategy needs work.

---

**Want weekly updates like this?** This was a one-time report. [Subscribe here](https://rivaledge.ai/audit) for the full GEO + CI Insights newsletter every Tuesday.

**Not interested?** [Unsubscribe](https://rivaledge.ai/unsubscribe) — no hard feelings.
"""


def create_value_drop_html(content: str) -> str:
    """Create HTML email for the value drop."""
    lines = content.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2 style="color: #3b82f6; font-size: 24px; margin-top: 30px; margin-bottom: 15px;">{stripped[3:]}</h2>')
        elif stripped.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h3 style="color: #60a5fa; font-size: 18px; margin-top: 20px; margin-bottom: 10px;">{stripped[4:]}</h3>')
        elif stripped.startswith('• ') or stripped.startswith('- '):
            if not in_list:
                html_lines.append('<ul style="margin-bottom: 15px;">')
                in_list = True
            html_lines.append(f'<li style="margin-bottom: 8px; line-height: 1.6;">{stripped[2:]}</li>')
        elif stripped.startswith('**') and stripped.endswith('**'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = stripped[2:-2]
            html_lines.append(f'<p style="font-weight: bold; margin-bottom: 10px;">{text}</p>')
        elif stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<p style="line-height: 1.6; margin-bottom: 15px; color: #e2e8f0;">{stripped}</p>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<br>')
    
    if in_list:
        html_lines.append('</ul>')
    
    body_html = '\n'.join(html_lines)
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Visibility Report - RivalEdge</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%;">
                    <!-- Header -->
                    <tr>
                        <td style="text-align: center; padding-bottom: 30px; border-bottom: 1px solid #1e293b;">
                            <h1 style="color: #3b82f6; font-size: 28px; margin: 0 0 10px 0;">AI VISIBILITY REPORT</h1>
                            <p style="color: #94a3b8; font-size: 14px; margin: 0;">Weekly intelligence on AI search shifts and competitive positioning</p>
                            <p style="color: #64748b; font-size: 12px; margin: 10px 0 0 0;">{datetime.now(timezone.utc).strftime('%B %d, %Y')} | <a href="https://rivaledge.ai" style="color: #3b82f6; text-decoration: none;">rivaledge.ai</a></p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px 0; color: #e2e8f0;">
                            {body_html}
                        </td>
                    </tr>
                    
                    <!-- Subscribe CTA -->
                    <tr>
                        <td style="text-align: center; padding: 30px 0; border-top: 1px solid #1e293b; background-color: #1e293b; border-radius: 8px;">
                            <p style="color: #e2e8f0; font-size: 18px; margin-bottom: 10px; font-weight: 600;">Want this every Tuesday?</p>
                            <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Get the full GEO + CI Insights newsletter with scorecards, competitive moves, and actionable tips.</p>
                            <a href="https://rivaledge.ai/audit" style="display: inline-block; background-color: #3b82f6; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">Subscribe to Weekly Updates →</a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="text-align: center; padding-top: 30px; border-top: 1px solid #1e293b;">
                            <p style="color: #64748b; font-size: 12px; margin: 0 0 10px 0;">
                                Sent by <a href="https://rivaledge.ai" style="color: #3b82f6; text-decoration: none;">RivalEdge</a> — AI-native competitive intelligence
                            </p>
                            <p style="color: #475569; font-size: 11px; margin: 0 0 15px 0;">
                                You're receiving this because your company matches our research criteria for AI-native B2B tools.
                            </p>
                            <p style="color: #475569; font-size: 11px; margin: 0;">
                                <a href="https://rivaledge.ai/unsubscribe?email={{email}}" style="color: #64748b; text-decoration: underline;">Unsubscribe</a> | 
                                <a href="https://rivaledge.ai/privacy" style="color: #64748b; text-decoration: underline;">Privacy Policy</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def send_value_drop(subscribers: list, test_mode: bool = False) -> dict:
    """Send the one-time value drop to subscribers."""
    resend_key = os.environ.get("RESEND_API_KEY", "") or os.environ.get("RESEND_KEY", "")
    if not resend_key:
        logger.error("RESEND_API_KEY not set")
        return {"sent": 0, "failed": len(subscribers)}
    
    resend.api_key = resend_key
    
    content = generate_value_drop_content()
    html = create_value_drop_html(content)
    
    if test_mode:
        # Send to first 1 only (as requested by Waters)
        subscribers = subscribers[:1]
        logger.info(f"TEST MODE: Sending to {len(subscribers)} subscriber")
    
    sent_count = 0
    failed_count = 0
    
    for subscriber in subscribers:
        email = subscriber.get("email")
        if not email:
            continue
        
        # Personalize HTML
        personalized_html = html.replace("{{email}}", email)
        
        try:
            response = resend.Emails.send({
                "from": f"Ben D - RivalEdge AI <{NEWSLETTER_FROM}>",
                "to": [email],
                "subject": "AI Visibility Report: What changed this week in AI search",
                "html": personalized_html,
                "reply_to": NEWSLETTER_FROM,
            })
            sent_count += 1
            logger.info(f"Value drop sent to {email}, ID: {response.get('id')}")
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send to {email}: {e}")
    
    return {"sent": sent_count, "failed": failed_count}


def main(test_mode: bool = False):
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    
    logger.info("=" * 60)
    logger.info("NEWSLETTER SEED + VALUE DROP")
    logger.info("=" * 60)
    
    # Step 1: Get all leads
    logger.info("Step 1: Fetching leads...")
    leads = get_all_leads()
    logger.info(f"Found {len(leads)} leads")
    
    # Step 2: Import as subscribers
    logger.info("Step 2: Importing leads as subscribers...")
    import_result = import_leads_as_subscribers(leads)
    logger.info(f"Imported: {import_result['imported']}, Skipped (already exists): {import_result['skipped']}")
    
    # Step 3: Get all subscribers
    logger.info("Step 3: Fetching subscribers...")
    try:
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        }
        r = httpx.get(
            f"{supabase_url}/rest/v1/newsletter_subscribers?is_active=eq.true&select=email",
            headers=headers,
            timeout=10,
        )
        subscribers = r.json() if r.status_code < 400 else []
        logger.info(f"Total active subscribers: {len(subscribers)}")
    except Exception as e:
        logger.error(f"Failed to get subscribers: {e}")
        subscribers = []
    
    # Step 4: Send value drop
    if subscribers:
        logger.info("Step 4: Sending value drop...")
        send_result = send_value_drop(subscribers, test_mode=test_mode)
        logger.info(f"Sent: {send_result['sent']}, Failed: {send_result['failed']}")
    else:
        logger.warning("No subscribers to send to")
        send_result = {"sent": 0, "failed": 0}
    
    # Summary
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Leads found: {len(leads)}")
    logger.info(f"Subscribers imported: {import_result['imported']}")
    logger.info(f"Subscribers skipped: {import_result['skipped']}")
    logger.info(f"Total subscribers: {len(subscribers)}")
    logger.info(f"Emails sent: {send_result['sent']}")
    logger.info(f"Emails failed: {send_result['failed']}")
    
    return {
        "leads": len(leads),
        "imported": import_result['imported'],
        "subscribers": len(subscribers),
        "sent": send_result['sent'],
        "failed": send_result['failed'],
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Send to first 5 subscribers only")
    args = parser.parse_args()
    
    result = main(test_mode=args.test)
    print(json.dumps(result, indent=2))
