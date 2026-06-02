"""
Clerk JWT verification + beta-access guard.

Uses Clerk's JWKS endpoint to verify tokens without a third-party Clerk SDK.
The public keys are cached in-memory after the first fetch.
"""

import json
import logging
from functools import lru_cache

import httpx
from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt

from app.settings import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JWKS key cache
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _get_jwks() -> list[dict]:
    """Fetch and cache Clerk's public keys (JWKS). Cached for the process lifetime."""
    if not settings.clerk_jwks_url:
        # Dev mode: skip auth
        return []
    resp = httpx.get(settings.clerk_jwks_url, timeout=10)
    resp.raise_for_status()
    return resp.json()["keys"]


def _refresh_jwks() -> None:
    """Force a JWKS refresh (call on 401 to handle key rotation)."""
    _get_jwks.cache_clear()


# ---------------------------------------------------------------------------
# JWT verification
# ---------------------------------------------------------------------------


def _verify_token(token: str) -> dict:
    """Decode and verify a Clerk JWT. Returns the payload."""
    keys = _get_jwks()
    if not keys:
        # Dev mode: accept any token, return a synthetic payload
        logger.warning("CLERK_JWKS_URL not set — skipping JWT verification (dev mode)")
        return {"sub": "dev_user_id", "public_metadata": {"beta_access": True}}

    # Try each key (Clerk rotates keys; usually only one active)
    last_err: Exception | None = None
    for key in keys:
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={"verify_aud": False},  # Clerk tokens don't always set aud
            )
            return payload
        except JWTError as e:
            last_err = e
            continue

    # Keys may have rotated — try once after refresh
    _refresh_jwks()
    for key in _get_jwks():
        try:
            return jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
        except JWTError:
            continue

    raise HTTPException(401, f"Invalid token: {last_err}")


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------


async def get_current_user(authorization: str = Header(default="")) -> str:
    """Extract and verify the Clerk JWT. Returns clerk_user_id."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or malformed Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = _verify_token(token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(401, f"Token verification failed: {exc}") from exc
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Token missing 'sub' claim")
    return user_id


async def require_beta_access(user_id: str = Depends(get_current_user)) -> str:
    """
    Gate access to beta users only.
    Check publicMetadata.beta_access via Clerk REST API.
    Falls back to allowing all in dev mode (no CLERK_API_KEY set).
    """
    if not settings.clerk_api_key:
        # Dev mode — allow everyone
        return user_id

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.clerk.com/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {settings.clerk_api_key}"},
                timeout=5,
            )
            resp.raise_for_status()
            user_data = resp.json()
    except Exception as exc:
        logger.error("Failed to fetch Clerk user %s: %s", user_id, exc)
        raise HTTPException(503, "Auth service unavailable") from exc

    beta_access = user_data.get("public_metadata", {}).get("beta_access", False)
    if not beta_access:
        raise HTTPException(
            403,
            "Beta access required. Join the waitlist at https://archon.dev",
        )
    return user_id
