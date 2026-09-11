"""
Structured Logger Utility
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""

import logging
import sys

# Configure standard logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("LandLogic")


def log_pipeline_event(member: str, stage: str, message: str):
    """
    Logs an event labeled with the corresponding team member.
    Example: log_pipeline_event('M4', 'OPENCV', 'SIFT matching completed')
    """
    logger.info(f"[{member}] [{stage}] {message}")
