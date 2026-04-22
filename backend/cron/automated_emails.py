"""
Automated email system for RivalEdge
Sends competitive intelligence reports and welcome emails on schedule
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.email_service import send_competitive_intelligence_report, send_welcome_email
from db.supabase import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_users_needing_welcome() -> List[Dict]:
    """Get users who signed up but haven't received welcome email"""
    supabase = get_supabase_client()
    
    # Get users created in last 24 hours with no welcome email sent
    cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    result = supabase.table('users').select('*').gte('created_at', cutoff).execute()
    
    # Filter out users who already got welcome email
    # (We'll need to add a 'welcome_email_sent' column to track this)
    return result.data or []

def get_users_needing_reports() -> List[Dict]:
    """Get users who need their weekly competitive intelligence report"""
    supabase = get_supabase_client()
    
    # Get all active users with competitors
    result = supabase.table('users').select('*, competitors(*)').execute()
    
    users_needing_reports = []
    for user in result.data or []:
        # Check if user has competitors and is due for a report
        if user.get('competitors') and len(user['competitors']) > 0:
            # Check last report sent (we'll need to add this tracking)
            last_report = user.get('last_report_sent')
            
            if not last_report:
                # Never sent a report - send first one
                users_needing_reports.append(user)
            else:
                # Check if it's been a week
                last_date = datetime.fromisoformat(last_report.replace('Z', '+00:00'))
                if datetime.utcnow() - last_date >= timedelta(days=7):
                    users_needing_reports.append(user)
    
    return users_needing_reports

def generate_sample_report_content(user: Dict, competitors: List[Dict]) -> str:
    """Generate sample report content for a user"""
    company_name = user.get('company_name', 'Your Company')
    
    competitor_list = "".join([
        f"<li><strong>{c.get('name', 'Unknown')}:</strong> {c.get('url', '')}</li>"
        for c in competitors
    ])
    
    html = f"""
    <h2>Weekly Competitive Intelligence Report</h2>
    <p><strong>For:</strong> {company_name}</p>
    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
    
    <h3>Your Tracked Competitors</h3>
    <ul>
        {competitor_list}
    </ul>
    
    <h3>Key Updates This Week</h3>
    <p>We're monitoring your competitors for pricing changes, new product launches, 
    funding news, and strategic moves. This is your first automated report - 
    full intelligence begins after we customize your tracking preferences.</p>
    
    <h3>Next Steps</h3>
    <ol>
        <li>Reply to this email with your specific tracking priorities</li>
        <li>Tell us what competitor moves would be most valuable to know about</li>
        <li>We'll customize your weekly reports accordingly</li>
    </ol>
    
    <p>Questions? Just reply to this email.</p>
    """
    
    return html

def send_scheduled_emails():
    """Main function to send all scheduled emails"""
    logger.info("Starting automated email job...")
    
    # Send welcome emails to new users    new_users = get_users_needing_welcome()
    logger.info(f"Found {len(new_users)} new users needing welcome emails")
    
    for user in new_users:
        try:
            email = user.get('email')name = email.split('@')[0] if email else 'User'
            company = user.get('company_name', 'Your Company')
            
            result = send_welcome_email(email, name, company)
            if result['success']:
                logger.info(f"Welcome email sent to {email}")
                # Mark as sent in database
            else:
                logger.error(f"Failed to send welcome email to {email}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
    
    # Send weekly reports
    users_for_reports = get_users_needing_reports()
    logger.info(f"Found {len(users_for_reports)} users needing reports")
    
    for user in users_for_reports:
        try:
            email = user.get('email')
            name = email.split('@')[0] if email else 'User'
            company = user.get('company_name', 'Your Company')
            competitors = user.get('competitors', [])
            
            if not competitors:
                continue
            
            report_content = generate_sample_report_content(user, competitors)
            
            result = send_competitive_intelligence_report(
                to_email=email,
                to_name=name,
                company_name=company,
                report_content=report_content
            )
            
            if result['success']:
                logger.info(f"Report sent to {email}")
                # Update last_report_sent in database
            else:
                logger.error(f"Failed to send report to {email}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending report: {e}")
    
    logger.info("Automated email job completed")

if __name__ == "__main__":
    send_scheduled_emails()
