"""Tests for outreach email endpoint."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

MOCK_USER = {"sub": "user_123", "email": "ben.d@rivaledge.ai"}
UNAUTH_USER = {"sub": "user_456", "email": "other@example.com"}


def test_send_outreach_requires_auth():
    """Endpoint should reject unauthenticated requests."""
    r = client.post("/api/outreach/send", json={
        "to": "test@example.com",
        "subject": "Test",
        "body": "Hello"
    })
    assert r.status_code in (401, 403)


def test_send_outreach_unauthorized_sender():
    """Only authorized senders (ben.d@rivaledge.ai) can send outreach."""
    with patch("routers.outreach.get_current_user", return_value=UNAUTH_USER):
        r = client.post("/api/outreach/send", json={
            "to": "prospect@example.com",
            "subject": "Test",
            "body": "Hello"
        })
    assert r.status_code == 403


def test_send_outreach_invalid_email():
    """Should reject invalid recipient email."""
    from auth import get_current_user
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    with patch("routers.outreach.RESEND_API_KEY", "re_test_key"):
        r = client.post("/api/outreach/send", json={
            "to": "not-an-email",
            "subject": "Test",
            "body": "Hello"
        })
    app.dependency_overrides.clear()
    assert r.status_code == 400


def test_send_outreach_success():
    """Should send email and return email_id on success."""
    from auth import get_current_user
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "email_abc123"}

    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    with patch("routers.outreach.RESEND_API_KEY", "re_test_key"), \
         patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        r = client.post("/api/outreach/send", json={
            "to": "prospect@company.com",
            "subject": "RivalEdge trial",
            "body": "Hey, want to try RivalEdge?"
        })
    app.dependency_overrides.clear()
    assert r.status_code == 200
    data = r.json()
    assert data["sent"] is True
