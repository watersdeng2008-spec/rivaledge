"""
GEO Monitor — Monthly monitoring and reporting for GEO clients.

Tracks changes in GEO posture over time, identifies new issues,
and generates monthly health reports.

Usage:
    from agents.geo_monitor import run_monthly_monitor
    
    report = await run_monthly_monitor(
        client_id="client_123",
        url="https://example.com",
        company_name="Example Inc"
    )
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import httpx

from agents.geo_audit_generator import (
    generate_geo_audit,
    GEOAuditReport,
    extract_domain,
)

logger = logging.getLogger(__name__)


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class GEOChange:
    """A single change detected between audits."""
    category: str  # technical, ai_citation, competitor
    change_type: str  # improved, declined, new_issue, resolved
    description: str
    impact: str  # high, medium, low
    recommendation: str


@dataclass
class MonthlyReport:
    """Monthly GEO health report."""
    client_id: str
    company_name: str
    url: str
    report_date: str
    period_start: str
    period_end: str
    current_score: int
    previous_score: int
    score_change: int
    grade: str
    changes: List[GEOChange]
    recommendations: List[Dict[str, Any]]
    competitor_updates: List[Dict[str, Any]]


# ── Change Detection ─────────────────────────────────────────────────────────

def detect_technical_changes(current: Dict, previous: Dict) -> List[GEOChange]:
    """Detect changes in technical GEO assets."""
    changes = []
    
    # Check llms.txt
    current_llms = current.get("llms_txt", {})
    previous_llms = previous.get("llms_txt", {})
    
    if current_llms.get("present") and not previous_llms.get("present"):
        changes.append(GEOChange(
            category="Technical",
            change_type="improved",
            description="llms.txt was added",
            impact="high",
            recommendation="Great! Ensure it's kept updated."
        ))
    elif not current_llms.get("present") and previous_llms.get("present"):
        changes.append(GEOChange(
            category="Technical",
            change_type="declined",
            description="llms.txt was removed",
            impact="high",
            recommendation="Critical: Re-deploy llms.txt immediately."
        ))
    
    # Check robots.txt
    current_robots = current.get("robots_txt", {})
    previous_robots = previous.get("robots_txt", {})
    
    current_rules = current_robots.get("crawler_rules", {})
    previous_rules = previous_robots.get("crawler_rules", {})
    
    for crawler, status in current_rules.items():
        prev_status = previous_rules.get(crawler)
        if prev_status and status != prev_status:
            if status == "disallowed" and prev_status != "disallowed":
                changes.append(GEOChange(
                    category="Technical",
                    change_type="declined",
                    description=f"{crawler} was blocked in robots.txt",
                    impact="high",
                    recommendation=f"Unblock {crawler} to restore AI visibility."
                ))
            elif status == "allowed" and prev_status == "disallowed":
                changes.append(GEOChange(
                    category="Technical",
                    change_type="improved",
                    description=f"{crawler} was unblocked in robots.txt",
                    impact="medium",
                    recommendation="Good! Monitor for increased crawler activity."
                ))
    
    # Check schema
    current_schema = current.get("schema", {})
    previous_schema = previous.get("schema", {})
    
    current_types = set(current_schema.get("types_found", []))
    previous_types = set(previous_schema.get("types_found", []))
    
    new_types = current_types - previous_types
    removed_types = previous_types - current_types
    
    if new_types:
        changes.append(GEOChange(
            category="Technical",
            change_type="improved",
            description=f"New schema types added: {', '.join(new_types)}",
            impact="medium",
            recommendation="Continue adding structured data for better AI understanding."
        ))
    
    if removed_types:
        changes.append(GEOChange(
            category="Technical",
            change_type="declined",
            description=f"Schema types removed: {', '.join(removed_types)}",
            impact="medium",
            recommendation="Re-add removed schema types."
        ))
    
    return changes


def detect_ai_citation_changes(current: Dict, previous: Dict) -> List[GEOChange]:
    """Detect changes in AI citation patterns."""
    changes = []
    
    current_ars = current.get("ars_result")
    previous_ars = previous.get("ars_result")
    
    if not current_ars or not previous_ars:
        return changes
    
    # Score change
    current_score = current_ars.get("ars_score", 0)
    previous_score = previous_ars.get("ars_score", 0)
    
    if current_score > previous_score + 5:
        changes.append(GEOChange(
            category="AI Visibility",
            change_type="improved",
            description=f"AI recommendation score increased from {previous_score:.0f}% to {current_score:.0f}%",
            impact="high",
            recommendation="Continue current strategy. Consider expanding to new query types."
        ))
    elif current_score < previous_score - 5:
        changes.append(GEOChange(
            category="AI Visibility",
            change_type="declined",
            description=f"AI recommendation score decreased from {previous_score:.0f}% to {current_score:.0f}%",
            impact="high",
            recommendation="Investigate competitor activity. Refresh content and llms.txt."
        ))
    
    # Competitor changes
    current_competitors = current_ars.get("competitor_scores", {})
    previous_competitors = previous_ars.get("competitor_scores", {})
    
    for comp, score in current_competitors.items():
        prev_score = previous_competitors.get(comp, 0)
        if score > prev_score + 10:
            changes.append(GEOChange(
                category="AI Visibility",
                change_type="declined",
                description=f"{comp}'s AI visibility increased significantly",
                impact="high",
                recommendation=f"Analyze {comp}'s recent GEO changes. Counter with targeted content."
            ))
    
    return changes


def detect_competitor_changes(current: List[Dict], previous: List[Dict]) -> List[GEOChange]:
    """Detect changes in competitor GEO posture."""
    changes = []
    
    # Create lookup by domain
    current_by_domain = {c.get("domain", ""): c for c in current}
    previous_by_domain = {c.get("domain", ""): c for c in previous}
    
    for domain, current_comp in current_by_domain.items():
        previous_comp = previous_by_domain.get(domain)
        if not previous_comp:
            continue
        
        # Check if competitor added llms.txt
        current_llms = current_comp.get("llms_txt", {}).get("present", False)
        previous_llms = previous_comp.get("llms_txt", {}).get("present", False)
        
        if current_llms and not previous_llms:
            changes.append(GEOChange(
                category="Competitive",
                change_type="declined",
                description=f"{domain} deployed llms.txt",
                impact="high",
                recommendation="Ensure your llms.txt is superior. Add missing sections."
            ))
        
        # Check if competitor improved schema
        current_schema = len(current_comp.get("schema", {}).get("types_found", []))
        previous_schema = len(previous_comp.get("schema", {}).get("types_found", []))
        
        if current_schema > previous_schema + 2:
            changes.append(GEOChange(
                category="Competitive",
                change_type="declined",
                description=f"{domain} added {current_schema - previous_schema} new schema types",
                impact="medium",
                recommendation="Match their schema coverage. Consider adding FAQ and HowTo schemas."
            ))
    
    return changes


# ── Report Generation ────────────────────────────────────────────────────────

def generate_monthly_report(
    client_id: str,
    company_name: str,
    url: str,
    current_audit: GEOAuditReport,
    previous_audit: Optional[GEOAuditReport],
) -> MonthlyReport:
    """Generate monthly GEO health report comparing current vs previous audit."""
    
    changes = []
    
    if previous_audit:
        # Detect all changes
        changes.extend(detect_technical_changes(
            {
                "robots_txt": current_audit.technical.robots_txt,
                "llms_txt": current_audit.technical.llms_txt,
                "sitemap": current_audit.technical.sitemap,
                "schema": current_audit.technical.schema,
            },
            {
                "robots_txt": previous_audit.technical.robots_txt,
                "llms_txt": previous_audit.technical.llms_txt,
                "sitemap": previous_audit.technical.sitemap,
                "schema": previous_audit.technical.schema,
            },
        ))
        
        changes.extend(detect_ai_citation_changes(
            {"ars_result": current_audit.ai_citations.ars_result},
            {"ars_result": previous_audit.ai_citations.ars_result},
        ))
        
        changes.extend(detect_competitor_changes(
            current_audit.competitors.competitors,
            previous_audit.competitors.competitors,
        ))
        
        previous_score = previous_audit.overall_score
    else:
        previous_score = 0
        changes.append(GEOChange(
            category="Setup",
            change_type="new_issue",
            description="First monthly audit — establishing baseline",
            impact="low",
            recommendation="Next month's report will show trends."
        ))
    
    score_change = current_audit.overall_score - previous_score
    
    # Generate recommendations based on current state
    recommendations = current_audit.recommendations[:5]  # Top 5
    
    # Competitor updates
    competitor_updates = []
    for comp in current_audit.competitors.competitors:
        competitor_updates.append({
            "domain": comp.get("domain", ""),
            "llms_txt": "✅" if comp.get("llms_txt", {}).get("present") else "❌",
            "schema_types": len(comp.get("schema", {}).get("types_found", [])),
        })
    
    return MonthlyReport(
        client_id=client_id,
        company_name=company_name,
        url=url,
        report_date=datetime.now().isoformat(),
        period_start=(datetime.now() - timedelta(days=30)).isoformat(),
        period_end=datetime.now().isoformat(),
        current_score=current_audit.overall_score,
        previous_score=previous_score,
        score_change=score_change,
        grade=current_audit.grade,
        changes=changes,
        recommendations=recommendations,
        competitor_updates=competitor_updates,
    )


# ── Main Function ────────────────────────────────────────────────────────────

async def run_monthly_monitor(
    client_id: str,
    url: str,
    company_name: str,
    industry: str,
    competitors: Optional[List[str]] = None,
    previous_audit: Optional[GEOAuditReport] = None,
    tier: str = "pro",
) -> MonthlyReport:
    """
    Run monthly GEO monitoring for a client.
    
    Args:
        client_id: Unique client identifier
        url: Client website URL
        company_name: Company name
        industry: Industry/category
        competitors: List of competitor URLs
        previous_audit: Previous month's audit (for comparison)
        tier: Subscription tier
    
    Returns:
        MonthlyReport with changes and recommendations
    """
    logger.info(f"Running monthly monitor for {company_name} ({client_id})")
    
    # Run new audit
    current_audit = await generate_geo_audit(
        url=url,
        company_name=company_name,
        industry=industry,
        competitors=competitors,
        tier=tier,
    )
    
    # Generate comparison report
    report = generate_monthly_report(
        client_id=client_id,
        company_name=company_name,
        url=url,
        current_audit=current_audit,
        previous_audit=previous_audit,
    )
    
    logger.info(f"Monthly report generated for {company_name}: {report.current_score}/100 (change: {report.score_change:+.0f})")
    
    return report


# ── Email Template ───────────────────────────────────────────────────────────

def generate_monthly_email(report: MonthlyReport) -> str:
    """Generate HTML email for monthly report."""
    
    score_color = "#22c55e" if report.score_change >= 0 else "#ef4444"
    score_sign = "+" if report.score_change >= 0 else ""
    
    changes_html = ""
    for change in report.changes:
        icon = "🟢" if change.change_type == "improved" else "🔴" if change.change_type == "declined" else "🟡"
        changes_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{icon} {change.category}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{change.description}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{change.impact}</td>
        </tr>
        """
    
    recommendations_html = ""
    for i, rec in enumerate(report.recommendations, 1):
        recommendations_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{i}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;"><strong>[{rec['priority']}]</strong> {rec['action']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{rec['impact']}</td>
        </tr>
        """
    
    competitor_html = ""
    for comp in report.competitor_updates:
        competitor_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{comp['domain']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{comp['llms_txt']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{comp['schema_types']}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>GEO Monthly Report — {report.company_name}</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #374151;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #111827;">GEO Health Report — {report.company_name}</h1>
            <p style="color: #6b7280;">Reporting period: {report.period_start[:10]} to {report.period_end[:10]}</p>
            
            <div style="background: #f9fafb; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h2 style="margin-top: 0;">Overall Score</h2>
                <div style="font-size: 48px; font-weight: bold; color: #111827;">
                    {report.current_score}<span style="font-size: 24px; color: #6b7280;">/100</span>
                </div>
                <div style="font-size: 24px; color: {score_color};">
                    {score_sign}{report.score_change} from last month
                </div>
                <div style="font-size: 18px; color: #6b7280; margin-top: 10px;">
                    Grade: <strong>{report.grade}</strong>
                </div>
            </div>
            
            <h2>Changes This Month</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background: #f3f4f6;">
                        <th style="padding: 8px; text-align: left;">Category</th>
                        <th style="padding: 8px; text-align: left;">Change</th>
                        <th style="padding: 8px; text-align: left;">Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {changes_html}
                </tbody>
            </table>
            
            <h2>Top Recommendations</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background: #f3f4f6;">
                        <th style="padding: 8px; text-align: left;">#</th>
                        <th style="padding: 8px; text-align: left;">Action</th>
                        <th style="padding: 8px; text-align: left;">Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {recommendations_html}
                </tbody>
            </table>
            
            <h2>Competitor GEO Posture</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background: #f3f4f6;">
                        <th style="padding: 8px; text-align: left;">Competitor</th>
                        <th style="padding: 8px; text-align: left;">llms.txt</th>
                        <th style="padding: 8px; text-align: left;">Schema Types</th>
                    </tr>
                </thead>
                <tbody>
                    {competitor_html}
                </tbody>
            </table>
            
            <div style="margin-top: 30px; padding: 20px; background: #eff6ff; border-radius: 8px;">
                <h3 style="margin-top: 0;">Need Help?</h3>
                <p>Reply to this email or book a call: <a href="https://calendly.com/rivaledge">calendly.com/rivaledge</a></p>
            </div>
            
            <footer style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 12px;">
                <p>Generated by RivalEdge AI Visibility Platform</p>
                <p><a href="https://rivaledge.ai">rivaledge.ai</a></p>
            </footer>
        </div>
    </body>
    </html>
    """


# ── CLI / Testing ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    
    async def test():
        report = await run_monthly_monitor(
            client_id="test_123",
            url="https://rivaledge.ai",
            company_name="RivalEdge",
            industry="competitive intelligence",
            competitors=["https://www.crayon.co"],
        )
        
        print(f"Monthly Report for {report.company_name}")
        print(f"Score: {report.current_score}/100 (change: {report.score_change:+.0f})")
        print(f"Grade: {report.grade}")
        print(f"Changes detected: {len(report.changes)}")
        
        # Generate email
        email_html = generate_monthly_email(report)
        print(f"\nEmail generated: {len(email_html)} characters")
    
    asyncio.run(test())
