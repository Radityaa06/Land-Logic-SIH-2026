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
import asyncio
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from PIL import Image

from app.models.schemas import PredictResponse
from app.services.pipeline import execute_pipeline
from app.services.errors import PipelineStageError
from app.dependencies import verify_api_key, pipeline_concurrency_guard

router = APIRouter()

UPLOAD_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dng"}
# 15MB limit per image prevents excessive memory consumption on single-worker deployments
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15MB
# 90s timeout provides headroom for multi-image SIFT stitching and sliding-window tile inference while preventing hung jobs from locking concurrency slots indefinitely
PIPELINE_TIMEOUT_SECONDS = int(os.getenv("PIPELINE_TIMEOUT_SECONDS", "90"))


@router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["Pipeline & Prediction"],
    dependencies=[Depends(verify_api_key)]
)
@router.post(
    "/api/v1/predict",
    response_model=PredictResponse,
    tags=["Pipeline & Prediction"],
    dependencies=[Depends(verify_api_key)]
)
async def predict(
    files: Optional[List[UploadFile]] = File(None),
    project_id: Optional[str] = Form(None)
):
    """
    Executes the drone mapping pipeline:
    Receives drone images -> OpenCV (Stitching) -> AI (Land/Crop Analysis) -> GIS (GeoJSON / Telemetry)
    Returns structured results with explicit coordinate_space ('geographic' or 'pixel').
    """
    # 1. Validate all files before writing anything to disk (extension & size)
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
            safe_name = os.path.basename(file.filename or "uploaded_frame.png")
            file_path = os.path.join(project_dir, safe_name)
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            saved_paths.append(file_path)
    else:
        # Check if project already has uploaded files
        if os.path.exists(project_dir):
            for f in os.listdir(project_dir):
                if f.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
                    saved_paths.append(os.path.join(project_dir, f))

    # 2. Safe image decode validation: attempt to actually decode each saved file
    for file_path in saved_paths:
        filename = os.path.basename(file_path)
        try:
            with Image.open(file_path) as img:
                img.verify()
            # Verify stream integrity and dimensions
            with Image.open(file_path) as img:
                if img.width <= 0 or img.height <= 0:
                    raise ValueError("Invalid image dimensions")
                img.draft(img.mode, (32, 32))
                img.load()
        except Exception:
            # Clean up partially-saved files to prevent disk pollution
            for p in saved_paths:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            raise HTTPException(
                status_code=422,
                detail=f"File '{filename}' is not a valid, decodable image"
            )

    # 3. Concurrency guard: cap concurrent in-flight pipeline runs to prevent worker exhaustion
    async with pipeline_concurrency_guard:
        try:
            # Run blocking CPU pipeline in worker thread with timeout protection
            res = await asyncio.wait_for(
                asyncio.to_thread(execute_pipeline, proj_id, saved_paths, OUTPUT_BASE_DIR),
                timeout=PIPELINE_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail=f"Pipeline exceeded {PIPELINE_TIMEOUT_SECONDS}s — try a smaller image set"
            )
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
