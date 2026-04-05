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
