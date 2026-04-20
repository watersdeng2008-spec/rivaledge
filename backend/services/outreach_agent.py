"""
Outreach Agent — sends emails and manages sequences via Instantly.ai API v2

Integrates with Instantly API v2 for:
- Creating campaigns
- Adding leads in bulk
- Activating campaigns
- Tracking opens, clicks, replies via webhooks
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from services.sales_db import (
    get_lead,
    create_email_sequence,
    update_lead,
    get_supabase,
)
from services.ai import generate_sales_copy
from services.instantly_client import InstantlyClient
from services.entity_detector import enrich_lead

logger = logging.getLogger(__name__)


class OutreachAgent:
    """
    Outreach Agent — orchestrates email sending and sequence management via Instantly v2.
    
    Workflow:
    1. Get email account IDs from Instantly
    2. Create campaign with sequence steps
    3. Add leads in bulk to campaign
    4. Activate campaign (starts sending)
    5. Track engagement via webhooks
    """
    
    def __init__(self):
        self.instantly = InstantlyClient()
        self.email_account_ids: List[str] = []
    
    def _get_email_accounts(self) -> List[str]:
        """Get available email account IDs from Instantly."""
        if self.email_account_ids:
            return self.email_account_ids
        
        try:
            accounts = self.instantly.list_email_accounts()
            # Filter for active, warmed-up accounts
            active_accounts = [
                acc["id"] for acc in accounts
                if acc.get("status") == "active" and acc.get("warmup_enabled", False)
            ]
            
            if not active_accounts:
                # Fallback: use any active account
                active_accounts = [
                    acc["id"] for acc in accounts
                    if acc.get("status") == "active"
                ]
            
            self.email_account_ids = active_accounts
            logger.info(f"Found {len(active_accounts)} active email accounts")
            return active_accounts
            
        except Exception as e:
            logger.error(f"Failed to get email accounts: {e}")
            return []
    
    def create_and_launch_campaign(
        self,
        name: str,
        sequence_steps: List[Dict[str, Any]],
        leads: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Create campaign, add leads, and launch.
        
        Args:
            name: Campaign name
            sequence_steps: List of {subject, body, delay_days}
            leads: List of lead dicts with email, first_name, last_name, company
            
        Returns:
            Campaign ID if successful
        """
        # Get email accounts
        email_account_ids = self._get_email_accounts()
        if not email_account_ids:
            logger.error("No active email accounts found in Instantly")
            return None
        
        try:
            # Step 1: Create campaign
            campaign_id = self.instantly.create_campaign(
                name=name,
                email_account_ids=email_account_ids,
                sequence_steps=sequence_steps,
            )
            
            if not campaign_id:
                logger.error("Failed to create campaign")
                return None
            
            # Step 2: Add leads in bulk (up to 1000 at a time)
            batch_size = 1000
            for i in range(0, len(leads), batch_size):
                batch = leads[i:i + batch_size]
                self.instantly.add_leads_to_campaign_bulk(
                    campaign_id=campaign_id,
                    leads=batch,
                )
            
            # Step 3: Activate campaign (starts sending)
            success = self.instantly.activate_campaign(campaign_id)
            if not success:
                logger.error(f"Failed to activate campaign {campaign_id}")
                return None
            
            logger.info(f"Campaign '{name}' launched with {len(leads)} leads")
            return campaign_id
            
        except Exception as e:
            logger.error(f"Failed to create and launch campaign: {e}")
            return None
    
    def process_approved_emails(self, email_ids: List[str]) -> List[str]:
        """
        Send approved emails by creating a campaign.
        
        Args:
            email_ids: List of approved email IDs from personalized_emails table
            
        Returns:
            List of campaign IDs created
        """
        campaign_ids = []
        
        # Group emails by campaign (for now, one campaign per batch)
        emails_to_send = []
        
        for email_id in email_ids:
            try:
                # Fetch email and lead
                email_result = get_supabase().table("personalized_emails")\
                    .select("*, leads(*)")\
                    .eq("id", email_id)\
                    .single()\
                    .execute()
                
                if not email_result.data:
                    logger.warning(f"Email not found: {email_id}")
                    continue
                
                email_data = email_result.data
                lead = email_data.get("leads", {})
                
                emails_to_send.append({
                    "email_id": email_id,
                    "lead": lead,
                    "subject": email_data.get("subject"),
                    "body": email_data.get("body"),
                })
                
            except Exception as e:
                logger.error(f"Failed to fetch email {email_id}: {e}")
        
        if not emails_to_send:
            return campaign_ids
        
        # Create leads list for Instantly (with enrichment)
        leads = []
        for item in emails_to_send:
            lead = item["lead"]
            
            # Enrich lead data with entity detection
            lead = self.enrich_lead_data(lead)
            
            name = lead.get("name", "")
            name_parts = name.split() if name else ["", ""]
            
            leads.append({
                "email": lead.get("email"),
                "first_name": name_parts[0] if name_parts else None,
                "last_name": name_parts[-1] if len(name_parts) > 1 else None,
                "company": lead.get("company"),
            })
        
        # Create sequence (just one email for now)
        sequence_steps = [{
            "subject": emails_to_send[0]["subject"],
            "body": emails_to_send[0]["body"],
            "delay_days": 0,
        }]
        
        # Create and launch campaign
        campaign_name = f"RivalEdge-Outreach-{datetime.utcnow().strftime('%Y%m%d')}"
        campaign_id = self.create_and_launch_campaign(
            name=campaign_name,
            sequence_steps=sequence_steps,
            leads=leads,
        )
        
        if campaign_id:
            campaign_ids.append(campaign_id)
            
            # Update email statuses
            for item in emails_to_send:
                get_supabase().table("personalized_emails")\
                    .update({
                        "status": "sent",
                        "campaign_id": campaign_id,
                        "sent_at": datetime.utcnow().isoformat(),
                    })\
                    .eq("id", item["email_id"])\
                    .execute()
                
                # Update lead status
                update_lead(item["lead"].get("id"), {
                    "status": "contacted",
                    "last_contacted_at": datetime.utcnow().isoformat(),
                })
        
        return campaign_ids
    
    def create_follow_up_sequence(
        self,
        lead_id: str,
        initial_email: Dict[str, Any],
    ) -> Optional[str]:
        """
        Create 3-touch follow-up sequence for a single lead.
        
        Args:
            lead_id: Lead ID
            initial_email: First email data
            
        Returns:
            Campaign ID if created
        """
        lead = get_lead(lead_id)
        if not lead:
            logger.warning(f"Lead not found: {lead_id}")
            return None
        
        # Enrich lead data
        lead = self.enrich_lead_data(lead)
        
        # Generate follow-up emails
        sequence_steps = self._generate_sequence(lead, initial_email)
        
        # Create lead for Instantly
        name = lead.get("name", "")
        name_parts = name.split() if name else ["", ""]
        leads = [{
            "email": lead.get("email"),
            "first_name": name_parts[0] if name_parts else None,
            "last_name": name_parts[-1] if len(name_parts) > 1 else None,
            "company": lead.get("company"),
        }]
        
        # Create and launch campaign
        campaign_name = f"RivalEdge-Sequence-{lead.get('company', 'Lead')}-{lead_id[:8]}"
        campaign_id = self.create_and_launch_campaign(
            name=campaign_name,
            sequence_steps=sequence_steps,
            leads=leads,
        )
        
        if campaign_id:
            # Save to database
            for i, email in enumerate(sequence_steps):
                create_email_sequence({
                    "lead_id": lead_id,
                    "campaign_id": campaign_id,
                    "sequence_name": campaign_name,
                    "email_number": i + 1,
                    "subject": email["subject"],
                    "body": email["body"],
                    "scheduled_at": (datetime.utcnow() + timedelta(days=email["delay_days"])).isoformat(),
                })
        
        return campaign_id
    
    def _generate_sequence(
        self,
        lead: Dict[str, Any],
        initial_email: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate 3-touch email sequence."""
        first_name = lead.get("name", "").split()[0] if lead.get("name") else "there"
        company = lead.get("company", "your company")
        
        # Email 1: Initial
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
        try:
            event_type = webhook_data.get("event")
            campaign_id = webhook_data.get("campaign_id")
            lead_email = webhook_data.get("lead_email")
            
            if not campaign_id or not lead_email:
                return False
            
            # Find lead by email
            lead_result = get_supabase().table("leads")\
                .select("id")\
                .eq("email", lead_email)\
                .single()\
                .execute()
            
            if not lead_result.data:
                logger.warning(f"Lead not found for email: {lead_email}")
                return False
            
            lead_id = lead_result.data["id"]
            
            # Find email sequence by campaign_id
            sequence_result = get_supabase().table("email_sequences")\
                .select("*")\
                .eq("campaign_id", campaign_id)\
                .eq("lead_id", lead_id)\
                .execute()
            
            if not sequence_result.data:
                logger.warning(f"Sequence not found for campaign: {campaign_id}")
                return False
            
            sequence_data = sequence_result.data[0]
            
            # Update based on event
            now = datetime.utcnow().isoformat()
            
            if event_type == "open":
                get_supabase().table("email_sequences")\
                    .update({
                        "opened_at": now,
                        "open_count": sequence_data.get("open_count", 0) + 1,
                    })\
                    .eq("id", sequence_data["id"])\
                    .execute()
                
            elif event_type == "click":
                get_supabase().table("email_sequences")\
                    .update({
                        "clicked_at": now,
                        "click_count": sequence_data.get("click_count", 0) + 1,
                    })\
                    .eq("id", sequence_data["id"])\
                    .execute()
                
            elif event_type == "reply":
                get_supabase().table("email_sequences")\
                    .update({
                        "replied_at": now,
                    })\
                    .eq("id", sequence_data["id"])\
                    .execute()
                
                # Hot lead! Update status
                update_lead(lead_id, {"status": "replied"})
                logger.info(f"🚨 HOT LEAD: {lead_id} replied to email!")
                
                # TODO: Notify Waters via Telegram
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return False
    
    def enrich_lead_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich lead data with entity detection.
        
        Extracts company, role, industry from available lead info.
        """
        try:
            enriched = enrich_lead(lead)
            
            # Merge enriched data with existing lead data
            lead.update({
                k: v for k, v in enriched.items()
                if v is not None and (k not in lead or lead[k] is None)
            })
            
            logger.info(f"Enriched lead: {lead.get('email')} -> {lead.get('company')}")
            return lead
            
        except Exception as e:
            logger.warning(f"Failed to enrich lead {lead.get('email')}: {e}")
            return lead
    
    def test_connection(self) -> bool:
        """Test Instantly API connection."""
        return self.instantly.test_connection()


# Convenience function
def get_outreach_agent() -> OutreachAgent:
    """Get configured Outreach Agent instance."""
    return OutreachAgent()
