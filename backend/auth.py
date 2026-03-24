"""
Clerk JWT validation middleware.

Clerk issues RS256 JWTs. We validate using the PEM public key
provided via CLERK_PEM_PUBLIC_KEY env var.

Usage:
    from auth import get_current_user
    
    @router.get("/me")
    def me(user = Depends(get_current_user)):
        return {"user_id": user["sub"]}
"""
import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


def _get_public_key() -> str:
    key = os.environ.get("CLERK_PEM_PUBLIC_KEY", "")
    if not key:
        raise RuntimeError("CLERK_PEM_PUBLIC_KEY env var not set")
    # Support both raw PEM and base64-encoded PEM (Railway env var quirk)
    return key.replace("\\n", "\n")


def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT and return the decoded payload.
    Raises jwt.PyJWTError on failure.
    """
    public_key = _get_public_key()
    issuer = os.environ.get("CLERK_JWT_ISSUER", "")
    
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=issuer if issuer else None,
        options={
            "verify_aud": False,  # Clerk JWTs don't always have audience
        },
    )
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    FastAPI dependency — extracts and validates the Clerk JWT from
    the Authorization: Bearer <token> header.
    
    Returns the decoded JWT payload (includes sub, email, etc.).
    Raises 401 if token is missing or invalid.
    """
    token = credentials.credentials
    try:
        payload = verify_clerk_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    """Optional auth — returns None if no token provided."""
    if not credentials:
        return None
    try:
        return verify_clerk_token(credentials.credentials)
    except jwt.InvalidTokenError:
        return None
