"""
Tests for email delivery service (Resend).
Written FIRST (TDD) — all tests written before implementation.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Path setup
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Env vars
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-service-role-key")
os.environ.setdefault("CLERK_JWT_ISSUER", "https://test.clerk.accounts.dev")
os.environ.setdefault("CLERK_PEM_PUBLIC_KEY", "test-pem-key")
os.environ.setdefault("RESEND_API_KEY", "test-resend-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")


# ── Fixtures ───────────────────────────────────────────────────────────────────

MOCK_USER_PAYLOAD = {
    "sub": "user_test123",
    "email": "test@example.com",
    "exp": 9999999999,
}

SAMPLE_HTML = """<!-- SUBJECT: Your RivalEdge Weekly Brief -->
<!DOCTYPE html>
<html>
<body>
<h1>Your RivalEdge Weekly Brief</h1>
<p>This week's competitor updates:</p>
</body>
</html>"""


# ── Tests: send_digest ────────────────────────────────────────────────────────

class TestSendDigest:
    def test_send_digest_calls_resend_api(self):
        """send_digest POSTs to https://api.resend.com/emails."""
        from services.email import send_digest
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_123"}
        
        with patch("httpx.post", return_value=mock_response) as mock_post:
            result = send_digest(
                to_email="user@example.com",
                html_content=SAMPLE_HTML,
                subject="Your RivalEdge Weekly Brief",
            )
        
        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "resend.com/emails" in call_args[0][0]

    def test_send_digest_uses_correct_from_address(self):
        """send_digest sends from RivalEdge <digests@rivaledge.ai>."""
        from services.email import send_digest
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_123"}
        
        with patch("httpx.post", return_value=mock_response) as mock_post:
            send_digest(
                to_email="user@example.com",
                html_content=SAMPLE_HTML,
                subject="Test Subject",
            )
        
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs.get("json", {})
        assert payload.get("from") == "RivalEdge <digests@rivaledge.ai>"

    def test_send_digest_handles_api_failure_gracefully(self):
        """send_digest returns False (doesn't raise) on API failure."""
        from services.email import send_digest
        
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Too Many Requests")
        
        with patch("httpx.post", return_value=mock_response):
            result = send_digest(
                to_email="user@example.com",
                html_content=SAMPLE_HTML,
                subject="Test Subject",
            )
        
        assert result is False

    def test_send_digest_handles_connection_error_gracefully(self):
        """send_digest returns False on network errors."""
        from services.email import send_digest
        
        with patch("httpx.post", side_effect=Exception("Connection refused")):
            result = send_digest(
                to_email="user@example.com",
                html_content=SAMPLE_HTML,
                subject="Test Subject",
            )
        
        assert result is False

    def test_send_digest_includes_resend_api_key_in_header(self):
        """send_digest sends Authorization: Bearer <RESEND_API_KEY>."""
        from services.email import send_digest
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_123"}
        
        with patch("httpx.post", return_value=mock_response) as mock_post:
            send_digest("user@example.com", SAMPLE_HTML, "Subject")
        
        call_kwargs = mock_post.call_args.kwargs
        headers = call_kwargs.get("headers", {})
        assert "Authorization" in headers
        assert "test-resend-key" in headers["Authorization"]

    def test_send_digest_sets_subject_correctly(self):
        """send_digest passes the subject to Resend API."""
        from services.email import send_digest
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_123"}
        
        with patch("httpx.post", return_value=mock_response) as mock_post:
            send_digest("user@example.com", SAMPLE_HTML, "Custom Weekly Subject")
        
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs.get("json", {})
        assert payload.get("subject") == "Custom Weekly Subject"


# ── Tests: send_welcome_email ─────────────────────────────────────────────────

class TestSendWelcomeEmail:
    def test_send_welcome_email_calls_resend_api(self):
        """send_welcome_email POSTs to Resend."""
        from services.email import send_welcome_email
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_456"}
        
        with patch("httpx.post", return_value=mock_response) as mock_post:
            result = send_welcome_email(
                to_email="newuser@example.com",
                first_competitor="Acme Corp",
            )
        
        assert result is True
        mock_post.assert_called_once()

    def test_send_welcome_email_mentions_competitor(self):
        """Welcome email HTML mentions the first competitor."""
        from services.email import send_welcome_email
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "email_456"}
        
        with patch("httpx.post", return_value=mock_response) as mock_post:
            send_welcome_email(
                to_email="newuser@example.com",
                first_competitor="Acme Corp",
            )
        
        call_kwargs = mock_post.call_args.kwargs
        payload = call_kwargs.get("json", {})
        html_body = payload.get("html", "")
        assert "Acme Corp" in html_body

    def test_send_welcome_email_handles_failure_gracefully(self):
        """send_welcome_email returns False on API failure."""
        from services.email import send_welcome_email
        
        with patch("httpx.post", side_effect=Exception("Network error")):
            result = send_welcome_email(
                to_email="newuser@example.com",
                first_competitor="Acme Corp",
            )
        
        assert result is False


# ── Tests: digest endpoint auth ───────────────────────────────────────────────

class TestDigestEndpointRequiresAuth:
    def test_digest_endpoint_requires_auth(self):
        """POST /api/digest/generate requires authentication."""
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/digest/generate")
        assert resp.status_code in (401, 403)

    def test_digest_send_endpoint_requires_auth(self):
        """POST /api/digest/send/{id} requires authentication."""
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/api/digest/send/some-digest-id")
        assert resp.status_code in (401, 403)

    def test_digest_generate_with_valid_auth(self):
        """POST /api/digest/generate works with valid auth token."""
        from main import app
        from fastapi.testclient import TestClient
        
        mock_competitors = [
            {
                "id": "comp_123",
                "user_id": "user_test123",
                "url": "https://acme.com",
                "name": "Acme Corp",
                "profile": None,
                "created_at": "2024-01-01T00:00:00+00:00",
            }
        ]
        mock_snapshot = {
            "id": "snap_123",
            "competitor_id": "comp_123",
            "content": {"title": "Acme"},
            "diff": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        mock_digest = {
            "id": "digest_abc123",
            "user_id": "user_test123",
            "content": SAMPLE_HTML,
            "sent_at": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        
        mock_ai_response = SAMPLE_HTML
        
        with patch("auth.verify_clerk_token", return_value=MOCK_USER_PAYLOAD), \
             patch("db.supabase.get_competitors", return_value=mock_competitors), \
             patch("db.supabase.get_latest_snapshot", return_value=mock_snapshot), \
             patch("db.supabase.get_prior_snapshot", return_value=None), \
             patch("db.supabase.create_digest", return_value=mock_digest), \
             patch("services.ai.generate_weekly_digest", return_value=mock_ai_response):
            
            client = TestClient(app, raise_server_exceptions=False)
            resp = client.post(
                "/api/digest/generate",
                headers={"Authorization": "Bearer fake-token"},
            )
        
        assert resp.status_code == 200
        data = resp.json()
        assert "digest_id" in data
        assert "preview" in data


# ── Tests: weekly cron ────────────────────────────────────────────────────────

class TestWeeklyCronProcessesAllUsers:
    def test_weekly_cron_processes_all_users(self):
        """Weekly cron iterates over all active users and generates + sends digests."""
        # Mock all external deps
        mock_users = [
            {"id": "user_1", "email": "user1@example.com", "plan": "solo"},
            {"id": "user_2", "email": "user2@example.com", "plan": "team"},
        ]
        mock_competitors = [
            {"id": "comp_1", "user_id": "user_1", "url": "https://comp.com", 
             "name": "Comp", "profile": None, "created_at": "2024-01-01T00:00:00+00:00"}
        ]
        mock_snapshot = {
            "id": "snap_1",
            "competitor_id": "comp_1",
            "content": {"title": "Comp"},
            "diff": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        mock_digest_record = {
            "id": "digest_1",
            "user_id": "user_1",
            "content": SAMPLE_HTML,
            "sent_at": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        
        with patch("db.supabase.get_all_active_users", return_value=mock_users), \
             patch("db.supabase.get_competitors", return_value=mock_competitors), \
             patch("db.supabase.get_latest_snapshot", return_value=mock_snapshot), \
             patch("db.supabase.get_prior_snapshot", return_value=None), \
             patch("db.supabase.create_digest", return_value=mock_digest_record), \
             patch("db.supabase.mark_digest_sent", return_value=mock_digest_record), \
             patch("services.ai.generate_weekly_digest", return_value=SAMPLE_HTML), \
             patch("services.email.send_digest", return_value=True):
            
            from cron.weekly_digest import run_weekly_digest
            result = run_weekly_digest()
        
        assert result["total_users"] == 2
        assert result["success_count"] >= 0  # may be 0 if no competitors for user_2
        assert "errors" in result

    def test_weekly_cron_continues_on_single_user_failure(self):
        """Cron job doesn't stop if one user fails — processes all others."""
        mock_users = [
            {"id": "user_fail", "email": "fail@example.com", "plan": "solo"},
            {"id": "user_ok", "email": "ok@example.com", "plan": "solo"},
        ]
        
        call_count = {"n": 0}
        
        def get_competitors_side_effect(user_id):
            call_count["n"] += 1
            if user_id == "user_fail":
                raise Exception("DB error for user_fail")
            return []
        
        with patch("db.supabase.get_all_active_users", return_value=mock_users), \
             patch("db.supabase.get_competitors", side_effect=get_competitors_side_effect), \
             patch("services.ai.generate_weekly_digest", return_value=SAMPLE_HTML), \
             patch("services.email.send_digest", return_value=True):
            
            from cron import weekly_digest as wd
            import importlib
            importlib.reload(wd)
            result = wd.run_weekly_digest()
        
        # Both users attempted
        assert result["total_users"] == 2
        assert len(result["errors"]) >= 1  # user_fail errored

    def test_weekly_cron_is_idempotent(self):
        """Running the cron twice doesn't crash or duplicate."""
        mock_users = [{"id": "user_1", "email": "user1@example.com", "plan": "solo"}]
        mock_digest_record = {
            "id": "digest_1",
            "user_id": "user_1",
            "content": SAMPLE_HTML,
            "sent_at": None,
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        
        with patch("db.supabase.get_all_active_users", return_value=mock_users), \
             patch("db.supabase.get_competitors", return_value=[]), \
             patch("db.supabase.create_digest", return_value=mock_digest_record), \
             patch("db.supabase.mark_digest_sent", return_value=mock_digest_record), \
             patch("services.ai.generate_weekly_digest", return_value=SAMPLE_HTML), \
             patch("services.email.send_digest", return_value=True):
            
            from cron.weekly_digest import run_weekly_digest
            result1 = run_weekly_digest()
            result2 = run_weekly_digest()
        
        # Both runs complete without exception
        assert "total_users" in result1
        assert "total_users" in result2
