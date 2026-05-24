"""
Agency Partnership Router

API endpoints for agency partner management, white-label configuration,
and reseller billing.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from auth import get_current_user, resolve_db_id

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class PartnerApplicationRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    website: str = Field(..., min_length=1)
    team_size: int = Field(..., ge=1, le=1000)
    current_clients: int = Field(..., ge=0)
    target_verticals: list[str] = Field(default=[])
    expected_client_volume: int = Field(..., ge=1)
    contact_name: str = Field(..., min_length=1)
    contact_email: str = Field(..., min_length=1)
    tier: str = Field(default="referral")  # referral, reseller, white_label


class PartnerConfigRequest(BaseModel):
    custom_domain: Optional[str] = Field(None)
    brand_color: Optional[str] = Field(None)
    logo_url: Optional[str] = Field(None)
    custom_pricing: Optional[dict] = Field(None)


class PartnerResponse(BaseModel):
    id: str
    company_name: str
    tier: str
    status: str
    revenue_share_percent: int
    wholesale_discount: int
    custom_domain: Optional[str]
    is_active: bool
    created_at: str


# ── Mock Partner Database (replace with real DB) ────────────────────────────

PARTNERS_DB = {}


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/apply")
def apply_for_partnership(body: PartnerApplicationRequest):
    """
    Apply to become a RivalEdge agency partner.
    
    No authentication required — this is a public application endpoint.
    """
    import uuid
    from datetime import datetime, timezone
    
    # Validate tier
    valid_tiers = {"referral", "reseller", "white_label"}
    if body.tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Must be one of: {valid_tiers}",
        )
    
    # Determine terms based on tier
    tier_config = {
        "referral": {"revenue_share": 20, "wholesale_discount": 0, "min_clients": 0},
        "reseller": {"revenue_share": 30, "wholesale_discount": 40, "min_clients": 3},
        "white_label": {"revenue_share": 40, "wholesale_discount": 50, "min_clients": 10},
    }
    
    config = tier_config[body.tier]
    
    # Check minimum client requirement
    if body.expected_client_volume < config["min_clients"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tier '{body.tier}' requires minimum {config['min_clients']} expected clients",
        )
    
    partner_id = str(uuid.uuid4())
    partner = {
        "id": partner_id,
        "company_name": body.company_name,
        "website": body.website,
        "team_size": body.team_size,
        "current_clients": body.current_clients,
        "target_verticals": body.target_verticals,
        "expected_client_volume": body.expected_client_volume,
        "contact_name": body.contact_name,
        "contact_email": body.contact_email,
        "tier": body.tier,
        "status": "pending",  # pending, approved, rejected
        "revenue_share_percent": config["revenue_share"],
        "wholesale_discount": config["wholesale_discount"],
        "custom_domain": None,
        "brand_color": None,
        "logo_url": None,
        "is_active": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    PARTNERS_DB[partner_id] = partner
    
    # TODO: Send notification to admin
    # TODO: Send confirmation email to applicant
    
    return {
        "status": "ok",
        "message": "Application submitted successfully",
        "partner_id": partner_id,
        "tier": body.tier,
        "next_steps": "Our team will review your application within 2 business days.",
    }


@router.get("/status/{partner_id}")
def get_partner_status(partner_id: str):
    """Get status of a partnership application."""
    partner = PARTNERS_DB.get(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner application not found",
        )
    
    return {
        "partner_id": partner_id,
        "status": partner["status"],
        "company_name": partner["company_name"],
        "tier": partner["tier"],
        "is_active": partner["is_active"],
        "applied_at": partner["created_at"],
    }


@router.get("/dashboard", response_model=PartnerResponse)
def get_partner_dashboard(current_user: dict = Depends(get_current_user)):
    """Get partner dashboard data."""
    user_id = resolve_db_id(current_user)
    
    # TODO: Look up partner by user_id in real database
    # For now, return mock data
    
    return PartnerResponse(
        id="mock-partner-id",
        company_name="Mock Agency",
        tier="reseller",
        status="active",
        revenue_share_percent=30,
        wholesale_discount=40,
        custom_domain=None,
        is_active=True,
        created_at="2026-05-24T00:00:00Z",
    )


@router.post("/config")
def update_partner_config(
    body: PartnerConfigRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update partner white-label configuration."""
    user_id = resolve_db_id(current_user)
    
    # TODO: Update in real database
    
    return {
        "status": "ok",
        "message": "Configuration updated",
        "config": body.dict(),
    }


@router.get("/pricing")
def get_partner_pricing():
    """Get partner wholesale pricing."""
    return {
        "retail_pricing": {
            "solo": {"monthly": 49, "annual": 490},
            "pro": {"monthly": 99, "annual": 990},
            "pro_geo": {"monthly": 299, "annual": 2990},
            "enterprise": {"monthly": 999, "annual": 9990},
        },
        "wholesale_discounts": {
            "referral": 0,
            "reseller": 40,
            "white_label": 50,
        },
        "example_margins": {
            "reseller": {
                "pro": {
                    "retail": 99,
                    "wholesale": 59,
                    "your_profit": 40,
                    "margin_percent": 40.4,
                }
            }
        }
    }


@router.get("/tiers")
def get_partner_tiers():
    """Get available partnership tiers."""
    return {
        "tiers": [
            {
                "id": "referral",
                "name": "Referral Partner",
                "description": "Refer clients and earn 20% recurring commission",
                "requirements": "None",
                "revenue_share": 20,
                "wholesale_discount": 0,
                "min_clients": 0,
                "monthly_fee": 0,
                "features": [
                    "Unique referral link",
                    "Partner dashboard",
                    "Monthly payouts",
                    "Co-branded case studies",
                ],
            },
            {
                "id": "reseller",
                "name": "Reseller Partner",
                "description": "White-label reports and resell at your price",
                "requirements": "Minimum 3 client accounts",
                "revenue_share": 30,
                "wholesale_discount": 40,
                "min_clients": 3,
                "monthly_fee": 99,
                "features": [
                    "40% wholesale pricing",
                    "White-label reports",
                    "Client management dashboard",
                    "API access",
                    "Dedicated partner manager",
                ],
            },
            {
                "id": "white_label",
                "name": "White-Label Partner",
                "description": "Full white-label platform under your brand",
                "requirements": "Minimum 10 client accounts",
                "revenue_share": 40,
                "wholesale_discount": 50,
                "min_clients": 10,
                "monthly_fee": 599,
                "features": [
                    "Full white-label platform",
                    "Custom domain",
                    "Custom branding",
                    "Priority feature development",
                    "Dedicated engineering support",
                    "Co-marketing opportunities",
                ],
            },
        ]
    }


@router.post("/clients")
def add_partner_client(
    client_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """Add a client under partner account."""
    user_id = resolve_db_id(current_user)
    
    # TODO: Create client in database with partner_id
    
    return {
        "status": "ok",
        "message": "Client added",
        "client_id": "mock-client-id",
    }


@router.get("/clients")
def list_partner_clients(current_user: dict = Depends(get_current_user)):
    """List clients under partner account."""
    user_id = resolve_db_id(current_user)
    
    # TODO: Query real database
    
    return {
        "clients": [],
        "total": 0,
        "revenue_monthly": 0,
    }


@router.get("/resources")
def get_partner_resources():
    """Get sales and marketing resources for partners."""
    return {
        "sales_collateral": [
            {
                "name": "RivalEdge Pitch Deck",
                "url": "https://rivaledge.ai/partners/pitch-deck.pdf",
                "type": "pdf",
            },
            {
                "name": "Competitive Comparison Sheet",
                "url": "https://rivaledge.ai/partners/comparisons.pdf",
                "type": "pdf",
            },
        ],
        "email_templates": [
            {
                "name": "Cold Outreach",
                "subject": "I ran an AI visibility audit on your brand...",
                "body": "Hi [Name],\n\nI ran a free AI visibility audit on [Brand] and found some interesting gaps compared to your competitors...",
            },
            {
                "name": "Follow-up",
                "subject": "Your competitors are winning in AI search",
                "body": "Hi [Name],\n\nFollowing up on the AI visibility audit I shared...",
            },
        ],
        "case_studies": [
            {
                "client": "Example Agency",
                "challenge": "Needed competitive intelligence for 20 clients",
                "solution": "White-labeled RivalEdge as their CI platform",
                "results": "40% increase in client retention, $50K additional MRR",
            }
        ],
    }
