"""
Pydantic Data Schemas for Land Logic API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., example="Greenfield Farm Survey Alpha")
    description: Optional[str] = Field(None, example="High-altitude DJI drone flight")
    target_crs: Optional[str] = Field("EPSG:4326", example="EPSG:4326")


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    image_count: int = 0
    metrics: Optional[Dict[str, Any]] = None


class StitchRequest(BaseModel):
    feature_detector: Optional[str] = "SIFT"
    blend_mode: Optional[str] = "MULTIBAND"
    downscale_factor: Optional[float] = 1.0


class AIAnalyzeRequest(BaseModel):
    tasks: List[str] = ["land_use_segmentation", "crop_health_ndvi"]
    confidence_threshold: Optional[float] = 0.50
    tile_size: Optional[int] = 512


class JobStatusResponse(BaseModel):
    job_id: str
    project_id: str
    stage: str
    status: str
    progress_pct: float
    message: str
    updated_at: datetime
