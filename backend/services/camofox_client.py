"""
Camofox Browser Client

REST API client for Camofox anti-detection browser.
Used for scraping LinkedIn profiles and other protected sites.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)


class CamofoxClient:
    """
    Client for Camofox browser automation server.
    
    Provides:
    - LinkedIn profile scraping
    - Company website scraping (fallback to Firecrawl)
    - Search macros for common sites
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.environ.get("CAMOFOX_URL", "http://localhost:9377")
        self.api_key = api_key or os.environ.get("CAMOFOX_API_KEY", "")
        
        if not self.api_key:
            logger.warning("CAMOFOX_API_KEY not set — cookie import will be disabled")
    
    def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make request to Camofox API."""
        url = f"{self.base_url}{endpoint}"
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Camofox API error: {e.response.status_code} - {e.response.text[:500]}")
            raise
        except Exception as e:
            logger.error(f"Camofox request failed: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if Camofox server is running."""
        try:
            response = self._request("GET", "/health")
            return response.get("status") == "ok"
        except Exception as e:
            logger.error(f"Camofox health check failed: {e}")
            return False
    
    def create_tab(self, url: Optional[str] = None) -> str:
        """
        Create a new browser tab.
        
        Returns:
            Tab ID
        """
        payload = {}
        if url:
            payload["url"] = url
        
        result = self._request("POST", "/tabs", json_data=payload)
        tab_id = result.get("tab_id")
        logger.info(f"Created Camofox tab: {tab_id}")
        return tab_id
    
    def close_tab(self, tab_id: str) -> bool:
        """Close a browser tab."""
        try:
            self._request("DELETE", f"/tabs/{tab_id}")
            logger.info(f"Closed Camofox tab: {tab_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to close tab {tab_id}: {e}")
            return False
    
    def get_snapshot(self, tab_id: str, screenshot: bool = False) -> Dict[str, Any]:
        """
        Get accessibility snapshot of page.
        
        Args:
            tab_id: Tab ID
            screenshot: Include base64 screenshot
            
        Returns:
            Snapshot with accessibility tree and optional screenshot
        """
        params = {"screenshot": screenshot}
        result = self._request("GET", f"/tabs/{tab_id}/snapshot?{urlencode(params)}")
        return result
    
    def navigate(self, tab_id: str, url: str) -> Dict[str, Any]:
        """Navigate to URL in tab."""
        result = self._request("POST", f"/tabs/{tab_id}/navigate", json_data={"url": url})
        return result
    
    def click(self, tab_id: str, element_ref: str) -> Dict[str, Any]:
        """Click element by reference (e.g., 'e1', 'e2')."""
        result = self._request("POST", f"/tabs/{tab_id}/click", json_data={"element": element_ref})
        return result
    
    def type_text(self, tab_id: str, element_ref: str, text: str) -> Dict[str, Any]:
        """Type text into element."""
        result = self._request(
            "POST",
            f"/tabs/{tab_id}/type",
            json_data={"element": element_ref, "text": text}
        )
        return result
    
    def scroll(self, tab_id: str, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """Scroll page."""
        result = self._request(
            "POST",
            f"/tabs/{tab_id}/scroll",
            json_data={"direction": direction, "amount": amount}
        )
        return result
    
    def search_google(self, query: str) -> Dict[str, Any]:
        """
        Search Google using macro.
        
        Args:
            query: Search query
            
        Returns:
            Search results snapshot
        """
        tab_id = self.create_tab()
        try:
            result = self._request(
                "POST",
                "/macros/google_search",
                json_data={"tab_id": tab_id, "query": query}
            )
            return result
        finally:
            self.close_tab(tab_id)
    
    def search_linkedin(self, query: str) -> Dict[str, Any]:
        """
        Search LinkedIn using macro.
        
        Note: Requires valid LinkedIn cookies to be imported first.
        
        Args:
            query: Search query (e.g., "VP Product SaaS")
            
        Returns:
            Search results snapshot
        """
        tab_id = self.create_tab()
        try:
            result = self._request(
                "POST",
                "/macros/linkedin_search",
                json_data={"tab_id": tab_id, "query": query}
            )
            return result
        finally:
            self.close_tab(tab_id)
    
    def scrape_linkedin_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Scrape a LinkedIn profile.
        
        Note: Requires valid LinkedIn cookies to be imported first.
        
        Args:
            profile_url: Full LinkedIn profile URL
            
        Returns:
            Extracted profile data
        """
        tab_id = self.create_tab(url=profile_url)
        try:
            # Wait for page to load and get snapshot
            import time
            time.sleep(3)  # Allow page to load
            
            snapshot = self.get_snapshot(tab_id)
            
            # Extract profile info from accessibility tree
            profile_data = self._extract_linkedin_profile(snapshot)
            
            return profile_data
            
        finally:
            self.close_tab(tab_id)
    
    def _extract_linkedin_profile(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from LinkedIn profile snapshot.
        
        This is a basic extractor — can be enhanced with LLM parsing.
        """
        text = snapshot.get("text", "")
        
        # Basic extraction (can be improved)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        profile = {
            "name": lines[0] if lines else None,
            "headline": lines[1] if len(lines) > 1 else None,
            "raw_text": text,
            "url": snapshot.get("url"),
        }
        
        return profile
    
    def import_cookies(self, cookie_file_path: str, domain: str) -> bool:
        """
        Import cookies from Netscape-format file.
        
        Args:
            cookie_file_path: Path to cookies.txt file
            domain: Domain for cookies (e.g., "linkedin.com")
            
        Returns:
            True if successful
        """
        try:
            with open(cookie_file_path, "r") as f:
                cookie_content = f.read()
            
            result = self._request(
                "POST",
                "/cookies/import",
                json_data={
                    "domain": domain,
                    "cookies": cookie_content,
                }
            )
            
            logger.info(f"Imported cookies for {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import cookies: {e}")
            return False


# Convenience function
def get_camofox_client() -> CamofoxClient:
    """Get configured Camofox client."""
    return CamofoxClient()
