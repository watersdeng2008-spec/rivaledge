"""
Camofox Research Agent

Replaces Apollo.io for LinkedIn lead research.
Uses Camofox anti-detection browser to scrape LinkedIn profiles.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from services.camofox_client import CamofoxClient, get_camofox_client
from services.sales_db import create_lead, get_lead_by_email
from services.entity_detector import enrich_lead

logger = logging.getLogger(__name__)


@dataclass
class LinkedInLead:
    """Structured LinkedIn lead data."""
    name: str
    title: str
    company: str
    linkedin_url: str
    email: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    source: str = "camofox_linkedin"


class CamofoxResearchAgent:
    """
    Research agent using Camofox for LinkedIn scraping.
    
    Replaces Apollo.io for lead discovery.
    """
    
    def __init__(self):
        self.camofox: Optional[CamofoxClient] = None
        self._init_camofox()
    
    def _init_camofox(self):
        """Initialize Camofox client if available."""
        try:
            self.camofox = get_camofox_client()
            if self.camofox.health_check():
                logger.info("Camofox research agent initialized")
            else:
                logger.warning("Camofox server not available")
                self.camofox = None
        except Exception as e:
            logger.warning(f"Camofox not available: {e}")
            self.camofox = None
    
    def is_available(self) -> bool:
        """Check if Camofox is available for research."""
        return self.camofox is not None
    
    def search_linkedin(
        self,
        titles: List[str],
        industries: Optional[List[str]] = None,
        company_size: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 50,
    ) -> List[LinkedInLead]:
        """
        Search LinkedIn for leads matching criteria.
        
        Args:
            titles: Job titles to search for (e.g., ["VP Product", "CEO"])
            industries: Industry filters (optional)
            company_size: Company size filter (optional)
            location: Location filter (optional)
            limit: Max results
            
        Returns:
            List of LinkedInLead objects
        """
        if not self.camofox:
            logger.error("Camofox not available")
            return []
        
        leads = []
        
        # Build search query
        title_query = " OR ".join([f'"{t}"' for t in titles])
        query = f"({title_query})"
        
        if industries:
            query += f" ({' OR '.join(industries)})"
        if location:
            query += f" {location}"
        
        logger.info(f"Searching LinkedIn: {query}")
        
        try:
            # Search LinkedIn
            result = self.camofox.search_linkedin(query)
            
            # Extract leads from search results
            # This is simplified — actual implementation would parse the snapshot
            snapshot = result.get("snapshot", {})
            leads = self._parse_search_results(snapshot, limit)
            
            logger.info(f"Found {len(leads)} leads from LinkedIn search")
            return leads
            
        except Exception as e:
            logger.error(f"LinkedIn search failed: {e}")
            return []
    
    def scrape_profile(self, linkedin_url: str) -> Optional[LinkedInLead]:
        """
        Scrape a single LinkedIn profile.
        
        Args:
            linkedin_url: Full LinkedIn profile URL
            
        Returns:
            LinkedInLead if successful
        """
        if not self.camofox:
            logger.error("Camofox not available")
            return None
        
        try:
            logger.info(f"Scraping LinkedIn profile: {linkedin_url}")
            
            profile_data = self.camofox.scrape_linkedin_profile(linkedin_url)
            
            lead = LinkedInLead(
                name=profile_data.get("name", ""),
                title=profile_data.get("headline", ""),
                company=self._extract_company_from_headline(profile_data.get("headline", "")),
                linkedin_url=linkedin_url,
            )
            
            return lead
            
        except Exception as e:
            logger.error(f"Failed to scrape profile {linkedin_url}: {e}")
            return None
    
    def enrich_and_create_lead(self, linkedin_lead: LinkedInLead) -> Optional[str]:
        """
        Enrich LinkedIn lead with email and create in database.
        
        Args:
            linkedin_lead: Lead from LinkedIn scraping
            
        Returns:
            Lead ID if created
        """
        try:
            # Check if lead already exists
            existing = get_lead_by_linkedin(linkedin_lead.linkedin_url)
            if existing:
                logger.info(f"Lead already exists: {linkedin_lead.linkedin_url}")
                return existing.get("id")
            
            # Find email using Hunter.io
            email = self._find_email(linkedin_lead)
            
            # Build lead data
            lead_data = {
                "name": linkedin_lead.name,
                "title": linkedin_lead.title,
                "company": linkedin_lead.company,
                "linkedin_url": linkedin_lead.linkedin_url,
                "email": email,
                "industry": linkedin_lead.industry,
                "company_size": linkedin_lead.company_size,
                "source": linkedin_lead.source,
                "status": "new",
            }
            
            # Enrich with entity detector
            lead_data = enrich_lead(lead_data)
            
            # Create lead
            created = create_lead(lead_data)
            logger.info(f"Created lead: {created.get('id')} - {linkedin_lead.name}")
            
            return created.get("id")
            
        except Exception as e:
            logger.error(f"Failed to create lead: {e}")
            return None
    
    def _parse_search_results(self, snapshot: Dict[str, Any], limit: int) -> List[LinkedInLead]:
        """
        Parse LinkedIn search results from snapshot.
        
        This is a placeholder — actual parsing depends on LinkedIn's structure.
        """
        leads = []
        
        # Extract profile links from snapshot
        # This would parse the accessibility tree to find profile cards
        # For now, return empty list — implement based on actual LinkedIn structure
        
        logger.warning("LinkedIn search parsing not fully implemented")
        return leads
    
    def _extract_company_from_headline(self, headline: str) -> str:
        """Extract company name from LinkedIn headline."""
        # Common pattern: "Title at Company" or "Title | Company"
        import re
        
        patterns = [
            r'at\s+([^|]+)',
            r'\|\s*([^|]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, headline, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _find_email(self, lead: LinkedInLead) -> Optional[str]:
        """
        Find email for lead using Hunter.io.
        
        Args:
            lead: LinkedIn lead with company info
            
        Returns:
            Email if found
        """
        try:
            from services.hunter_client import find_email
            
            if not lead.company:
                return None
            
            # Guess domain from company name
            domain = self._company_to_domain(lead.company)
            if not domain:
                return None
            
            # Use Hunter.io to find email
            email = find_email(
                domain=domain,
                first_name=lead.name.split()[0] if lead.name else None,
                last_name=lead.name.split()[-1] if lead.name and len(lead.name.split()) > 1 else None,
            )
            
            return email
            
        except Exception as e:
            logger.warning(f"Failed to find email for {lead.name}: {e}")
            return None
    
    def _company_to_domain(self, company: str) -> Optional[str]:
        """Convert company name to likely domain."""
        # Simple conversion: "Stripe" -> "stripe.com"
        import re
        
        # Clean company name
        domain = re.sub(r'[^\w\s]', '', company).lower().replace(' ', '')
        
        # Common TLDs to try
        tlds = ['.com', '.io', '.co', '.ai']
        
        # For now, just return .com version
        # In production, would verify domain exists
        return f"{domain}.com"


def get_camofox_research_agent() -> CamofoxResearchAgent:
    """Get configured Camofox research agent."""
    return CamofoxResearchAgent()


# Helper function for sales_db
def get_lead_by_linkedin(linkedin_url: str) -> Optional[Dict[str, Any]]:
    """Find lead by LinkedIn URL."""
    from services.sales_db import get_supabase
    
    try:
        supabase = get_supabase()
        result = supabase.table("leads")\
            .select("*")\
            .eq("linkedin_url", linkedin_url)\
            .single()\
            .execute()
        
        return result.data
    except Exception:
        return None
