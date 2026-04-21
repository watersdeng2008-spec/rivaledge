"""
Email service using Resend API for sending competitive intelligence reports.
"""
import os
import logging
from typing import Optional

import resend

logger = logging.getLogger(__name__)

# Initialize Resend with API key
resend.api_key = os.environ.get("RESEND_API_KEY", "")

FROM_EMAIL = "ben.d@rivaledge.ai"
FROM_NAME = "Ben D - RivalEdge AI"


def send_competitive_intelligence_report(
    to_email: str,
    to_name: str,
    company_name: str,
    report_content: str,
    subject: Optional[str] = None
) -> dict:
    """
    Send a competitive intelligence report email.
    """
    if not resend.api_key:
        logger.error("Resend API key not configured")
        return {"success": False, "error": "Email service not configured"}
    
    try:
        email_subject = subject or f"Your Competitive Intelligence Report - {company_name} Market Analysis"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
                h2 {{ color: #1f2937; margin-top: 30px; }}
                h3 {{ color: #374151; }}
                .executive-summary {{ background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .threat {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 10px 0; }}
                .opportunity {{ background: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px; margin: 10px 0; }}
                ul {{ padding-left: 20px; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <h1>Competitive Intelligence Report</h1>
            <p><strong>For:</strong> {to_name}<br>
            <strong>Company:</strong> {company_name}<br>
            <strong>Date:</strong> {__import__('datetime').datetime.now().strftime('%B %d, %Y')}</p>
            
            {report_content}
            
            <div class="footer">
                <p>This report was prepared by <strong>RivalEdge AI</strong></p>
                <p>Questions? Reply to this email or contact: ben.d@rivaledge.ai</p>
                <p><a href="https://www.rivaledge.ai">www.rivaledge.ai</a></p>
            </div>
        </body>
        </html>
        """
        
        response = resend.Emails.send({
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": email_subject,
            "html": html_content,
            "reply_to": FROM_EMAIL
        })
        
        logger.info(f"Email sent successfully to {to_email}, ID: {response.get('id')}")
        return {
            "success": True,
            "message_id": response.get("id"),
            "to": to_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "to": to_email
        }


def send_welcome_email(to_email: str, to_name: str, company_name: str) -> dict:
    """Send welcome email to new users."""
    if not resend.api_key:
        return {"success": False, "error": "Email service not configured"}
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2563eb; }}.button {{ background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Welcome to RivalEdge!</h1>
            <p>Hi {to_name},</p>
            <p>Thank you for signing up for RivalEdge. We're excited to help {company_name} stay ahead of the competition.</p>
            <p>Your competitive intelligence monitoring is now active. You'll receive your first report within 24 hours.</p>
            <a href="https://www.rivaledge.ai/dashboard" class="button">Go to Dashboard</a>
            <p>Questions? Just reply to this email.</p>
            <p>Best,<br>Ben D<br>RivalEdge AI</p>
        </body>
        </html>
        """
        
        response = resend.Emails.send({
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to_email],
            "subject": f"Welcome to RivalEdge - {company_name} Competitive Monitoring Active",
            "html": html_content,
            "reply_to": FROM_EMAIL
        })
        
        return {
            "success": True,
            "message_id": response.get("id"),
            "to": to_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return {"success": False, "error": str(e)}
