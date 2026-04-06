"""
Sales router — API endpoints for sales agent operations.

Handles leads, personalized emails, sequences, and engagement tracking.
"""
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel

from auth import get_current_user
from services.sales_db import (
    create_lead,
    get_lead,
    get_leads,
    update_lead,
    delete_lead,
    get_lead_by_email,
)
from services.research_agent import get_research_agent

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Pydantic Models ───────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    email: str
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    source: str = "manual"
    source_details: Optional[dict] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    priority_score: Optional[int] = None
    pain_signals: Optional[List[str]] = None
    status: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    title: Optional[str]
    company: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    priority_score: int
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Leads Endpoints ───────────────────────────────────────────────────────────

@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead_endpoint(
    lead: LeadCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new sales lead.
    """
    try:
        # Check if lead already exists
        existing = get_lead_by_email(lead.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Lead with email {lead.email} already exists",
            )
        
        new_lead = create_lead(lead.dict())
        return new_lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lead: {str(e)}",
        )


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead_endpoint(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get a single lead by ID.
    """
    try:
        lead = get_lead(lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead {lead_id} not found",
            )
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get lead: {str(e)}",
        )


@router.get("/leads", response_model=List[LeadResponse])
def list_leads_endpoint(
    status: Optional[str] = Query(None, description="Filter by status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum priority score"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user),
):
    """
    List leads with optional filtering.
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        if source:
            filters["source"] = source
        if min_score is not None:
            filters["min_score"] = min_score
        
        leads = get_leads(filters=filters, limit=limit, offset=offset)
        return leads
    except Exception as e:
        logger.error(f"Failed to list leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list leads: {str(e)}",
        )


@router.put("/leads/{lead_id}", response_model=LeadResponse)
def update_lead_endpoint(
    lead_id: str,
    lead_update: LeadUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Update a lead.
    """
    try:
        # Check if lead exists
        existing = get_lead(lead_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead {lead_id} not found",
            )
        
        updated = update_lead(lead_id, lead_update.dict(exclude_unset=True))
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update lead: {str(e)}",
        )


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead_endpoint(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a lead.
    """
    try:
        # Check if lead exists
        existing = get_lead(lead_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead {lead_id} not found",
            )
        
        delete_lead(lead_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete lead: {str(e)}",
        )


# ── Helper function (placeholder for actual implementation) ───────────────────

# ── Research Agent Endpoints ───────────────────────────────────────────────────

class ApolloSearchRequest(BaseModel):
    titles: Optional[List[str]] = None
    company_sizes: Optional[List[str]] = None
    limit: int = 50


@router.post("/research/linkedin")
async def research_linkedin(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Process LinkedIn Sales Navigator CSV export.
    
    Upload a CSV file exported from LinkedIn Sales Navigator.
    Returns list of created lead IDs.
    """
    try:
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Process with Research Agent
        agent = get_research_agent()
        lead_ids = agent.process_linkedin_export(csv_content)
        
        return {
            "success": True,
            "leads_created": len(lead_ids),
            "lead_ids": lead_ids,
        }
        
    except Exception as e:
        logger.error(f"LinkedIn research failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process LinkedIn export: {str(e)}",
        )


@router.post("/research/apollo")
def research_apollo(
    request: ApolloSearchRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Search Apollo.io for leads.
    
    Searches Apollo and creates leads for matching prospects.
    Returns list of created lead IDs.
    """
    try:
        agent = get_research_agent()
        lead_ids = agent.search_apollo(
            titles=request.titles,
            company_sizes=request.company_sizes,
            limit=request.limit,
        )
        
        return {
            "success": True,
            "leads_created": len(lead_ids),
            "lead_ids": lead_ids,
        }
        
    except Exception as e:
        logger.error(f"Apollo research failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search Apollo: {str(e)}",
        )


@router.get("/research/stats")
def get_research_stats(
    current_user: dict = Depends(get_current_user),
):
    """
    Get research statistics.
    
    Returns counts by source, enrichment rates, etc.
    """
    try:
        from services.sales_db import get_lead_stats
        stats = get_lead_stats()
        
        return {
            "success": True,
            "stats": stats,
        }
        
    except Exception as e:
        logger.error(f"Failed to get research stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


# ── Personalization Agent Endpoints ────────────────────────────────────────────

class PersonalizeRequest(BaseModel):
    lead_ids: List[str]


@router.post("/personalize")
def personalize_leads(
    request: PersonalizeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate personalized emails for leads.
    
    Takes lead IDs, drafts personalized emails using AI (Qwen - free).
    Returns list of created email IDs.
    """
    try:
        from services.personalization_agent import get_personalization_agent
        
        agent = get_personalization_agent()
        email_ids = agent.process_leads(request.lead_ids)
        
        return {
            "success": True,
            "emails_created": len(email_ids),
            "email_ids": email_ids,
        }
        
    except Exception as e:
        logger.error(f"Personalization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to personalize: {str(e)}",
        )


@router.get("/emails/pending")
def get_pending_emails(
    min_score: int = Query(6, ge=1, le=10),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Get personalized emails awaiting approval.
    
    Query params:
    - min_score: Minimum personalization score (1-10)
    - limit: Max results
    """
    try:
        from services.sales_db import supabase
        
        result = supabase.table("personalized_emails")\
            .select("*, leads(name, email, company)")\
            .eq("status", "draft")\
            .gte("personalization_score", min_score)\
            .limit(limit)\
            .execute()
        
        return {
            "success": True,
            "emails": result.data,
        }
        
    except Exception as e:
        logger.error(f"Failed to get pending emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get emails: {str(e)}",
        )


@router.post("/emails/{email_id}/approve")
def approve_email(
    email_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Approve a personalized email for sending.
    """
    try:
        from services.sales_db import supabase
        
        result = supabase.table("personalized_emails")\
            .update({
                "status": "approved",
                "reviewed_by": current_user.get("email"),
                "reviewed_at": "now()",
            })\
            .eq("id", email_id)\
            .execute()
        
        return {
            "success": True,
            "email": result.data[0] if result.data else None,
        }
        
    except Exception as e:
        logger.error(f"Failed to approve email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve: {str(e)}",
        )


@router.post("/emails/{email_id}/reject")
def reject_email(
    email_id: str,
    notes: str = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Reject a personalized email.
    """
    try:
        from services.sales_db import supabase
        
        update_data = {
            "status": "rejected",
            "reviewed_by": current_user.get("email"),
            "reviewed_at": "now()",
        }
        if notes:
            update_data["review_notes"] = notes
        
        result = supabase.table("personalized_emails")\
            .update(update_data)\
            .eq("id", email_id)\
            .execute()
        
        return {
            "success": True,
            "email": result.data[0] if result.data else None,
        }
        
    except Exception as e:
        logger.error(f"Failed to reject email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject: {str(e)}",
        )


# ── Outreach Agent Endpoints ──────────────────────────────────────────────────

class SendEmailsRequest(BaseModel):
    email_ids: List[str]


@router.post("/outreach/send")
def send_approved_emails(
    request: SendEmailsRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send approved emails via Instantly.
    
    Takes list of approved email IDs, sends via Instantly API.
    Returns list of sent message IDs.
    """
    try:
        from services.outreach_agent import get_outreach_agent
        
        agent = get_outreach_agent()
        message_ids = agent.process_approved_emails(request.email_ids)
        
        return {
            "success": True,
            "sent_count": len(message_ids),
            "message_ids": message_ids,
        }
        
    except Exception as e:
        logger.error(f"Outreach send failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send: {str(e)}",
        )


@router.post("/outreach/sequence/{lead_id}")
def create_sequence(
    lead_id: str,
    email_id: str,  # Initial email ID
    current_user: dict = Depends(get_current_user),
):
    """
    Create 3-touch follow-up sequence for lead.
    
    Generates follow-up emails and creates sequence in Instantly.
    """
    try:
        from services.outreach_agent import get_outreach_agent
        from services.sales_db import supabase
        
        # Get initial email
        email_result = supabase.table("personalized_emails")\
            .select("*")\
            .eq("id", email_id)\
            .single()\
            .execute()
        
        if not email_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found",
            )
        
        agent = get_outreach_agent()
        sequence_id = agent.create_follow_up_sequence(
            lead_id=lead_id,
            initial_email=email_result.data,
        )
        
        return {
            "success": True,
            "sequence_id": sequence_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create sequence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sequence: {str(e)}",
        )


@router.post("/outreach/webhook")
async def instantly_webhook(
    request: Request,
):
    """
    Webhook endpoint for Instantly events.
    
    Receives open, click, reply events from Instantly.
    Updates database and triggers notifications.
    """
    try:
        from services.outreach_agent import get_outreach_agent
        
        webhook_data = await request.json()
        
        agent = get_outreach_agent()
        success = agent.handle_webhook(webhook_data)
        
        return {
            "success": success,
        }
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        # Return 200 to prevent Instantly from retrying
        return {
            "success": False,
            "error": str(e),
        }


@router.get("/outreach/stats")
def get_outreach_stats(
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user),
):
    """
    Get outreach statistics.
    
    Returns: sent, delivered, opened, clicked, replied counts
    """
    try:
        from services.sales_db import supabase
        
        # Get stats from email_sequences table
        result = supabase.table("email_sequences")\
            .select("status, opened_at, clicked_at, replied_at")\
            .gte("created_at", (datetime.utcnow() - timedelta(days=days)).isoformat())\
            .execute()
        
        emails = result.data or []
        
        stats = {
            "period_days": days,
            "total_sent": len([e for e in emails if e.get("status") == "sent"]),
            "total_opened": len([e for e in emails if e.get("opened_at")]),
            "total_clicked": len([e for e in emails if e.get("clicked_at")]),
            "total_replied": len([e for e in emails if e.get("replied_at")]),
        }
        
        # Calculate rates
        if stats["total_sent"] > 0:
            stats["open_rate"] = round(stats["total_opened"] / stats["total_sent"] * 100, 2)
            stats["click_rate"] = round(stats["total_clicked"] / stats["total_sent"] * 100, 2)
            stats["reply_rate"] = round(stats["total_replied"] / stats["total_sent"] * 100, 2)
        
        return {
            "success": True,
            "stats": stats,
        }
        
    except Exception as e:
        logger.error(f"Failed to get outreach stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


# ── Dashboard Endpoints ───────────────────────────────────────────────────────

@router.get("/dashboard/pipeline")
def get_dashboard_pipeline(
    current_user: dict = Depends(get_current_user),
):
    """
    Get sales pipeline overview.
    
    Returns lead counts by stage and conversion rates.
    """
    try:
        from services.sales_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        overview = dashboard.get_pipeline_overview()
        
        return {
            "success": True,
            "data": overview,
        }
        
    except Exception as e:
        logger.error(f"Failed to get pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipeline: {str(e)}",
        )


@router.get("/dashboard/campaign")
def get_dashboard_campaign(
    days: int = Query(30, ge=1, le=90),
    current_user: dict = Depends(get_current_user),
):
    """
    Get campaign performance metrics.
    
    Query params:
    - days: Analysis period (default: 30)
    
    Returns: open rates, click rates, reply rates
    """
    try:
        from services.sales_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        performance = dashboard.get_campaign_performance(days)
        
        return {
            "success": True,
            "data": performance,
        }
        
    except Exception as e:
        logger.error(f"Failed to get campaign metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign metrics: {str(e)}",
        )


@router.get("/dashboard/templates")
def get_dashboard_templates(
    current_user: dict = Depends(get_current_user),
):
    """
    Get email template effectiveness analysis.
    
    Returns templates ranked by performance.
    """
    try:
        from services.sales_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        effectiveness = dashboard.get_template_effectiveness()
        
        return {
            "success": True,
            "data": effectiveness,
        }
        
    except Exception as e:
        logger.error(f"Failed to get template effectiveness: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template effectiveness: {str(e)}",
        )


@router.get("/dashboard/recommendations")
def get_dashboard_recommendations(
    current_user: dict = Depends(get_current_user),
):
    """
    Get optimization recommendations.
    
    Returns AI-generated recommendations based on performance data.
    """
    try:
        from services.sales_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        recommendations = dashboard.get_optimization_recommendations()
        
        return {
            "success": True,
            "data": recommendations,
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}",
        )


@router.get("/dashboard/hot-leads")
def get_dashboard_hot_leads(
    min_score: int = Query(70, ge=0, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Get hot leads (high priority + engagement).
    
    Query params:
    - min_score: Minimum priority score (default: 70)
    
    Returns: List of hot leads requiring attention.
    """
    try:
        from services.sales_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        hot_leads = dashboard.get_hot_leads(min_score)
        
        return {
            "success": True,
            "count": len(hot_leads),
            "data": hot_leads,
        }
        
    except Exception as e:
        logger.error(f"Failed to get hot leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hot leads: {str(e)}",
        )


@router.get("/dashboard/daily-summary")
def get_daily_summary(
    current_user: dict = Depends(get_current_user),
):
    """
    Get daily summary for founder review.
    
    Returns formatted summary of day's activity.
    """
    try:
        from services.sales_dashboard import get_dashboard
        
        dashboard = get_dashboard()
        summary = dashboard.get_daily_summary()
        
        return {
            "success": True,
            "summary": summary,
        }
        
    except Exception as e:
        logger.error(f"Failed to generate daily summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}",
        )
