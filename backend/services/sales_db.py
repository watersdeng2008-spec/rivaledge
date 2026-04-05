"""
Sales database service layer.

CRUD operations for leads, emails, sequences, and engagement.
"""
import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key)


# ── Leads CRUD ────────────────────────────────────────────────────────────────

def create_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new lead.
    
    Args:
        lead_data: Lead information
        
    Returns:
        Created lead with ID
    """
    try:
        # Calculate initial priority score
        score = calculate_priority_score(lead_data)
        lead_data["priority_score"] = score
        
        result = supabase.table("leads").insert(lead_data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise Exception("No data returned from insert")
            
    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        raise


def get_lead(lead_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a lead by ID.
    
    Args:
        lead_id: UUID of the lead
        
    Returns:
        Lead data or None if not found
    """
    try:
        result = supabase.table("leads").select("*").eq("id", lead_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Failed to get lead {lead_id}: {e}")
        raise


def get_lead_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a lead by email address.
    
    Args:
        email: Email address
        
    Returns:
        Lead data or None if not found
    """
    try:
        result = supabase.table("leads").select("*").eq("email", email).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Failed to get lead by email {email}: {e}")
        raise


def get_leads(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Get leads with optional filtering.
    
    Args:
        filters: Optional filters (status, source, min_score)
        limit: Max number of results
        offset: Pagination offset
        
    Returns:
        List of leads
    """
    try:
        query = supabase.table("leads").select("*")
        
        # Apply filters
        if filters:
            if "status" in filters:
                query = query.eq("status", filters["status"])
            if "source" in filters:
                query = query.eq("source", filters["source"])
            if "min_score" in filters:
                query = query.gte("priority_score", filters["min_score"])
        
        # Order by priority score descending, then created_at
        query = query.order("priority_score", desc=True).order("created_at", desc=True)
        
        # Pagination
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        return result.data or []
        
    except Exception as e:
        logger.error(f"Failed to get leads: {e}")
        raise


def update_lead(lead_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a lead.
    
    Args:
        lead_id: UUID of the lead
        update_data: Fields to update
        
    Returns:
        Updated lead
    """
    try:
        # Recalculate score if relevant fields changed
        if any(field in update_data for field in ["title", "company_size", "industry"]):
            # Get current lead data
            current = get_lead(lead_id)
            if current:
                merged = {**current, **update_data}
                update_data["priority_score"] = calculate_priority_score(merged)
        
        result = supabase.table("leads").update(update_data).eq("id", lead_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            raise Exception("No data returned from update")
            
    except Exception as e:
        logger.error(f"Failed to update lead {lead_id}: {e}")
        raise


def delete_lead(lead_id: str) -> bool:
    """
    Delete a lead.
    
    Args:
        lead_id: UUID of the lead
        
    Returns:
        True if deleted
    """
    try:
        result = supabase.table("leads").delete().eq("id", lead_id).execute()
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete lead {lead_id}: {e}")
        raise


# ── Priority Scoring ──────────────────────────────────────────────────────────

def calculate_priority_score(lead_data: Dict[str, Any]) -> int:
    """
    Calculate priority score (0-100) based on ICP fit.
    
    Scoring:
    - Company size 10-200: +20
    - Title VP/CEO/Product/Founder: +30
    - Industry SaaS/B2B software: +20
    - Email found: +10
    - Company website present: +10
    - LinkedIn URL present: +10
    """
    score = 0
    
    # Company size
    company_size = lead_data.get("company_size", "")
    if company_size in ["11-50", "51-200"]:
        score += 20
    elif company_size in ["1-10", "201-500"]:
        score += 10
    
    # Title
    title = (lead_data.get("title") or "").lower()
    if any(t in title for t in ["vp", "vice president", "ceo", "founder", "cto", "head of", "director"]):
        score += 30
    elif any(t in title for t in ["product", "strategy", "growth", "marketing"]):
        score += 20
    
    # Industry
    industry = (lead_data.get("industry") or "").lower()
    if any(i in industry for i in ["saas", "software", "b2b", "technology", "tech"]):
        score += 20
    
    # Data completeness
    if lead_data.get("email"):
        score += 10
    if lead_data.get("company_website"):
        score += 10
    if lead_data.get("linkedin_url"):
        score += 10
    
    return min(score, 100)


# ── Statistics ─────────────────────────────────────────────────────────────────

def get_lead_stats() -> Dict[str, Any]:
    """
    Get lead statistics.
    
    Returns:
        Stats dict with counts by status, source, etc.
    """
    try:
        # Total leads
        total_result = supabase.table("leads").select("count", count="exact").execute()
        total = total_result.count if hasattr(total_result, 'count') else 0
        
        # By status
        status_counts = {}
        for status in ["new", "enriched", "personalized", "contacted", "replied", "qualified", "disqualified", "converted"]:
            result = supabase.table("leads").select("count", count="exact").eq("status", status).execute()
            count = result.count if hasattr(result, 'count') else 0
            if count > 0:
                status_counts[status] = count
        
        # High priority leads (score >= 70)
        high_priority_result = supabase.table("leads").select("count", count="exact").gte("priority_score", 70).execute()
        high_priority = high_priority_result.count if hasattr(high_priority_result, 'count') else 0
        
        return {
            "total_leads": total,
            "by_status": status_counts,
            "high_priority": high_priority,
        }
        
    except Exception as e:
        logger.error(f"Failed to get lead stats: {e}")
        raise
