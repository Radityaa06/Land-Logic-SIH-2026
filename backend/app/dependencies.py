"""
Dependencies and Security Guards
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Security Addendum:
- API Key verification dependency for /predict endpoints
- Concurrency guard limiting in-flight pipeline executions
"""

import os
import secrets
import asyncio
from typing import Optional
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.utils.logger import logger

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Render free/starter tiers have 1 vCPU and 512MB RAM.
# Capping concurrent heavy stitching/AI pipeline jobs to 3 prevents worker OOM crashes.
DEFAULT_MAX_CONCURRENT_REQUESTS = 3


def log_startup_security_warnings() -> None:
    """Logs startup warning if API_KEY is missing from the environment."""
    if not os.getenv("API_KEY"):
        logger.warning(
            "[SECURITY] API_KEY is not set in the environment! "
            "Protected routes (/predict) will reject requests (fail-closed) until configured."
        )


async def verify_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """
    Validates the X-API-Key header against the configured API_KEY environment variable.
    Fails closed: if API_KEY is unset on the server, requests are rejected with 401.
    Uses constant-time comparison (secrets.compare_digest) to prevent timing attacks.
    """
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        logger.warning("[SECURITY] Rejected request: API_KEY is not configured on the server.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key authentication required but no API_KEY configured on server"
        )

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

    return api_key


class ConcurrencyGuard:
    """
    Async concurrency guard capping simultaneous in-flight pipeline runs.
    Returns HTTP 503 when the server is at capacity to prevent memory exhaustion.
    """

    def __init__(self, limit: int = DEFAULT_MAX_CONCURRENT_REQUESTS):
        self.limit = limit
        self._active_count = 0
        self._lock = asyncio.Lock()

    def get_limit(self) -> int:
        env_val = os.getenv("MAX_CONCURRENT_REQUESTS")
        if env_val:
            try:
                return int(env_val)
            except ValueError:
                pass
        return self.limit

    def set_limit(self, limit: int) -> None:
        self.limit = limit

    def reset(self) -> None:
        self._active_count = 0

    async def acquire(self) -> None:
        async with self._lock:
            effective_limit = self.get_limit()
            if self._active_count >= effective_limit:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Server busy, try again in a moment"
                )
            self._active_count += 1

    async def release(self) -> None:
        async with self._lock:
            if self._active_count > 0:
                self._active_count -= 1

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()


# Global concurrency guard instance for pipeline requests
pipeline_concurrency_guard = ConcurrencyGuard()
