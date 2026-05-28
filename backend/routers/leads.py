"""
Leads router — capture website leads from interactive forms.
"""
import logging
import os
from typing import Optional

import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()


class LeadCaptureRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    company_url: Optional[str] = Field(None, max_length=500)
    competitor_url: Optional[str] = Field(None, max_length=500)
    capture_source: str = Field(..., pattern="^(homepage|pricing|exit_intent|demo|geo_audit)$")


class LeadCaptureResponse(BaseModel):
    success: bool
    message: str
    lead_id: Optional[str] = None


async def send_welcome_email(name: str, email: str, competitor_url: Optional[str]):
    """Send welcome email via Resend."""
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set, skipping welcome email")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
        }
        
        # Personalize based on competitor
        competitor_section = ""
        if competitor_url:
            competitor_section = f"""
<p>We're already analyzing <strong>{competitor_url}</strong> for you. Here's what our AI found:</p>

<ul>
  <li>📊 Pricing changes tracked automatically</li>
  <li>📝 Product updates monitored weekly</li>
  <li>🎯 Battle cards generated on-demand</li>
</ul>
"""
        
        payload = {
            "from": "ben.d@rivaledge.ai",
            "to": email,
            "subject": f"{name}, your competitor analysis is ready",
            "html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to RivalEdge</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1e293b; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #3b82f6; margin: 0;">RivalEdge</h1>
    <p style="color: #64748b; margin: 5px 0 0;">AI-powered competitive intelligence</p>
  </div>
  
  <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
    <h2 style="margin-top: 0; color: #1e293b;">Hi {name},</h2>
    <p>Thanks for checking out RivalEdge! Here's what you can do next:</p>
    
    {competitor_section}
    
    <div style="background: white; border-radius: 8px; padding: 16px; margin: 20px 0; border: 1px solid #e2e8f0;">
      <h3 style="margin-top: 0; color: #3b82f6;">🚀 Start your free trial</h3>
      <p style="margin-bottom: 16px;">Track up to 3 competitors free for 14 days. No credit card required.</p>
      <a href="https://rivaledge.ai/sign-up" style="display: inline-block; background: #3b82f6; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">Start Free Trial →</a>
    </div>
    
    <div style="background: white; border-radius: 8px; padding: 16px; border: 1px solid #e2e8f0;">
      <h3 style="margin-top: 0; color: #8b5cf6;">📊 See a live demo</h3>
      <p style="margin-bottom: 16px;">Watch how RivalEdge tracks competitors in real-time.</p>
      <a href="https://rivaledge.ai/demo" style="display: inline-block; background: #8b5cf6; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">View Demo →</a>
    </div>
  </div>
  
  <p style="color: #64748b; font-size: 14px;">Questions? Just reply to this email — I read every one.</p>
  
  <p style="color: #64748b; font-size: 14px;">
    — Ben D<br>
    Co-founder, RivalEdge
  </p>
  
  <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
  <p style="color: #94a3b8; font-size: 12px; text-align: center;">
    RivalEdge · Aether Holding LLC<br>
    <a href="https://rivaledge.ai" style="color: #94a3b8;">rivaledge.ai</a>
  </p>
</body>
</html>""",
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers=headers,
            )
            if response.status_code == 200:
                logger.info("Welcome email sent to %s", email)
                return True
            else:
                logger.error("Failed to send welcome email: %s", response.text)
                return False
    except Exception as e:
        logger.error("Error sending welcome email: %s", e)
        return False


@router.post("/capture", response_model=LeadCaptureResponse)
async def capture_lead(
    body: LeadCaptureRequest,
    request: Request,
):
    """Capture a lead from the website and send welcome email."""
    
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Get UTM params from request
    utm_source = request.query_params.get("utm_source")
    utm_medium = request.query_params.get("utm_medium")
    utm_campaign = request.query_params.get("utm_campaign")
    
    lead_id = None
    
    # Save to Supabase
    if supabase_url and supabase_key:
        try:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }
            payload = {
                "name": body.name,
                "email": body.email,
                "company_name": body.company_name,
                "company_url": body.company_url,
                "competitor_url": body.competitor_url,
                "capture_source": body.capture_source,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{supabase_url}/rest/v1/lead_captures",
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code == 201:
                    data = response.json()
                    if data and len(data) > 0:
                        lead_id = data[0].get("id")
                    logger.info(
                        "Lead captured: email=%s source=%s",
                        body.email,
                        body.capture_source,
                    )
                else:
                    logger.error("Failed to save lead: %s", response.text)
        except Exception as e:
            logger.error("Error saving lead: %s", e)
    
    # Send welcome email
    email_sent = await send_welcome_email(body.name, body.email, body.competitor_url)
    
    # Update email_sent status if we have the lead_id
    if lead_id and supabase_url and supabase_key:
        try:
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=5) as client:
                await client.patch(
                    f"{supabase_url}/rest/v1/lead_captures?id=eq.{lead_id}",
                    json={
                        "email_sent": email_sent,
                        "email_sent_at": "now()" if email_sent else None,
                    },
                    headers=headers,
                )
        except Exception as e:
            logger.error("Error updating email status: %s", e)
    
    return LeadCaptureResponse(
        success=True,
        message="Thanks! Check your email for next steps.",
        lead_id=lead_id,
    )


class NewsletterSignupRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    source: str = Field(default="website", max_length=100)


@router.post("/newsletter")
async def newsletter_signup(body: NewsletterSignupRequest):
    """Subscribe to the GEO + CI Insights newsletter."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not supabase_url or not supabase_key:
        return {"success": False, "error": "Supabase not configured"}
    
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        payload = {
            "email": body.email,
            "source": body.source,
            "is_active": True,
            "subscribed_at": datetime.now().isoformat(),
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{supabase_url}/rest/v1/newsletter_subscribers",
                json=payload,
                headers=headers,
            )
            
            if response.status_code in (200, 201):
                logger.info("Newsletter signup: %s from %s", body.email, body.source)
                return {"success": True, "message": "Subscribed successfully"}
            elif response.status_code == 409:
                # Already exists — update to active
                await client.patch(
                    f"{supabase_url}/rest/v1/newsletter_subscribers?email=eq.{body.email}",
                    json={"is_active": True},
                    headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}", "Content-Type": "application/json"},
                )
                return {"success": True, "message": "Already subscribed — reactivated"}
            else:
                logger.error("Newsletter signup failed: %s", response.text)
                return {"success": False, "error": "Failed to subscribe"}
    except Exception as e:
        logger.error("Newsletter signup error: %s", e)
        return {"success": False, "error": str(e)}


@router.get("/capture/stats")
async def get_lead_stats():
    """Get lead capture statistics (admin endpoint)."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not supabase_url or not supabase_key:
        return {"error": "Supabase not configured"}
    
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            # Total leads
            total_response = await client.get(
                f"{supabase_url}/rest/v1/lead_captures?select=count",
                headers=headers,
            )
            
            # By source
            source_response = await client.get(
                f"{supabase_url}/rest/v1/lead_captures?select=capture_source,count",
                headers=headers,
            )
            
            # Recent leads (last 7 days)
            recent_response = await client.get(
                f"{supabase_url}/rest/v1/lead_captures?select=*&created_at=gte.{(datetime.now() - timedelta(days=7)).isoformat()}&order=created_at.desc",
                headers=headers,
            )
            
            return {
                "total": total_response.json()[0]["count"] if total_response.status_code == 200 else 0,
                "by_source": source_response.json() if source_response.status_code == 200 else [],
                "recent": recent_response.json() if recent_response.status_code == 200 else [],
            }
    except Exception as e:
        logger.error("Error getting lead stats: %s", e)
        return {"error": str(e)}
