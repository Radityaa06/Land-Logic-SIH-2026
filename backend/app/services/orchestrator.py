"""
Pipeline Orchestrator Service
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Coordinates asynchronous execution of Member 4 (OpenCV), Member 3 (AI), and Member 5 (GIS).
"""

import os
import asyncio
from datetime import datetime
from app.services.pipeline import execute_pipeline

UPLOAD_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))


async def run_full_pipeline(project_id: str, job_id: str, jobs_db: dict):
    """
    Executes the multi-stage pipeline:
    1. OpenCV Orthomosaic Stitching (Member 4)
    2. AI Semantic Land & Crop Health Segmentation (Member 3)
    3. GIS Georeferencing & Vector GeoJSON Generation (Member 5)
    """
    try:
        # Update stage to OpenCV
        jobs_db[job_id]["stage"] = "OPENCV_STITCHING"
        jobs_db[job_id]["status"] = "PROCESSING"
        jobs_db[job_id]["progress_pct"] = 25.0
        jobs_db[job_id]["message"] = "OpenCV: Extracting SIFT keypoints & computing homography matrices"
        jobs_db[job_id]["updated_at"] = datetime.utcnow()
        await asyncio.sleep(0.5)

        # Gather images for project
        project_dir = os.path.join(UPLOAD_BASE_DIR, project_id)
        image_paths = []
        if os.path.exists(project_dir):
            for f in os.listdir(project_dir):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".dng", ".tiff")):
                    image_paths.append(os.path.join(project_dir, f))

        jobs_db[job_id]["stage"] = "AI_SEGMENTATION"
        jobs_db[job_id]["progress_pct"] = 60.0
        jobs_db[job_id]["message"] = "AI Engine: Running 512x512 tile inference & VARI spectral analysis"
        jobs_db[job_id]["updated_at"] = datetime.utcnow()
        await asyncio.sleep(0.5)

        jobs_db[job_id]["stage"] = "GIS_GEOREFERENCING"
        jobs_db[job_id]["progress_pct"] = 85.0
        jobs_db[job_id]["message"] = "GIS: Georeferencing telemetry & generating RFC 7946 GeoJSON parcels"
        jobs_db[job_id]["updated_at"] = datetime.utcnow()

        # Execute real pipeline logic
        result = execute_pipeline(project_id, image_paths, OUTPUT_BASE_DIR)

        # Finalize
        jobs_db[job_id]["stage"] = "COMPLETE"
        jobs_db[job_id]["status"] = "COMPLETED"
        jobs_db[job_id]["progress_pct"] = 100.0
        jobs_db[job_id]["message"] = "Pipeline completed successfully. Layers ready for visualization."
        jobs_db[job_id]["updated_at"] = datetime.utcnow()
        jobs_db[job_id]["result_summary"] = result.get("summary")

    except Exception as exc:
        jobs_db[job_id]["status"] = "FAILED"
        jobs_db[job_id]["message"] = f"Pipeline execution failed: {str(exc)}"
        jobs_db[job_id]["updated_at"] = datetime.utcnow()
