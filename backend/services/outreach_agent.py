"""
Outreach Agent — sends emails and manages sequences via Instantly.ai

Integrates with Instantly API for:
- Sending personalized emails
- Managing follow-up sequences
- Tracking opens, clicks, replies
- Scheduling campaigns
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx

from services.sales_db import (
    get_lead,
    create_email_sequence,
    update_lead,
)
from services.ai import generate_sales_copy

logger = logging.getLogger(__name__)

# Instantly API configuration
INSTANTLY_API_KEY = os.environ.get("INSTANTLY_API_KEY", "")
INSTANTLY_BASE_URL = "https://api.instantly.ai/api/v1"


@dataclass
class EmailSequence:
    """Email sequence configuration."""
    lead_id: str
    email_address: str
    sequence_name: str
    emails: List[Dict[str, Any]]  # List of {subject, body, delay_days}


class InstantlyClient:
    """Client for Instantly.ai API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or INSTANTLY_API_KEY
        self.base_url = INSTANTLY_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        track_opens: bool = True,
        track_clicks: bool = True,
    ) -> Dict[str, Any]:
        """
        Send single email via Instantly.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (HTML or text)
            from_email: Sender email (optional, uses default)
            track_opens: Track email opens
            track_clicks: Track link clicks
            
        Returns:
            API response with message_id
        """
        if not self.api_key:
            logger.warning("Instantly API key not set")
            return {"error": "API key not configured"}
        
        url = f"{self.base_url}/send"
        
        payload = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "track_opens": track_opens,
            "track_clicks": track_clicks,
        }
        
        if from_email:
            payload["from"] = from_email
        
        try:
            response = httpx.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Email sent to {to_email}, message_id: {data.get('message_id')}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to send email via Instantly: {e}")
            raise
    
    def create_sequence(
        self,
        name: str,
        emails: List[Dict[str, Any]],
    ) -> str:
        """
        Create email sequence (campaign) in Instantly.
        
        Args:
            name: Sequence name
            emails: List of {subject, body, delay_days}
            
        Returns:
            Sequence ID
        """
        if not self.api_key:
            logger.warning("Instantly API key not set")
            return ""
        
        url = f"{self.base_url}/campaigns"
        
        payload = {
            "name": name,
            "steps": [
                {
                    "subject": email["subject"],
                    "body": email["body"],
                    "delay": email.get("delay_days", 0) * 24 * 60,  # Convert to minutes
                }
                for email in emails
            ],
        }
        
        try:
            response = httpx.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            sequence_id = data.get("id")
            logger.info(f"Created sequence: {sequence_id}")
            return sequence_id
            
        except Exception as e:
            logger.error(f"Failed to create sequence: {e}")
            raise
    
    def add_lead_to_sequence(
        self,
        sequence_id: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        custom_fields: Optional[Dict] = None,
    ) -> bool:
        """
        Add lead to email sequence.
        
        Args:
            sequence_id: Sequence/campaign ID
            email: Lead email
            first_name: Lead first name
            last_name: Lead last name
            company: Lead company
            custom_fields: Additional custom fields
            
        Returns:
            True if successful
        """
        if not self.api_key:
            logger.warning("Instantly API key not set")
            return False
        
        url = f"{self.base_url}/campaigns/{sequence_id}/leads"
        
        payload = {
            "email": email,
        }
        
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if company:
            payload["company"] = company
        if custom_fields:
            payload["custom_fields"] = custom_fields
        
        try:
            response = httpx.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            
            logger.info(f"Added {email} to sequence {sequence_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add lead to sequence: {e}")
            return False
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign statistics.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Stats dict with sent, opened, clicked, replied counts
        """
        if not self.api_key:
            logger.warning("Instantly API key not set")
            return {}
        
        url = f"{self.base_url}/campaigns/{campaign_id}/stats"
        
        try:
            response = httpx.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get campaign stats: {e}")
            return {}


class OutreachAgent:
    """
    Outreach Agent — orchestrates email sending and sequence management.
    
    Workflow:
    1. Fetch approved emails from database
    2. Create sequence in Instantly (if multi-touch)
    3. Send emails or add to sequence
    4. Track engagement via webhooks
    5. Update lead status
    """
    
    def __init__(self):
        self.instantly = InstantlyClient()
    
    def process_approved_emails(self, email_ids: List[str]) -> List[str]:
        """
        Send approved emails.
        
        Args:
            email_ids: List of approved email IDs
            
        Returns:
            List of sent message IDs
        """
        from services.sales_db import supabase
        
        sent_messages = []
        
        for email_id in email_ids:
            try:
                # Fetch email and lead
                email_result = supabase.table("personalized_emails")\
                    .select("*, leads(*)")\
                    .eq("id", email_id)\
                    .single()\
                    .execute()
                
                if not email_result.data:
                    logger.warning(f"Email not found: {email_id}")
                    continue
                
                email_data = email_result.data
                lead = email_data.get("leads", {})
                
                # Send via Instantly
                result = self.instantly.send_email(
                    to_email=lead.get("email"),
                    subject=email_data.get("subject"),
                    body=email_data.get("body"),
                )
                
                if result.get("message_id"):
                    # Update email status
                    supabase.table("personalized_emails")\
                        .update({
                            "status": "sent",
                            "external_message_id": result["message_id"],
                        })\
                        .eq("id", email_id)\
                        .execute()
                    
                    # Update lead
                    update_lead(lead.get("id"), {
                        "status": "contacted",
                        "last_contacted_at": datetime.utcnow().isoformat(),
                    })
                    
                    sent_messages.append(result["message_id"])
                    logger.info(f"Sent email to {lead.get('email')}")
                
            except Exception as e:
                logger.error(f"Failed to send email {email_id}: {e}")
        
        return sent_messages
    
    def create_follow_up_sequence(
        self,
        lead_id: str,
        initial_email: Dict[str, Any],
    ) -> Optional[str]:
        """
        Create 3-touch follow-up sequence for lead.
        
        Args:
            lead_id: Lead ID
            initial_email: First email data
            
        Returns:
            Sequence ID if created
        """
        lead = get_lead(lead_id)
        if not lead:
            logger.warning(f"Lead not found: {lead_id}")
            return None
        
        # Generate follow-up emails
        sequence_emails = self._generate_sequence(lead, initial_email)
        
        # Create in Instantly
        sequence_name = f"RivalEdge-{lead.get('company', 'Lead')}-{lead_id[:8]}"
        sequence_id = self.instantly.create_sequence(
            name=sequence_name,
            emails=sequence_emails,
        )
        
        if sequence_id:
            # Add lead to sequence
            self.instantly.add_lead_to_sequence(
                sequence_id=sequence_id,
                email=lead.get("email"),
                first_name=lead.get("name", "").split()[0] if lead.get("name") else None,
                last_name=lead.get("name", "").split()[-1] if lead.get("name") and len(lead.get("name", "").split()) > 1 else None,
                company=lead.get("company"),
            )
            
            # Save to database
            for i, email in enumerate(sequence_emails):
                create_email_sequence({
                    "lead_id": lead_id,
                    "sequence_name": sequence_name,
                    "email_number": i + 1,
                    "subject": email["subject"],
                    "body": email["body"],
                    "scheduled_at": (datetime.utcnow() + timedelta(days=email["delay_days"])).isoformat(),
                })
        
        return sequence_id
    
    def _generate_sequence(
        self,
        lead: Dict[str, Any],
        initial_email: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate 3-touch email sequence.
        
        Returns list of {subject, body, delay_days}
        """
        first_name = lead.get("name", "").split()[0] if lead.get("name") else "there"
        company = lead.get("company", "your company")
        
        # Email 1: Initial (already have this)
        emails = [{
            "subject": initial_email.get("subject"),
            "body": initial_email.get("body"),
            "delay_days": 0,
        }]
        
        # Email 2: Follow-up (Day 3)
        prompt = f"""Write a brief, polite follow-up email to {first_name} at {company}.

Context: I sent an email 3 days ago about RivalEdge (competitor monitoring tool) but haven't heard back.

Requirements:
- Keep it under 100 words
- Don't be pushy
- Add value (share a relevant insight)
- Include clear call to action

Subject line should reference the previous email."""
        
        try:
            followup_body = generate_sales_copy(prompt, max_tokens=300)
            followup_subject = f"Re: {initial_email.get('subject')}"
            
            emails.append({
                "subject": followup_subject,
                "body": followup_body,
                "delay_days": 3,
            })
        except Exception as e:
            logger.error(f"Failed to generate follow-up: {e}")
            # Use template fallback
            emails.append({
                "subject": f"Re: {initial_email.get('subject')}",
                "body": f"Hi {first_name},\n\nJust following up on my previous email about RivalEdge.\n\nWorth a quick conversation?\n\nBest,\nBen",
                "delay_days": 3,
            })
        
        # Email 3: Break-up (Day 7)
        emails.append({
            "subject": f"Re: {initial_email.get('subject')}",
            "body": f"Hi {first_name},\n\nI don't want to be a bother. If now isn't the right time, I understand.\n\nIf competitor monitoring becomes a priority for {company}, feel free to reach out.\n\nBest,\nBen",
            "delay_days": 7,
        })
        
        return emails
    
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Handle Instantly webhook for email events.
        
        Args:
            webhook_data: Webhook payload from Instantly
            
        Returns:
            True if processed successfully
        """
        from services.sales_db import supabase
        
        try:
            event_type = webhook_data.get("event")
            message_id = webhook_data.get("message_id")
            
            if not message_id:
                return False
            
            # Find email by message_id
            email_result = supabase.table("email_sequences")\
                .select("*, leads(id)")\
                .eq("external_message_id", message_id)\
                .execute()
            
            if not email_result.data:
                logger.warning(f"Email not found for message_id: {message_id}")
                return False
            
            email_data = email_result.data[0]
            lead_id = email_data.get("leads", {}).get("id")
            
            # Update based on event
            if event_type == "open":
                supabase.table("email_sequences")\
                    .update({
                        "opened_at": datetime.utcnow().isoformat(),
                        "open_count": email_data.get("open_count", 0) + 1,
                    })\
                    .eq("id", email_data.get("id"))\
                    .execute()
                
                # Update lead
                update_lead(lead_id, {
                    "emails_opened": supabase.table("leads").select("emails_opened").eq("id", lead_id).execute().data[0]["emails_opened"] + 1,
                })
                
            elif event_type == "click":
                supabase.table("email_sequences")\
                    .update({
                        "clicked_at": datetime.utcnow().isoformat(),
                        "click_count": email_data.get("click_count", 0) + 1,
                    })\
                    .eq("id", email_data.get("id"))\
                    .execute()
                
                update_lead(lead_id, {
                    "emails_clicked": supabase.table("leads").select("emails_clicked").eq("id", lead_id).execute().data[0]["emails_clicked"] + 1,
                })
                
            elif event_type == "reply":
                supabase.table("email_sequences")\
                    .update({
                        "replied_at": datetime.utcnow().isoformat(),
                    })\
                    .eq("id", email_data.get("id"))\
                    .execute()
                
                # Hot lead! Update status
                update_lead(lead_id, {
                    "status": "replied",
                })
                
                # TODO: Notify Waters via Telegram
                logger.info(f"🚨 HOT LEAD: {lead_id} replied to email!")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return False


# Convenience function
def get_outreach_agent() -> OutreachAgent:
    """Get configured Outreach Agent instance."""
    return OutreachAgent()
