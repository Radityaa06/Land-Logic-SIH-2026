"""
Pipeline error definitions
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""


class PipelineStageError(Exception):
    """Raised when a discrete pipeline stage fails during execution."""
    def __init__(self, stage: str, detail: str):
        self.stage = stage
        self.detail = detail
        super().__init__(f"{stage} failed: {detail}")
