"""
Camofox API Router

Endpoints for LinkedIn research using Camofox browser.
Replaces Apollo.io for lead discovery.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

from auth import get_current_user
from services.camofox_research import get_camofox_research_agent, LinkedInLead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/camofox", tags=["Camofox Research"])


# ── Pydantic Models ───────────────────────────────────────────────────────────

class LinkedInSearchRequest(BaseModel):
    titles: List[str]
    industries: Optional[List[str]] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    limit: int = 50


class LinkedInSearchResponse(BaseModel):
    success: bool
    leads_found: int
    leads: List[dict]
    message: Optional[str] = None


class ProfileScrapeRequest(BaseModel):
    linkedin_url: str
    auto_create: bool = True


class ProfileScrapeResponse(BaseModel):
    success: bool
    lead: Optional[dict] = None
    lead_id: Optional[str] = None
    message: Optional[str] = None


class CamofoxStatusResponse(BaseModel):
    available: bool
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/status", response_model=CamofoxStatusResponse)
def get_camofox_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Check if Camofox browser is available.
    """
    try:
        agent = get_camofox_research_agent()
        available = agent.is_available()
        
        return CamofoxStatusResponse(
            available=available,
            message="Camofox is ready" if available else "Camofox server not available",
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return CamofoxStatusResponse(
            available=False,
            message=f"Error: {str(e)}",
        )


@router.post("/search/linkedin", response_model=LinkedInSearchResponse)
def search_linkedin(
    request: LinkedInSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Search LinkedIn for leads.
    
    Replaces Apollo.io search. Requires Camofox server running.
    """
    try:
        agent = get_camofox_research_agent()
        
        if not agent.is_available():
            raise HTTPException(
                status_code=503,
                detail="Camofox server not available. Please deploy Camofox first.",
            )
        
        leads = agent.search_linkedin(
            titles=request.titles,
            industries=request.industries,
            company_size=request.company_size,
            location=request.location,
            limit=request.limit,
        )
        
        # Convert to dict for response
        leads_data = [
            {
                "name": lead.name,
                "title": lead.title,
                "company": lead.company,
                "linkedin_url": lead.linkedin_url,
                "email": lead.email,
            }
            for lead in leads
        ]
        
        return LinkedInSearchResponse(
            success=True,
            leads_found=len(leads),
            leads=leads_data,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LinkedIn search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/profile", response_model=ProfileScrapeResponse)
def scrape_profile(
    request: ProfileScrapeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Scrape a single LinkedIn profile.
    
    Args:
        linkedin_url: Full LinkedIn profile URL
        auto_create: Automatically create lead in database
    """
    try:
        agent = get_camofox_research_agent()
        
        if not agent.is_available():
            raise HTTPException(
                status_code=503,
                detail="Camofox server not available",
            )
        
        lead = agent.scrape_profile(request.linkedin_url)
        
        if not lead:
            return ProfileScrapeResponse(
                success=False,
                message="Failed to scrape profile",
            )
        
        lead_data = {
            "name": lead.name,
            "title": lead.title,
            "company": lead.company,
            "linkedin_url": lead.linkedin_url,
        }
        
        # Create lead in database if requested
        lead_id = None
        if request.auto_create:
            lead_id = agent.enrich_and_create_lead(lead)
        
        return ProfileScrapeResponse(
            success=True,
            lead=lead_data,
            lead_id=lead_id,
            message="Profile scraped successfully" + (" and lead created" if lead_id else ""),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-cookies")
def import_linkedin_cookies(
    cookie_content: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Import LinkedIn cookies for authenticated scraping.
    
    Requires Netscape-format cookies.txt file content.
    """
    try:
        from services.camofox_client import get_camofox_client
        
        client = get_camofox_client()
        
        # Save cookies to temp file and import
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(cookie_content)
            temp_path = f.name
        
        try:
            success = client.import_cookies(temp_path, "linkedin.com")
            
            if success:
                return {"success": True, "message": "LinkedIn cookies imported successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to import cookies")
                
        finally:
            os.unlink(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cookie import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/linkedin")
def get_linkedin_leads(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Get leads sourced from LinkedIn/Camofox.
    """
    try:
        from services.sales_db import get_supabase
        
        supabase = get_supabase()
        
        query = supabase.table("leads")\
            .select("*")\
            .eq("source", "camofox_linkedin")\
            .order("created_at", desc=True)\
            .limit(limit)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "count": len(result.data),
            "leads": result.data,
        }
        
    except Exception as e:
        logger.error(f"Failed to get LinkedIn leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
