"""
Price tracking service for RivalEdge
Monitors competitor prices across retail channels and sends alerts on significant changes.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import db.supabase as db
from services.email import send_digest

logger = logging.getLogger(__name__)

# Price tracking configuration
DEFAULT_ALERT_THRESHOLD = 0.02  # 2% change
SCAN_INTERVAL_HOURS = 2

# Retail channels to monitor
RETAIL_CHANNELS = [
    "amazon",
    "walmart", 
    "website",
    "ebay",
    "bestbuy",
    "target"
]


def extract_price_from_snapshot(snapshot_content: dict, channel: str = "website") -> Optional[float]:
    """
    Extract price from competitor snapshot content.
    Looks for common price fields and formats.
    """
    if not snapshot_content:
        return None
    
    # Common price field names
    price_fields = [
        "price",
        "pricing",
        "current_price",
        "sale_price",
        "discounted_price",
        f"{channel}_price"
    ]
    
    for field in price_fields:
        value = snapshot_content.get(field)
        if value is not None:
            try:
                # Handle string prices (e.g., "$49.99" or "49.99 USD")
                if isinstance(value, str):
                    # Remove currency symbols and commas
                    cleaned = value.replace("$", "").replace("€", "").replace("£", "")
                    cleaned = cleaned.replace(",", "").strip()
                    # Extract first number
                    import re
                    numbers = re.findall(r'\d+\.?\d*', cleaned)
                    if numbers:
                        return float(numbers[0])
                elif isinstance(value, (int, float)):
                    return float(value)
            except (ValueError, TypeError):
                continue
    
    return None


def calculate_price_change(old_price: float, new_price: float) -> Dict[str, Any]:
    """
    Calculate price change metrics.
    Returns dict with change_amount, change_percent, and direction.
    """
    if old_price is None or new_price is None or old_price == 0:
        return {
            "change_amount": 0,
            "change_percent": 0,
            "direction": "unknown"
        }
    
    change_amount = new_price - old_price
    change_percent = (change_amount / old_price)
    
    direction = "increase" if change_amount > 0 else "decrease" if change_amount < 0 else "no_change"
    
    return {
        "change_amount": round(change_amount, 2),
        "change_percent": round(change_percent, 4),
        "direction": direction
    }


def should_trigger_alert(change_percent: float, threshold: float = DEFAULT_ALERT_THRESHOLD) -> bool:
    """
    Determine if a price change should trigger an alert.
    Alerts on changes >= threshold (default 2%).
    """
    return abs(change_percent) >= threshold


def scan_competitor_prices(competitor_id: str) -> List[Dict[str, Any]]:
    """
    Scan a competitor's current prices across all tracked channels.
    Returns list of price data for each channel.
    """
    # Get latest snapshot
    latest = db.get_latest_snapshot(competitor_id)
    if not latest:
        logger.warning(f"No snapshot found for competitor {competitor_id}")
        return []
    
    content = latest.get("content", {})
    prices = []
    
    # Check each retail channel
    for channel in RETAIL_CHANNELS:
        price = extract_price_from_snapshot(content, channel)
        if price is not None:
            prices.append({
                "channel": channel,
                "price": price,
                "snapshot_id": latest.get("id"),
                "checked_at": latest.get("created_at")
            })
    
    return prices


def check_price_changes(user_id: str, competitor_id: str) -> List[Dict[str, Any]]:
    """
    Check for price changes for a specific competitor.
    Compares current prices with historical data.
    Returns list of alerts that should be sent.
    """
    # Get user's alert threshold
    user = db.get_user(user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        return []
    
    threshold = user.get("price_alert_threshold", DEFAULT_ALERT_THRESHOLD)
    
    # Get current prices
    current_prices = scan_competitor_prices(competitor_id)
    if not current_prices:
        return []
    
    # Get price history
    price_history = db.get_price_history(competitor_id, limit=10)
    
    alerts = []
    
    for current in current_prices:
        channel = current["channel"]
        new_price = current["price"]
        
        # Find previous price for this channel
        previous = None
        for hist in price_history:
            if hist.get("channel") == channel:
                previous = hist
                break
        
        if previous:
            old_price = previous.get("price")
            
            # Calculate change
            change = calculate_price_change(old_price, new_price)
            
            # Check if alert should be triggered
            if should_trigger_alert(change["change_percent"], threshold):
                alerts.append({
                    "user_id": user_id,
                    "competitor_id": competitor_id,
                    "channel": channel,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_amount": change["change_amount"],
                    "change_percent": change["change_percent"],
                    "direction": change["direction"],
                    "threshold": threshold
                })
    
    return alerts


def process_price_alerts() -> Dict[str, Any]:
    """
    Main entry point for price tracking.
    Scans all users with price tracking enabled and creates alerts.
    Returns summary of processing.
    """
    logger.info("Starting price tracking scan...")
    
    # Get users with price tracking enabled
    users = db.get_users_with_price_tracking()
    
    total_checked = 0
    total_alerts = 0
    errors = []
    
    for user in users:
        user_id = user.get("id")
        
        try:
            # Get competitors with price tracking for this user
            competitors = db.get_competitors_with_price_tracking(user_id)
            
            for competitor in competitors:
                competitor_id = competitor.get("id")
                total_checked += 1
                
                # Check for price changes
                alerts = check_price_changes(user_id, competitor_id)
                
                for alert in alerts:
                    # Create alert in database
                    db.create_price_alert(
                        user_id=alert["user_id"],
                        competitor_id=alert["competitor_id"],
                        old_price=alert["old_price"],
                        new_price=alert["new_price"],
                        change_percent=alert["change_percent"],
                        channel=alert["channel"]
                    )
                    total_alerts += 1
                    
        except Exception as e:
            logger.error(f"Error processing user {user_id}: {e}")
            errors.append({"user_id": user_id, "error": str(e)})
    
    result = {
        "users_scanned": len(users),
        "competitors_checked": total_checked,
        "alerts_created": total_alerts,
        "errors": errors,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"Price tracking complete: {result}")
    return result


def send_price_alert_email(alert_id: str) -> bool:
    """
    Send a price alert email to the user.
    Returns True if sent successfully.
    """
    # Get alert details
    alerts = db.get_pending_price_alerts()
    alert = next((a for a in alerts if a.get("id") == alert_id), None)
    
    if not alert:
        logger.warning(f"Alert {alert_id} not found or already sent")
        return False
    
    user_id = alert.get("user_id")
    user = db.get_user(user_id)
    
    if not user:
        logger.warning(f"User {user_id} not found")
        return False
    
    user_email = user.get("email")
    if not user_email:
        logger.warning(f"User {user_id} has no email")
        return False
    
    # Get competitor details
    competitor_id = alert.get("competitor_id")
    competitors = db.get_competitors(user_id)
    competitor = next((c for c in competitors if c.get("id") == competitor_id), None)
    competitor_name = competitor.get("name", "Unknown Competitor") if competitor else "Unknown Competitor"
    
    # Build email content
    direction = alert.get("direction", "changed")
    change_percent = abs(alert.get("change_percent", 0)) * 100
    old_price = alert.get("old_price", 0)
    new_price = alert.get("new_price", 0)
    channel = alert.get("channel", "website")
    
    direction_text = "increased" if direction == "increase" else "decreased" if direction == "decrease" else "changed"
    direction_color = "#ef4444" if direction == "increase" else "#22c55e" if direction == "decrease" else "#f59e0b"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Price Alert - RivalEdge</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #0f172a; color: #ffffff;">
  <div style="max-width: 600px; margin: 40px auto; background: #1e293b; border-radius: 8px; overflow: hidden; border: 1px solid #334155;">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 32px 40px;">
      <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700;">⚡ Price Alert</h1>
      <p style="margin: 8px 0 0; color: rgba(255,255,255,0.85); font-size: 14px;">Significant price change detected</p>
    </div>
    
    <!-- Alert Body -->
    <div style="padding: 40px;">
      <div style="background: #0f172a; border-radius: 8px; padding: 24px; margin-bottom: 24px; border-left: 4px solid {direction_color};">
        <h2 style="margin: 0 0 16px; color: #ffffff; font-size: 18px;">{competitor_name}</h2>
        
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase;">Old Price</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: 600; text-decoration: line-through;">${old_price:.2f}</div>
          </div>
          
          <div style="color: {direction_color}; font-size: 20px;">→</div>
          
          <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase;">New Price</div>
            <div style="color: {direction_color}; font-size: 24px; font-weight: 600;">${new_price:.2f}</div>
          </div>
        </div>
        
        <div style="background: {direction_color}20; border-radius: 6px; padding: 12px; text-align: center;">
          <span style="color: {direction_color}; font-size: 16px; font-weight: 600;">
            Price {direction_text} by {change_percent:.1f}%
          </span>
        </div>
        
        <div style="margin-top: 16px; color: #94a3b8; font-size: 14px;">
          Channel: {channel.upper()}<br>
          Detected: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
      </div>
      
      <div style="background: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
        <h3 style="margin: 0 0 12px; color: #ffffff; font-size: 16px;">💡 Recommended Actions</h3>
        <ul style="color: #cbd5e1; line-height: 1.6; font-size: 14px; padding-left: 20px; margin: 0;">
          <li>Review your pricing strategy in response to this change</li>
          <li>Check if this is a temporary promotion or permanent change</li>
          <li>Consider updating your competitive positioning</li>
          <li>Monitor customer reactions over the next few days</li>
        </ul>
      </div>
      
      <div style="text-align: center;">
        <a href="https://rivaledge.ai/dashboard" 
           style="display: inline-block; background: #6366f1; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 15px; font-weight: 600;">
          View Dashboard →
        </a>
      </div>
    </div>
    
    <!-- Footer -->
    <div style="background: #0f172a; border-top: 1px solid #334155; padding: 24px 40px; text-align: center;">
      <p style="margin: 0; color: #64748b; font-size: 12px;">
        RivalEdge · AI Competitor Intelligence<br>
        <a href="{{{{unsubscribe_url}}}}" style="color: #6366f1;">Unsubscribe</a> · 
        <a href="https://rivaledge.ai/settings" style="color: #6366f1;">Manage Alerts</a>
      </p>
    </div>
  </div>
</body>
</html>"""
    
    # Send email
    subject = f"🚨 Price Alert: {competitor_name} price {direction_text} {change_percent:.1f}%"
    
    sent = send_digest(user_email, html_content, subject)
    
    if sent:
        # Mark alert as sent
        db.mark_price_alert_sent(alert_id)
        logger.info(f"Price alert sent to {user_email} for {competitor_name}")
    else:
        logger.error(f"Failed to send price alert to {user_email}")
    
    return sent


def process_and_send_pending_alerts() -> Dict[str, Any]:
    """
    Process all pending price alerts and send emails.
    Returns summary of sent alerts.
    """
    logger.info("Processing pending price alerts...")
    
    pending = db.get_pending_price_alerts()
    
    sent_count = 0
    failed_count = 0
    
    for alert in pending:
        alert_id = alert.get("id")
        
        try:
            if send_price_alert_email(alert_id):
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"Error sending alert {alert_id}: {e}")
            failed_count += 1
    
    result = {
        "pending_alerts": len(pending),
        "sent": sent_count,
        "failed": failed_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"Alert processing complete: {result}")
    return result
