"""
Land Logic DRONE-MAPPING-AI — Pipeline Concurrency Guard
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Security Addendum: Concurrency Guard
Restricts the number of simultaneous heavy pipeline jobs (OpenCV stitching + AI + GIS)
to prevent CPU/GPU memory exhaustion and denial-of-service.
"""

import os
import asyncio
from fastapi import HTTPException, status

DEFAULT_MAX_CONCURRENT = 2


class ConcurrencyGuard:
    """
    Limits concurrent asynchronous pipeline executions.
    Rejects incoming requests with HTTP 429 Too Many Requests when the limit is reached.
    """

    def __init__(self, limit: int = DEFAULT_MAX_CONCURRENT):
        self.limit = limit
        self._active_count = 0
        self._lock = asyncio.Lock()

    @property
    def active_count(self) -> int:
        return self._active_count

    def get_limit(self) -> int:
        env_val = os.getenv("MAX_CONCURRENT_PIPELINES")
        if env_val:
            try:
                return int(env_val)
            except ValueError:
                pass
        return self.limit

    def set_limit(self, limit: int) -> None:
        self.limit = limit

    async def acquire(self) -> None:
        async with self._lock:
            effective_limit = self.get_limit()
            if self._active_count >= effective_limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Pipeline concurrency limit reached ({effective_limit} active). Please retry shortly."
                )
            self._active_count += 1

    async def release(self) -> None:
        async with self._lock:
            if self._active_count > 0:
                self._active_count -= 1

    def reset(self) -> None:
        self._active_count = 0

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()


# Global pipeline concurrency guard instance
pipeline_concurrency_guard = ConcurrencyGuard()
