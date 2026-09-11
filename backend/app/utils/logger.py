"""
Structured Logger Utility
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""

import logging
import sys

logger = logging.getLogger("land_logic")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_request(request_id: str, stage: str, duration_ms: float, outcome: str) -> None:
    """
    Logs one structured line per pipeline stage with execution metrics.
    """
    logger.info(
        f"[request_id={request_id}] [stage={stage}] [duration_ms={duration_ms:.2f}] [outcome={outcome}]"
    )
