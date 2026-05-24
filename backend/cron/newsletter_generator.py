"""
GEO + CI Insights Newsletter Generator

Generates and sends weekly newsletter analyzing AI search shifts
and competitive intelligence insights.

Schedule: Every Tuesday at 8:00 AM CDT
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone, timedelta

import httpx

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai import _call_ai
from services.email_service import send_email
import db.supabase as db

logger = logging.getLogger(__name__)

# ── Newsletter Configuration ─────────────────────────────────────────────────

NEWSLETTER_FROM = "ben.d@rivaledge.ai"
NEWSLETTER_NAME = "GEO + CI Insights"

# Verticals to analyze (rotate weekly)
VERTICALS = [
    "Project Management Software",
    "E-commerce Platforms",
    "Healthcare SaaS",
    "B2B SaaS",
    "Wellness & Supplements",
    "Fintech",
    "Travel & Hospitality",
    "Legal Tech",
]

# ── Content Generation ───────────────────────────────────────────────────────

NEWSLETTER_SYSTEM_PROMPT = """You are the editor of "GEO + CI Insights" — a weekly newsletter for B2B founders, marketers, and product leaders about AI search and competitive intelligence.

WRITING STYLE:
- Sharp, insightful, no fluff
- Data-driven but accessible
- Founder-to-founder tone
- Actionable takeaways in every section

FORMAT:
## The Big Shift: [Headline]
[300-400 words on one major trend]

## AI Visibility Scorecard: [Vertical]
[Table format scorecard with mock data]

## Competitive Move of the Week
[200-300 words on one significant competitor move]

## GEO Tip of the Week
[150-200 words with one actionable tip]

## What We're Tracking Next Week
[Bullet list of 3-4 items]

Use markdown formatting. Include specific numbers and examples."""


def generate_newsletter_content(week_number: int, vertical: str) -> dict:
    """Generate newsletter content for a specific week."""
    
    # Determine topics based on week number
    topics = [
        "Journey compression killing traditional funnels",
        "Perplexity shopping feature impact",
        "Google AI Overviews update",
        "Claude 4 citation changes",
        "Trust signals vs. technical GEO",
        "AI recommendation share as new metric",
        "Vertical AI search winners",
        "The future of AI recommendations",
    ]
    
    topic = topics[week_number % len(topics)]
    
    prompt = f"""Generate the GEO + CI Insights newsletter for Week {week_number}.

FOCUS TOPIC: {topic}
SCORECARD VERTICAL: {vertical}

Generate all sections:
1. The Big Shift (300-400 words)
2. AI Visibility Scorecard for {vertical} (with realistic mock data)
3. Competitive Move of the Week (200-300 words)
4. GEO Tip of the Week (150-200 words)
5. What We're Tracking Next Week (3-4 bullets)

Make it insightful and actionable. Use realistic company names and data."""
    
    content = _call_ai(
        system=NEWSLETTER_SYSTEM_PROMPT,
        user=prompt,
        max_tokens=4000,
        use_cache=False,
    )
    
    return {
        "week_number": week_number,
        "vertical": vertical,
        "topic": topic,
        "content": content,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── Email Template ───────────────────────────────────────────────────────────

def create_newsletter_html(content: str, week_number: int) -> str:
    """Create HTML email from newsletter content."""
    
    # Convert markdown to basic HTML
    html_content = content
    
    # Simple markdown-to-HTML conversion
    lines = html_content.split('\n')
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
    <title>GEO + CI Insights - Issue #{week_number}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%;">
                    <!-- Header -->
                    <tr>
                        <td style="text-align: center; padding-bottom: 30px; border-bottom: 1px solid #1e293b;">
                            <h1 style="color: #3b82f6; font-size: 28px; margin: 0 0 10px 0;">GEO + CI INSIGHTS</h1>
                            <p style="color: #94a3b8; font-size: 14px; margin: 0;">Weekly analysis of AI search shifts and competitive intelligence</p>
                            <p style="color: #64748b; font-size: 12px; margin: 10px 0 0 0;">Issue #{week_number} | {datetime.now(timezone.utc).strftime('%B %d, %Y')} | <a href="https://rivaledge.ai" style="color: #3b82f6; text-decoration: none;">rivaledge.ai</a></p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px 0; color: #e2e8f0;">
                            {body_html}
                        </td>
                    </tr>
                    
                    <!-- CTA -->
                    <tr>
                        <td style="text-align: center; padding: 30px 0; border-top: 1px solid #1e293b;">
                            <p style="color: #94a3b8; font-size: 16px; margin-bottom: 20px;">Want to track your AI Recommendation Share?</p>
                            <a href="https://rivaledge.ai/audit" style="display: inline-block; background-color: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: 600;">Start Free Audit →</a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="text-align: center; padding-top: 30px; border-top: 1px solid #1e293b;">
                            <p style="color: #64748b; font-size: 12px; margin: 0 0 10px 0;">
                                <strong style="color: #94a3b8;">GEO + CI Insights</strong> is brought to you by <a href="https://rivaledge.ai" style="color: #3b82f6; text-decoration: none;">RivalEdge</a>
                            </p>
                            <p style="color: #475569; font-size: 11px; margin: 0;">
                                You're receiving this because you signed up at rivaledge.ai or downloaded our AI Visibility Audit.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


# ── Subscriber Management ────────────────────────────────────────────────────

def get_newsletter_subscribers() -> list:
    """Get all active newsletter subscribers."""
    try:
        r = httpx.get(
            db._url("newsletter_subscribers?is_active=eq.true&select=*"),
            headers=db._headers(),
            timeout=10,
        )
        
        if r.status_code >= 400:
            logger.error(f"Failed to get subscribers: {r.text[:500]}")
            return []
        
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Failed to get subscribers: {e}")
        return []


def add_newsletter_subscriber(email: str, source: str = "website") -> dict:
    """Add a new newsletter subscriber."""
    payload = {
        "email": email,
        "source": source,
        "is_active": True,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
    }
    
    try:
        headers = {**db._headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
        r = httpx.post(
            db._url("newsletter_subscribers"),
            json=payload,
            headers=headers,
            timeout=10,
        )
        
        if r.status_code >= 400:
            logger.error(f"Failed to add subscriber: {r.text[:500]}")
            return {}
        
        data = r.json()
        return data[0] if isinstance(data, list) and data else payload
    except Exception as e:
        logger.error(f"Failed to add subscriber: {e}")
        return {}


# ── Main Generator ───────────────────────────────────────────────────────────

def generate_and_send_newsletter():
    """Generate and send the weekly newsletter."""
    logger.info("Starting newsletter generation...")
    
    # Calculate week number (starting from first week of 2026)
    start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    today = datetime.now(timezone.utc)
    week_number = (today - start_date).days // 7 + 1
    
    # Select vertical based on week
    vertical = VERTICALS[week_number % len(VERTICALS)]
    
    logger.info(f"Generating newsletter for week {week_number}, vertical: {vertical}")
    
    # Generate content
    newsletter_data = generate_newsletter_content(week_number, vertical)
    content = newsletter_data["content"]
    
    # Create HTML
    html = create_newsletter_html(content, week_number)
    
    # Get subscribers
    subscribers = get_newsletter_subscribers()
    
    if not subscribers:
        logger.warning("No subscribers found. Newsletter generated but not sent.")
        # Still save the newsletter for archive
        save_newsletter_archive(newsletter_data, html)
        return
    
    logger.info(f"Sending newsletter to {len(subscribers)} subscribers")
    
    # Send to each subscriber
    sent_count = 0
    failed_count = 0
    
    for subscriber in subscribers:
        email = subscriber.get("email")
        if not email:
            continue
        
        try:
            send_email(
                to_email=email,
                subject=f"GEO + CI Insights - Issue #{week_number}: {newsletter_data['topic']}",
                html_content=html,
                from_email=NEWSLETTER_FROM,
            )
            sent_count += 1
            logger.info(f"Newsletter sent to {email}")
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send to {email}: {e}")
    
    # Save to archive
    save_newsletter_archive(newsletter_data, html)
    
    logger.info(f"Newsletter complete: {sent_count} sent, {failed_count} failed")
    return {
        "week_number": week_number,
        "vertical": vertical,
        "subscribers": len(subscribers),
        "sent": sent_count,
        "failed": failed_count,
    }


def save_newsletter_archive(newsletter_data: dict, html: str) -> dict:
    """Save newsletter to archive."""
    payload = {
        "week_number": newsletter_data["week_number"],
        "vertical": newsletter_data["vertical"],
        "topic": newsletter_data["topic"],
        "content": newsletter_data["content"],
        "html": html,
        "generated_at": newsletter_data["generated_at"],
    }
    
    try:
        r = httpx.post(
            db._url("newsletter_archive"),
            json=payload,
            headers=db._headers(),
            timeout=10,
        )
        
        if r.status_code >= 400:
            logger.error(f"Failed to archive newsletter: {r.text[:500]}")
            return {}
        
        data = r.json()
        return data[0] if isinstance(data, list) and data else payload
    except Exception as e:
        logger.error(f"Failed to archive newsletter: {e}")
        return {}


# ── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = generate_and_send_newsletter()
    if result:
        print(json.dumps(result, indent=2))
