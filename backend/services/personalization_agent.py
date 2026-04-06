"""
Personalization Agent — drafts personalized cold emails for sales leads.

Uses Qwen (free) to generate personalized outreach at scale.
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from services.ai import generate_sales_copy
from services.sales_db import create_personalized_email
from services.memory_store import get_memory

logger = logging.getLogger(__name__)


@dataclass
class EmailTemplate:
    """Email template with personalization hooks."""
    id: str
    name: str
    subject: str
    body: str
    best_for: List[str]  # Use cases


# Email Templates (based on Nathan's Buffer patterns)
TEMPLATES = {
    "competitor_monitoring": EmailTemplate(
        id="competitor_monitoring",
        name="Competitor Monitoring Angle",
        subject="{{company}} vs {{competitor_name}} — noticed something",
        body="""Hi {{first_name}},

I was looking at {{company}}'s positioning against {{competitor_name}} and noticed {{personalization_hook}}.

Most {{industry}} teams I talk to are flying blind on competitor moves. They're the last to know about:
• Pricing changes
• Feature launches  
• Messaging pivots

We built RivalEdge to fix this. It monitors your competitors automatically and sends weekly AI briefings.

Worth a 10-minute conversation?

Best,
Ben
""",
        best_for=["vp_product", "ceo", "founder"],
    ),
    
    "pricing_intelligence": EmailTemplate(
        id="pricing_intelligence",
        name="Pricing Intelligence Angle",
        subject="Quick question about {{company}}'s pricing strategy",
        body="""Hi {{first_name}},

{{personalization_hook}}

I help {{industry}} teams track competitor pricing changes in real-time. One of our users just caught a competitor raising prices 40% — they matched it within 24 hours and captured 3 deals from the confusion.

Worth exploring for {{company}}?

Best,
Ben
""",
        best_for=["pricing", "strategy", "revenue"],
    ),
    
    "feature_tracking": EmailTemplate(
        id="feature_tracking",
        name="Feature Launch Tracking",
        subject="{{competitor_name}} just launched something interesting",
        body="""Hi {{first_name}},

Not sure if you saw — {{competitor_name}} launched {{feature_name}} this week.

{{personalization_hook}}

We built RivalEdge specifically to catch these moves early. Weekly AI briefings on what your competitors are building, pricing, and messaging.

Interested in seeing how it works?

Best,
Ben
""",
        best_for=["product", "innovation", "strategy"],
    ),
    
    "market_gap": EmailTemplate(
        id="market_gap",
        name="Market Gap Analysis",
        subject="The competitive intelligence market is broken",
        body="""Hi {{first_name}},

The competitive intelligence market is broken.

Enterprise tools: $20,000+/year, 3-month implementation, 200-page quarterly reports.

DIY approach: 10+ hours/week monitoring competitor websites, scattered notes, no system.

There's a massive gap in the middle.

Small teams need:
• Automated monitoring (not manual checking)
• Weekly briefings (not quarterly decks)
• Actionable insights (not raw data dumps)
• Affordable pricing (not enterprise contracts)

That's why we built RivalEdge.

$49/month. 5-minute setup. Weekly AI briefings.

Because competitive intelligence shouldn't be a luxury reserved for Fortune 500s.

Worth a conversation?

Best,
Ben
""",
        best_for=["smb", "startup", "indie"],
    ),
}


class PersonalizationEngine:
    """
    Generates personalized email content for leads.
    
    Uses AI (Qwen - free) to:
    1. Select best template based on lead profile
    2. Research personalization hooks
    3. Draft customized email
    4. Score quality
    """
    
    def __init__(self):
        self.templates = TEMPLATES
    
    def select_template(self, lead: Dict[str, Any]) -> EmailTemplate:
        """
        Select best email template based on lead profile.
        
        Args:
            lead: Lead data from database
            
        Returns:
            Best matching template
        """
        title = (lead.get("title") or "").lower()
        industry = (lead.get("industry") or "").lower()
        pain_signals = lead.get("pain_signals", [])
        
        # Score each template
        scores = {}
        
        for template_id, template in self.templates.items():
            score = 0
            
            # Title matching
            if any(t in title for t in ["vp", "ceo", "founder", "head"]):
                if template_id == "competitor_monitoring":
                    score += 3
            if any(t in title for t in ["pricing", "revenue", "finance"]):
                if template_id == "pricing_intelligence":
                    score += 3
            if any(t in title for t in ["product", "innovation"]):
                if template_id == "feature_tracking":
                    score += 3
            
            # Industry matching
            if "saas" in industry or "software" in industry:
                score += 1
            
            # Pain signal matching
            if "pricing_pressure" in pain_signals and template_id == "pricing_intelligence":
                score += 2
            if "new_competitor" in pain_signals and template_id == "competitor_monitoring":
                score += 2
            
            # Company size (SMB prefer market_gap)
            company_size = lead.get("company_size", "")
            if company_size in ["1-10", "11-50"] and template_id == "market_gap":
                score += 2
            
            scores[template_id] = score
        
        # Select highest scoring template
        best_template_id = max(scores, key=scores.get)
        return self.templates[best_template_id]
    
    def generate_personalization_hook(self, lead: Dict[str, Any]) -> str:
        """
        Generate personalized hook based on lead research.
        
        Uses AI (Qwen - free) to find specific angle.
        
        Args:
            lead: Lead data
            
        Returns:
            Personalized hook sentence
        """
        try:
            prompt = f"""Generate a personalized opening hook for a cold email to this person:

Name: {lead.get('name')}
Title: {lead.get('title')}
Company: {lead.get('company')}
Industry: {lead.get('industry')}
Pain Signals: {lead.get('pain_signals', [])}

Write ONE sentence that shows I've done research and connects to their potential interest in competitor monitoring.

Examples:
- "I noticed you recently expanded into enterprise pricing tiers..."
- "Saw that {{competitor}} just raised their prices by 30%..."
- "Your team has been hiring aggressively for product roles..."

Be specific, concise, and relevant. One sentence only."""
            
            hook = generate_sales_copy(prompt, max_tokens=150)
            
            # Clean up
            hook = hook.strip().strip('"').strip("'")
            if not hook.endswith(('.', '!', '?')):
                hook += "."
            
            return hook
            
        except Exception as e:
            logger.error(f"Failed to generate hook: {e}")
            # Fallback hooks
            fallbacks = [
                f"I noticed {lead.get('company')} has been growing fast in the {lead.get('industry')} space.",
                f"Saw that you're leading {lead.get('company')}'s strategy in a competitive market.",
                f"Noticed {lead.get('company')} is positioned well in the {lead.get('industry')} landscape.",
            ]
            import random
            return random.choice(fallbacks)
    
    def personalize_email(self, lead: Dict[str, Any], template: EmailTemplate) -> Dict[str, Any]:
        """
        Personalize email template for specific lead.
        
        Args:
            lead: Lead data
            template: Selected template
            
        Returns:
            Personalized email with subject and body
        """
        # Generate personalization hook
        hook = self.generate_personalization_hook(lead)
        
        # Extract first name
        name = lead.get("name", "")
        first_name = name.split()[0] if name else "there"
        
        # Build replacements
        replacements = {
            "{{first_name}}": first_name,
            "{{company}}": lead.get("company", "your company"),
            "{{industry}}": lead.get("industry", "your industry"),
            "{{personalization_hook}}": hook,
            "{{competitor_name}}": "your competitor",  # Could be enriched
            "{{feature_name}}": "new features",  # Could be enriched
        }
        
        # Apply replacements
        subject = template.subject
        body = template.body
        
        for key, value in replacements.items():
            subject = subject.replace(key, value)
            body = body.replace(key, value)
        
        return {
            "subject": subject,
            "body": body,
            "template_used": template.id,
            "personalization_score": self._score_personalization(subject, body, hook),
            "personalization_notes": {
                "hook": hook,
                "template": template.name,
                "lead_title": lead.get("title"),
            },
        }
    
    def _score_personalization(self, subject: str, body: str, hook: str) -> int:
        """
        Score personalization quality (1-10).
        
        Higher score = more specific, less generic.
        """
        score = 5  # Base score
        
        # Check for generic phrases (deduct)
        generic_phrases = ["your company", "your industry", "there"]
        for phrase in generic_phrases:
            if phrase in body.lower():
                score -= 1
        
        # Check for specific details (add)
        if len(hook) > 50:  # Detailed hook
            score += 2
        if "I noticed" in hook or "Saw that" in hook:  # Shows research
            score += 1
        if any(char.isdigit() for char in hook):  # Contains numbers (specific)
            score += 1
        
        # Length check
        if len(body) < 1000:  # Concise
            score += 1
        
        return max(1, min(10, score))


class PersonalizationAgent:
    """
    Personalization Agent — orchestrates email drafting workflow.
    
    Workflow:
    1. Fetch unprocessed leads from database
    2. Select best template for each lead
    3. Generate personalized content
    4. Score quality
    5. Save to database for approval
    6. Store template performance in AgentMemory
    """
    
    def __init__(self):
        self.engine = PersonalizationEngine()
        self.memory = get_memory()
    
    def process_leads(self, lead_ids: List[str]) -> List[str]:
        """
        Process leads and create personalized emails.
        
        Args:
            lead_ids: List of lead IDs to process
            
        Returns:
            List of created email IDs
        """
        from services.sales_db import get_lead
        
        created_emails = []
        
        for lead_id in lead_ids:
            try:
                # Fetch lead
                lead = get_lead(lead_id)
                if not lead:
                    logger.warning(f"Lead not found: {lead_id}")
                    continue
                
                # Skip if already has personalized email
                # (Would check database in production)
                
                # Generate personalized email
                email_data = self.draft_email(lead)
                if email_data:
                    # Save to database
                    email_id = create_personalized_email({
                        "lead_id": lead_id,
                        **email_data,
                        "status": "draft",
                    })
                    created_emails.append(email_id)
                    logger.info(f"Created personalized email for {lead.get('email')}")
                    
                    # Store in AgentMemory for learning
                    self.memory.remember(
                        content=f"Email drafted for {lead.get('title')} at {lead.get('company')}: {email_data['template_used']} (score: {email_data['personalization_score']})",
                        importance=5,
                        category="email_personalization",
                        template=email_data['template_used'],
                        score=email_data['personalization_score'],
                        lead_title=lead.get('title'),
                        industry=lead.get('industry')
                    )
                
            except Exception as e:
                logger.error(f"Failed to process lead {lead_id}: {e}")
        
        # Store batch summary
        if created_emails:
            self.memory.remember(
                content=f"Personalization batch: Created {len(created_emails)} emails for {len(lead_ids)} leads",
                importance=6,
                category="personalization_summary",
                batch_size=len(lead_ids),
                success_rate=len(created_emails)/len(lead_ids) if lead_ids else 0
            )
        
        return created_emails
    
    def draft_email(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Draft personalized email for single lead.
        
        Args:
            lead: Lead data
            
        Returns:
            Email data or None if failed
        """
        try:
            # Select template
            template = self.engine.select_template(lead)
            
            # Personalize
            email = self.engine.personalize_email(lead, template)
            
            # Only return if quality score >= 6
            if email["personalization_score"] >= 6:
                return email
            else:
                logger.warning(f"Low quality email for {lead.get('email')}, skipping")
                return None
                
        except Exception as e:
            logger.error(f"Failed to draft email: {e}")
            return None
    
    def get_pending_emails(self, min_score: int = 6) -> List[Dict[str, Any]]:
        """
        Get personalized emails awaiting approval.
        
        Args:
            min_score: Minimum personalization score
            
        Returns:
            List of pending emails
        """
        # Would query database in production
        # For now, return placeholder
        return []


# Convenience function
def get_personalization_agent() -> PersonalizationAgent:
    """Get configured Personalization Agent instance."""
    return PersonalizationAgent()
