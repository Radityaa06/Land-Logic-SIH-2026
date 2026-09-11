"""
Unified Predict & Pipeline Route
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Implements the central pipeline coordinator route:
Frontend -> POST /predict -> Backend -> OpenCV -> AI -> GIS -> Backend -> Frontend
"""

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import PredictResponse
from app.services.pipeline import execute_pipeline
from app.services.errors import PipelineStageError

router = APIRouter()

UPLOAD_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dng"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15MB


@router.post("/predict", response_model=PredictResponse, tags=["Pipeline & Prediction"])
@router.post("/api/v1/predict", response_model=PredictResponse, tags=["Pipeline & Prediction"])
async def predict(
    files: Optional[List[UploadFile]] = File(None),
    project_id: Optional[str] = Form(None)
):
    """
    Executes the drone mapping pipeline:
    Receives drone images -> OpenCV (Stitching) -> AI (Land/Crop Analysis) -> GIS (GeoJSON / Telemetry)
    Returns structured results with explicit coordinate_space ('geographic' or 'pixel').
    """
    # 1. Validate all files before writing anything to disk
    if files:
        for file in files:
            ext = os.path.splitext(file.filename or "")[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=422,
                    detail=f"Unsupported file format '{ext}' in '{file.filename}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                )

            # Check size via attribute or by reading and rewinding
            size = getattr(file, "size", None)
            if size is not None:
                if size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=422,
                        detail=f"File '{file.filename}' exceeds 15MB limit ({size / (1024 * 1024):.1f}MB)"
                    )
            else:
                content = await file.read()
                if len(content) > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=422,
                        detail=f"File '{file.filename}' exceeds 15MB limit ({len(content) / (1024 * 1024):.1f}MB)"
                    )
                await file.seek(0)

    proj_id = project_id or f"proj_{uuid.uuid4().hex[:8]}"
    project_dir = os.path.join(UPLOAD_BASE_DIR, proj_id)
    os.makedirs(project_dir, exist_ok=True)

    saved_paths = []

    if files:
        for file in files:
            file_path = os.path.join(project_dir, file.filename)
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            saved_paths.append(file_path)
    else:
        # Check if project already has uploaded files
        if os.path.exists(project_dir):
            for f in os.listdir(project_dir):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".dng")):
                    saved_paths.append(os.path.join(project_dir, f))

    # If no files were uploaded or found, use empty list (pipeline generates calibrated baseline)
    try:
        res = execute_pipeline(proj_id, saved_paths, OUTPUT_BASE_DIR)
    except PipelineStageError as e:
        raise HTTPException(
            status_code=500,
            detail=f"{e.stage} failed: {e.detail}"
        )

    # Attach public URL references
    artifact_urls = {
        "stitched_image_url": f"/api/v1/projects/{proj_id}/artifacts/stitched_orthomosaic.png",
        "mask_url": f"/api/v1/projects/{proj_id}/artifacts/segmentation_mask.png",
        "geojson_url": f"/api/v1/projects/{proj_id}/layers/parcels.geojson"
    }

    return {
        "status": res["status"],
        "message": res["message"],
        "project_id": proj_id,
        "coordinate_space": res["coordinate_space"],
        "summary": res["summary"],
        "geojson": res["geojson"],
        "artifacts": artifact_urls
    }
