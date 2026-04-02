"""
Onboarding trigger — emails users who signed up but haven't added a competitor.
Runs every 30 minutes via Railway cron.
"""
import os
import httpx
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
RESEND_KEY = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "ben.d@rivaledge.ai")

def get_users_without_competitors():
    """Find users who signed up 2-24 hours ago and have 0 competitors."""
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    now = datetime.now(timezone.utc)
    two_hours_ago = (now - timedelta(hours=2)).isoformat()
    twenty_four_hours_ago = (now - timedelta(hours=24)).isoformat()
    
    # Get users who signed up in the 2-24 hour window
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/users?created_at=gte.{twenty_four_hours_ago}&created_at=lte.{two_hours_ago}&select=id,email",
        headers=headers, timeout=10
    )
    users = r.json() if r.status_code == 200 else []
    
    # Filter to those with 0 competitors
    no_competitor_users = []
    for user in users:
        if not user.get("email") or "@unknown.local" in user["email"]:
            continue
        r2 = httpx.get(
            f"{SUPABASE_URL}/rest/v1/competitors?user_id=eq.{user['id']}&select=id",
            headers=headers, timeout=10
        )
        competitors = r2.json() if r2.status_code == 200 else []
        if len(competitors) == 0:
            no_competitor_users.append(user)
    
    return no_competitor_users

def send_onboarding_email(user_email: str, user_id: str):
    """Send the onboarding nudge email."""
    html = """
<!DOCTYPE html>
<html>
<head><style>
body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #e2e8f0; background: #0f172a; }
.btn { display: inline-block; background: #3b82f6; color: white !important; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; }
p { color: #94a3b8; line-height: 1.6; }
h2 { color: #f8fafc; }
</style></head>
<body>
<h2>Your RivalEdge account is ready 🎯</h2>
<p>You signed up but haven't added your first competitor yet.</p>
<p>Most sellers start by tracking their top 3 rivals — the ones you check manually every week. RivalEdge watches them automatically and sends you a briefing every Monday morning.</p>
<p><strong>It takes 30 seconds to set up:</strong></p>
<ol>
<li>Go to your dashboard</li>
<li>Paste a competitor's URL (e.g. cdw.com)</li>
<li>We'll scrape it and start monitoring immediately</li>
</ol>
<p><a href="https://www.rivaledge.ai/dashboard" class="btn">Add your first competitor →</a></p>
<p style="font-size:12px; color: #475569;">You're on the 14-day free trial. No credit card required.</p>
</body>
</html>
"""
    
    payload = {
        "from": f"Ben D <{FROM_EMAIL}>",
        "to": [user_email],
        "subject": "Your competitors aren't going to track themselves 👀",
        "html": html,
    }
    
    r = httpx.post(
        "https://api.resend.com/emails",
        json=payload,
        headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
        timeout=15
    )
    return r.status_code == 200

def mark_onboarding_sent(user_id: str):
    """Add a tag to prevent re-sending."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    # Insert into feedback table as a system event (reuse existing table)
    httpx.post(
        f"{SUPABASE_URL}/rest/v1/feedback",
        json={"user_id": user_id, "reaction": "system", "message": "onboarding_email_sent", "page": "cron"},
        headers=headers, timeout=10
    )

def already_sent(user_id: str) -> bool:
    """Check if we already sent the onboarding email."""
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/feedback?user_id=eq.{user_id}&reaction=eq.system&message=eq.onboarding_email_sent&limit=1",
        headers=headers, timeout=10
    )
    data = r.json() if r.status_code == 200 else []
    return len(data) > 0

def run():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Running onboarding email cron...")
    
    if not RESEND_KEY:
        print("RESEND_API_KEY not set — skipping")
        return
    
    users = get_users_without_competitors()
    print(f"Found {len(users)} users without competitors in 2-24hr window")
    
    sent = 0
    for user in users:
        if already_sent(user["id"]):
            print(f"  Already sent to {user['email']} — skipping")
            continue
        
        if send_onboarding_email(user["email"], user["id"]):
            mark_onboarding_sent(user["id"])
            print(f"  ✅ Sent to {user['email']}")
            sent += 1
        else:
            print(f"  ❌ Failed for {user['email']}")
    
    print(f"Done. Sent {sent} onboarding emails.")

if __name__ == "__main__":
    run()
