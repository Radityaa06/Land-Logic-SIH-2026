"""
Land Logic DRONE-MAPPING-AI — API Key Authentication Module (Re-export)
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Consolidated into app.dependencies to ensure a single canonical implementation.
Re-exported here to maintain backward compatibility across module imports.
"""

from app.dependencies import (
    verify_api_key,
    verify_sse_api_key,
    API_KEY_HEADER,
)

__all__ = ["verify_api_key", "verify_sse_api_key", "API_KEY_HEADER"]
