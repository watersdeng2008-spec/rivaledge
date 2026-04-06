"""
Sales Agent Dashboard Service

Provides analytics, optimization, and management functions for the sales agent.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from services.sales_db import supabase
from services.memory_store import get_memory

logger = logging.getLogger(__name__)


class SalesDashboard:
    """
    Sales Agent Dashboard — analytics and management.
    
    Features:
    - Pipeline overview (leads by stage)
    - Campaign performance metrics
    - Template effectiveness analysis
    - Cost tracking
    - Optimization recommendations
    """
    
    def __init__(self):
        self.memory = get_memory()
    
    def get_pipeline_overview(self) -> Dict[str, Any]:
        """
        Get sales pipeline overview.
        
        Returns:
            Dict with lead counts by stage
        """
        try:
            # Get counts by status
            statuses = ["new", "enriched", "personalized", "contacted", "replied", "qualified", "converted"]
            pipeline = {}
            
            for status in statuses:
                result = supabase.table("leads")\
                    .select("count", count="exact")\
                    .eq("status", status)\
                    .execute()
                count = result.count if hasattr(result, 'count') else 0
                pipeline[status] = count
            
            # Calculate conversion rates
            total = sum(pipeline.values())
            contacted = pipeline.get("contacted", 0) + pipeline.get("replied", 0) + pipeline.get("qualified", 0) + pipeline.get("converted", 0)
            replied = pipeline.get("replied", 0) + pipeline.get("qualified", 0) + pipeline.get("converted", 0)
            converted = pipeline.get("converted", 0)
            
            return {
                "pipeline": pipeline,
                "total_leads": total,
                "conversion_rates": {
                    "lead_to_contact": round(contacted / total * 100, 2) if total > 0 else 0,
                    "contact_to_reply": round(replied / contacted * 100, 2) if contacted > 0 else 0,
                    "reply_to_conversion": round(converted / replied * 100, 2) if replied > 0 else 0,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline overview: {e}")
            return {"error": str(e)}
    
    def get_campaign_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        Get email campaign performance metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Performance metrics
        """
        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Get email sequences in period
            result = supabase.table("email_sequences")\
                .select("*")\
                .gte("created_at", cutoff)\
                .execute()
            
            emails = result.data or []
            
            if not emails:
                return {
                    "period_days": days,
                    "message": "No emails sent in this period"
                }
            
            # Calculate metrics
            total_sent = len([e for e in emails if e.get("status") == "sent"])
            total_opened = len([e for e in emails if e.get("opened_at")])
            total_clicked = len([e for e in emails if e.get("clicked_at")])
            total_replied = len([e for e in emails if e.get("replied_at")])
            
            return {
                "period_days": days,
                "emails_sent": total_sent,
                "emails_opened": total_opened,
                "emails_clicked": total_clicked,
                "emails_replied": total_replied,
                "rates": {
                    "open_rate": round(total_opened / total_sent * 100, 2) if total_sent > 0 else 0,
                    "click_rate": round(total_clicked / total_sent * 100, 2) if total_sent > 0 else 0,
                    "reply_rate": round(total_replied / total_sent * 100, 2) if total_sent > 0 else 0,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign performance: {e}")
            return {"error": str(e)}
    
    def get_template_effectiveness(self) -> List[Dict[str, Any]]:
        """
        Analyze which email templates perform best.
        
        Returns:
            List of templates with performance metrics
        """
        try:
            # Get all sent emails with template info
            result = supabase.table("personalized_emails")\
                .select("template_used, status, leads!inner(emails_opened, emails_replied)")\
                .eq("status", "sent")\
                .execute()
            
            emails = result.data or []
            
            # Group by template
            template_stats = {}
            for email in emails:
                template = email.get("template_used", "unknown")
                if template not in template_stats:
                    template_stats[template] = {
                        "sent": 0,
                        "opened": 0,
                        "replied": 0,
                    }
                
                template_stats[template]["sent"] += 1
                lead = email.get("leads", {})
                if lead.get("emails_opened", 0) > 0:
                    template_stats[template]["opened"] += 1
                if lead.get("emails_replied", 0) > 0:
                    template_stats[template]["replied"] += 1
            
            # Calculate effectiveness scores
            effectiveness = []
            for template, stats in template_stats.items():
                sent = stats["sent"]
                if sent > 0:
                    effectiveness.append({
                        "template": template,
                        "emails_sent": sent,
                        "open_rate": round(stats["opened"] / sent * 100, 2),
                        "reply_rate": round(stats["replied"] / sent * 100, 2),
                        "effectiveness_score": round(
                            (stats["opened"] * 1 + stats["replied"] * 3) / sent * 100, 2
                        ),  # Weighted: replies worth 3x opens
                    })
            
            # Sort by effectiveness
            effectiveness.sort(key=lambda x: x["effectiveness_score"], reverse=True)
            return effectiveness
            
        except Exception as e:
            logger.error(f"Failed to get template effectiveness: {e}")
            return []
    
    def get_cost_tracking(self, days: int = 30) -> Dict[str, Any]:
        """
        Track AI and infrastructure costs.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Cost breakdown
        """
        try:
            # This would integrate with token usage logs
            # For now, return placeholder structure
            
            return {
                "period_days": days,
                "ai_costs": {
                    "qwen_free": 0.0,  # Free tier
                    "kimi_k2_5": 0.0,  # Would calculate from logs
                    "total": 0.0,
                },
                "infrastructure": {
                    "railway": 7.0,  # Estimated
                    "supabase": 0.0,  # Free tier
                    "total": 7.0,
                },
                "total_cost": 7.0,
                "cost_per_lead": 0.0,  # Would calculate
                "cost_per_demo": 0.0,  # Would calculate
            }
            
        except Exception as e:
            logger.error(f"Failed to get cost tracking: {e}")
            return {"error": str(e)}
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations based on data.
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        try:
            # 1. Template optimization
            templates = self.get_template_effectiveness()
            if templates:
                best = templates[0]
                worst = templates[-1]
                
                if best["reply_rate"] > worst["reply_rate"] * 2:
                    recommendations.append({
                        "priority": "high",
                        "category": "templates",
                        "recommendation": f"Use '{best['template']}' more — it gets {best['reply_rate']}% replies vs {worst['reply_rate']}% for '{worst['template']}'",
                        "action": "Shift 50% of volume to best-performing template",
                    })
            
            # 2. Lead quality optimization
            pipeline = self.get_pipeline_overview()
            if pipeline.get("conversion_rates", {}).get("lead_to_contact", 0) < 50:
                recommendations.append({
                    "priority": "medium",
                    "category": "lead_quality",
                    "recommendation": "Lead-to-contact rate below 50% — tighten ICP criteria",
                    "action": "Focus on VP/CEO titles, 11-200 employee companies",
                })
            
            # 3. Follow-up optimization
            campaign = self.get_campaign_performance(days=14)
            if campaign.get("rates", {}).get("reply_rate", 0) < 5:
                recommendations.append({
                    "priority": "high",
                    "category": "messaging",
                    "recommendation": "Reply rate below 5% — emails need stronger hooks",
                    "action": "A/B test subject lines and opening sentences",
                })
            
            # 4. Cost optimization
            costs = self.get_cost_tracking()
            if costs.get("cost_per_lead", 0) > 10:
                recommendations.append({
                    "priority": "medium",
                    "category": "cost",
                    "recommendation": f"Cost per lead (${costs['cost_per_lead']}) above target ($5)",
                    "action": "Use more Qwen free tier, optimize context windows",
                })
            
            # 5. Memory-based recommendation
            recent_learnings = self.memory.recall(
                "What has been working well in sales outreach?",
                n_results=3
            )
            if recent_learnings:
                recommendations.append({
                    "priority": "low",
                    "category": "learning",
                    "recommendation": "Review recent learnings in AgentMemory",
                    "action": "Query memory for patterns: memory.recall('effective templates')",
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def get_hot_leads(self, min_score: int = 70) -> List[Dict[str, Any]]:
        """
        Get hot leads (high priority + recent engagement).
        
        Args:
            min_score: Minimum priority score
            
        Returns:
            List of hot leads
        """
        try:
            result = supabase.table("leads")\
                .select("*, personalized_emails(*), email_sequences(*)")\
                .gte("priority_score", min_score)\
                .in_("status", ["replied", "qualified"])\
                .order("priority_score", desc=True)\
                .limit(20)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to get hot leads: {e}")
            return []
    
    def get_daily_summary(self) -> str:
        """
        Generate daily summary for Waters.
        
        Returns:
            Formatted summary string
        """
        try:
            pipeline = self.get_pipeline_overview()
            campaign = self.get_campaign_performance(days=1)
            hot_leads = self.get_hot_leads(min_score=80)
            
            lines = [
                "📊 RivalEdge Sales Agent — Daily Summary",
                f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                "",
                "📈 Pipeline:",
                f"  Total leads: {pipeline.get('total_leads', 0)}",
            ]
            
            for status, count in pipeline.get('pipeline', {}).items():
                if count > 0:
                    lines.append(f"  • {status}: {count}")
            
            lines.extend([
                "",
                "📧 Today's Activity:",
                f"  Emails sent: {campaign.get('emails_sent', 0)}",
                f"  Opens: {campaign.get('emails_opened', 0)} ({campaign.get('rates', {}).get('open_rate', 0)}%)",
                f"  Replies: {campaign.get('emails_replied', 0)} ({campaign.get('rates', {}).get('reply_rate', 0)}%)",
                "",
                f"🔥 Hot Leads ({len(hot_leads)}):",
            ])
            
            for lead in hot_leads[:5]:
                lines.append(f"  • {lead.get('name')} ({lead.get('title')}) at {lead.get('company')} — Score: {lead.get('priority_score')}")
            
            # Add recommendations
            recommendations = self.get_optimization_recommendations()
            if recommendations:
                lines.extend([
                    "",
                    "💡 Recommendations:",
                ])
                for rec in recommendations[:3]:
                    lines.append(f"  [{rec['priority'].upper()}] {rec['recommendation']}")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            return f"Error generating summary: {e}"


# Convenience function
def get_dashboard() -> SalesDashboard:
    """Get configured SalesDashboard instance."""
    return SalesDashboard()
