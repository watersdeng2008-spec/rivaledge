"""
Instantly.ai API v2 Client

Complete client for Instantly API v2 based on patterns from instantly-mcp-python.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

INSTANTLY_BASE_URL = "https://api.instantly.ai/api/v2"


class InstantlyClient:
    """Client for Instantly.ai API v2."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("INSTANTLY_API_KEY", "")
        self.base_url = INSTANTLY_BASE_URL
        
        if not self.api_key:
            logger.warning("INSTANTLY_API_KEY not set")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to Instantly API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=json_data,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Instantly API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Instantly request failed: {e}")
            raise
    
    # ── Campaigns ────────────────────────────────────────────────────────────
    
    def create_campaign(
        self,
        name: str,
        email_account_ids: List[str],
        sequence_steps: List[Dict[str, Any]],
    ) -> str:
        """
        Create a new email campaign.
        
        Args:
            name: Campaign name
            email_account_ids: List of email account IDs to send from
            sequence_steps: List of {subject, body, delay_days} dicts
            
        Returns:
            Campaign ID
        """
        payload = {
            "name": name,
            "email_account_ids": email_account_ids,
            "sequences": [
                {
                    "subject": step["subject"],
                    "body": step["body"],
                    "delay": step.get("delay_days", 0) * 24 * 60,  # Convert to minutes
                }
                for step in sequence_steps
            ],
        }
        
        result = self._request("POST", "/campaigns", json_data=payload)
        campaign_id = result.get("id")
        logger.info(f"Created campaign: {campaign_id}")
        return campaign_id
    
    def activate_campaign(self, campaign_id: str) -> bool:
        """Activate (start) a campaign."""
        try:
            self._request("POST", f"/campaigns/{campaign_id}/activate")
            logger.info(f"Activated campaign: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate campaign: {e}")
            return False
    
    def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a campaign."""
        try:
            self._request("POST", f"/campaigns/{campaign_id}/pause")
            logger.info(f"Paused campaign: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return False
    
    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details."""
        return self._request("GET", f"/campaigns/{campaign_id}")
    
    def list_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List campaigns."""
        result = self._request("GET", "/campaigns", params={"limit": limit})
        return result.get("items", [])
    
    # ── Leads ────────────────────────────────────────────────────────────────
    
    def create_lead(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        custom_variables: Optional[Dict] = None,
    ) -> str:
        """
        Create a single lead.
        
        Returns:
            Lead ID
        """
        payload = {"email": email}
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if company:
            payload["company"] = company
        if custom_variables:
            payload["custom_variables"] = custom_variables
        
        result = self._request("POST", "/leads", json_data=payload)
        lead_id = result.get("id")
        logger.info(f"Created lead: {lead_id}")
        return lead_id
    
    def add_leads_to_campaign_bulk(
        self,
        campaign_id: str,
        leads: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add up to 1,000 leads to a campaign in bulk.
        
        Args:
            campaign_id: Campaign ID
            leads: List of lead dicts with email, first_name, last_name, company, etc.
            
        Returns:
            API response with import status
        """
        payload = {
            "campaign_id": campaign_id,
            "leads": leads,
        }
        
        result = self._request("POST", "/leads/bulk", json_data=payload)
        logger.info(f"Added {len(leads)} leads to campaign {campaign_id}")
        return result
    
    def list_leads(self, campaign_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List leads, optionally filtered by campaign."""
        params = {"limit": limit}
        if campaign_id:
            params["campaign_id"] = campaign_id
        
        result = self._request("GET", "/leads", params=params)
        return result.get("items", [])
    
    # ── Email Accounts ───────────────────────────────────────────────────────
    
    def list_email_accounts(self) -> List[Dict[str, Any]]:
        """List available email accounts."""
        result = self._request("GET", "/accounts")
        return result.get("items", [])
    
    def get_email_account(self, account_id: str) -> Dict[str, Any]:
        """Get email account details."""
        return self._request("GET", f"/accounts/{account_id}")
    
    # ── Analytics ────────────────────────────────────────────────────────────
    
    def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign analytics (opens, clicks, replies)."""
        return self._request("GET", f"/campaigns/{campaign_id}/analytics")
    
    def test_connection(self) -> bool:
        """Test API connection by listing campaigns."""
        try:
            self.list_campaigns(limit=1)
            logger.info("Instantly API connection successful")
            return True
        except Exception as e:
            logger.error(f"Instantly API connection failed: {e}")
            return False
