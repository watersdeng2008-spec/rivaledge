"""
Entity Detector — extracts structured data from unstructured text

Uses:
1. Regex for emails, URLs, phone numbers
2. LLM (Qwen/free) for names, companies, roles, industries
3. Firecrawl for website scraping when needed
"""
import re
import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from services.ai import research_lead

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntities:
    """Structured entities extracted from text."""
    person_name: Optional[str] = None
    person_role: Optional[str] = None
    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    emails: List[str] = None
    urls: List[str] = None
    phone_numbers: List[str] = None
    
    def __post_init__(self):
        if self.emails is None:
            self.emails = []
        if self.urls is None:
            self.urls = []
        if self.phone_numbers is None:
            self.phone_numbers = []


class EntityDetector:
    """
    Extract entities from text using regex + LLM.
    
    Pattern:
    1. Regex extraction for structured data (emails, URLs, phones)
    2. LLM extraction for semantic data (names, roles, companies)
    """
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    URL_PATTERN = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?')
    PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b')
    
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    
    def extract_from_text(self, text: str, context: str = "") -> ExtractedEntities:
        """
        Extract all entities from text.
        
        Args:
            text: Raw text to analyze
            context: Additional context (e.g., "LinkedIn profile", "email signature")
            
        Returns:
            ExtractedEntities with all found data
        """
        entities = ExtractedEntities()
        
        # Step 1: Regex extraction
        entities.emails = self._extract_emails(text)
        entities.urls = self._extract_urls(text)
        entities.phone_numbers = self._extract_phones(text)
        
        # Step 2: LLM extraction for semantic data
        semantic = self._extract_semantic(text, context)
        entities.person_name = semantic.get("person_name")
        entities.person_role = semantic.get("person_role")
        entities.company_name = semantic.get("company_name")
        entities.company_industry = semantic.get("company_industry")
        entities.company_size = semantic.get("company_size")
        
        return entities
    
    def extract_from_email(self, email: str, name: str = "") -> ExtractedEntities:
        """
        Extract entities from an email address.
        
        Attempts to infer company from domain.
        """
        entities = ExtractedEntities()
        entities.emails = [email]
        
        # Extract domain
        if "@" in email:
            domain = email.split("@")[1]
            entities.urls = [f"https://{domain}"]
            
            # Try to infer company name from domain
            company_guess = self._domain_to_company(domain)
            if company_guess:
                entities.company_name = company_guess
        
        # If name provided, parse it
        if name:
            name_parts = name.strip().split()
            if len(name_parts) >= 2:
                entities.person_name = name
        
        return entities
    
    def extract_from_linkedin_headline(self, headline: str, name: str = "") -> ExtractedEntities:
        """
        Extract entities from LinkedIn headline.
        
        Example: "VP Product at Stripe | Fintech | San Francisco"
        """
        entities = ExtractedEntities()
        entities.person_name = name if name else None
        
        # Use LLM to parse headline
        prompt = f"""Extract structured information from this LinkedIn headline:

Headline: "{headline}"

Return ONLY a JSON object with these fields (use null if not found):
- person_role: their job title/role
- company_name: company they work at
- company_industry: industry if mentioned

Example output:
{{"person_role": "VP Product", "company_name": "Stripe", "company_industry": "Fintech"}}"""
        
        try:
            result = research_lead(prompt, max_tokens=200)
            # Parse JSON from result
            import json
            data = json.loads(result.strip())
            entities.person_role = data.get("person_role")
            entities.company_name = data.get("company_name")
            entities.company_industry = data.get("company_industry")
        except Exception as e:
            logger.warning(f"Failed to parse LinkedIn headline: {e}")
        
        return entities
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        return list(set(self.EMAIL_PATTERN.findall(text)))
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        return list(set(self.URL_PATTERN.findall(text)))
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        return list(set(self.PHONE_PATTERN.findall(text)))
    
    def _extract_semantic(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Use LLM to extract semantic entities.
        
        Uses Qwen (free) for cost efficiency.
        """
        context_str = f"Context: {context}\n\n" if context else ""
        
        prompt = f"""{context_str}Extract structured information from this text:

""" + text[:2000] + """

Return ONLY a JSON object with these fields (use null if not found):
- person_name: full name of the person
- person_role: their job title/role
- company_name: company name
- company_industry: industry (e.g., SaaS, Fintech, Healthcare)
- company_size: company size if mentioned (e.g., "11-50", "500+")

Example output:
{"person_name": "Sarah Chen", "person_role": "VP Product", "company_name": "Stripe", "company_industry": "Fintech", "company_size": null}"""
        
        try:
            result = research_lead(prompt, max_tokens=300)
            import json
            # Extract JSON from response
            json_match = re.search(r'\{[^}]*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}")
            return {}
    
    def _domain_to_company(self, domain: str) -> Optional[str]:
        """
        Try to infer company name from domain.
        
        Example: stripe.com -> Stripe
        """
        # Remove TLD
        parts = domain.split('.')
        if len(parts) >= 2:
            name = parts[-2]
            # Capitalize and clean
            name = name.replace('-', ' ').replace('_', ' ')
            return name.title()
        return None
    
    def enrich_from_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape website and extract company info.
        
        Uses Firecrawl if API key is available.
        """
        if not self.firecrawl_api_key:
            logger.warning("No Firecrawl API key, skipping website enrichment")
            return {}
        
        try:
            # Use Firecrawl to scrape
            import requests
            
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {self.firecrawl_api_key}"},
                json={"url": url, "formats": ["markdown"]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                markdown = data.get("data", {}).get("markdown", "")
                
                # Extract entities from scraped content
                entities = self.extract_from_text(markdown, context="Company website")
                
                return {
                    "company_name": entities.company_name,
                    "company_industry": entities.company_industry,
                    "company_size": entities.company_size,
                    "description": markdown[:500] if markdown else None,
                }
            else:
                logger.warning(f"Firecrawl failed: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Website enrichment failed: {e}")
            return {}


# Convenience function
def detect_entities(text: str, context: str = "") -> ExtractedEntities:
    """Quick entity detection from text."""
    detector = EntityDetector()
    return detector.extract_from_text(text, context)


def enrich_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich lead data with entity detection.
    
    Args:
        lead_data: Dict with email, name, linkedin_url, etc.
        
    Returns:
        Enriched lead data
    """
    detector = EntityDetector()
    
    email = lead_data.get("email", "")
    name = lead_data.get("name", "")
    linkedin = lead_data.get("linkedin_url", "")
    
    # Start with email extraction
    entities = detector.extract_from_email(email, name)
    
    # If LinkedIn headline available, extract more
    headline = lead_data.get("linkedin_headline", "")
    if headline:
        linkedin_entities = detector.extract_from_linkedin_headline(headline, name)
        # Merge (LinkedIn data is more reliable)
        if linkedin_entities.person_role:
            entities.person_role = linkedin_entities.person_role
        if linkedin_entities.company_name:
            entities.company_name = linkedin_entities.company_name
        if linkedin_entities.company_industry:
            entities.company_industry = linkedin_entities.company_industry
    
    # Try website enrichment if we have a URL
    if entities.urls:
        website_data = detector.enrich_from_website(entities.urls[0])
        if website_data.get("company_name") and not entities.company_name:
            entities.company_name = website_data["company_name"]
        if website_data.get("company_industry") and not entities.company_industry:
            entities.company_industry = website_data["company_industry"]
    
    # Return enriched data
    return {
        "name": entities.person_name or name,
        "title": entities.person_role or lead_data.get("title"),
        "company": entities.company_name or lead_data.get("company"),
        "industry": entities.company_industry or lead_data.get("industry"),
        "company_size": entities.company_size or lead_data.get("company_size"),
        "email": entities.emails[0] if entities.emails else email,
        "website": entities.urls[0] if entities.urls else None,
    }
