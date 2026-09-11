"""
Land Logic DRONE-MAPPING-AI — API Key Authentication Module
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Security Addendum: API Key Auth
Enforces optional API key authentication via environment variable 'API_KEY'.
If 'API_KEY' is not configured or empty, requests are allowed without credentials (for local dev).
If 'API_KEY' is set, requests must supply a valid key via the 'X-API-Key' header.
"""

import os
import secrets
from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_expected_api_key() -> Optional[str]:
    key = os.getenv("API_KEY", "").strip()
    return key if key else None


async def verify_api_key(
    api_key_header: Optional[str] = Security(API_KEY_HEADER)
) -> Optional[str]:
    """
    Validates the incoming X-API-Key header against the configured API_KEY.
    Uses constant-time comparison (secrets.compare_digest) to prevent timing attacks.
    """
    expected_key = get_expected_api_key()

    # If no API key is configured in the environment, bypass auth (development mode)
    if not expected_key:
        return None

    # If an API key is configured, header is mandatory and must match
    if not api_key_header or not secrets.compare_digest(api_key_header, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide a valid 'X-API-Key' header."
        )

    return api_key_header
