"""
Hunter.io API Client

Find email addresses by domain and name.
"""
import os
import logging
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)

HUNTER_BASE_URL = "https://api.hunter.io/v2"


class HunterClient:
    """Client for Hunter.io email finder API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("HUNTER_API_KEY", "")
        
        if not self.api_key:
            logger.warning("HUNTER_API_KEY not set")
    
    def find_email(
        self,
        domain: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Find email address for a person.
        
        Args:
            domain: Company domain (e.g., "stripe.com")
            first_name: First name
            last_name: Last name
            full_name: Full name (alternative to first/last)
            
        Returns:
            Email address if found
        """
        if not self.api_key:
            logger.error("Hunter API key not configured")
            return None
        
        params = {
            "domain": domain,
            "api_key": self.api_key,
        }
        
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if full_name:
            params["full_name"] = full_name
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{HUNTER_BASE_URL}/email-finder",
                    params=params,
                )
                response.raise_for_status()
                
                data = response.json()
                email = data.get("data", {}).get("email")
                
                if email:
                    logger.info(f"Found email via Hunter: {email}")
                    return email
                else:
                    logger.info(f"No email found for {first_name} {last_name} @ {domain}")
                    return None
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"Hunter API error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Hunter request failed: {e}")
            return None
    
    def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Verify if an email address is valid.
        
        Args:
            email: Email to verify
            
        Returns:
            Verification result
        """
        if not self.api_key:
            return {"valid": False, "error": "API key not configured"}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{HUNTER_BASE_URL}/email-verifier",
                    params={"email": email, "api_key": self.api_key},
                )
                response.raise_for_status()
                
                return response.json().get("data", {})
                
        except Exception as e:
            logger.error(f"Email verification failed: {e}")
            return {"valid": False, "error": str(e)}
    
    def domain_search(self, domain: str, limit: int = 10) -> list:
        """
        Search for all emails at a domain.
        
        Args:
            domain: Company domain
            limit: Max results
            
        Returns:
            List of email addresses
        """
        if not self.api_key:
            return []
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{HUNTER_BASE_URL}/domain-search",
                    params={
                        "domain": domain,
                        "api_key": self.api_key,
                        "limit": limit,
                    },
                )
                response.raise_for_status()
                
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                
                return [e.get("value") for e in emails if e.get("value")]
                
        except Exception as e:
            logger.error(f"Domain search failed: {e}")
            return []


# Convenience function
def find_email(
    domain: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    full_name: Optional[str] = None,
) -> Optional[str]:
    """Quick email finder."""
    client = HunterClient()
    return client.find_email(domain, first_name, last_name, full_name)
