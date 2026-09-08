"""
Pipeline execution & job polling routes
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.schemas import StitchRequest, AIAnalyzeRequest, JobStatusResponse
from app.services.orchestrator import run_full_pipeline
from datetime import datetime
import uuid

router = APIRouter()

JOBS_DB = {}


@router.post("/projects/{project_id}/pipeline/stitch", status_code=202)
async def trigger_stitching(project_id: str, payload: StitchRequest, background_tasks: BackgroundTasks):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job_record = {
        "job_id": job_id,
        "project_id": project_id,
        "stage": "STITCHING",
        "status": "QUEUED",
        "progress_pct": 0.0,
        "message": "Stitching job queued",
        "updated_at": datetime.utcnow()
    }
    JOBS_DB[job_id] = job_record

    # Dispatch background orchestration task
    background_tasks.add_task(run_full_pipeline, project_id, job_id, JOBS_DB)

    return job_record


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    if job_id not in JOBS_DB:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS_DB[job_id]


@router.get("/projects/{project_id}/layers/parcels.geojson")
async def get_parcels_geojson(project_id: str):
    """
    Returns detected land parcels in RFC 7946 GeoJSON format
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-122.4194, 37.7749],
                            [-122.4174, 37.7749],
                            [-122.4174, 37.7735],
                            [-122.4194, 37.7735],
                            [-122.4194, 37.7749]
                        ]
                    ]
                },
                "properties": {
                    "id": "parcel_alpha",
                    "class": "healthy_crop",
                    "area_hectares": 3.42,
                    "mean_ndvi": 0.76,
                    "soil_moisture": "OPTIMAL"
                }
            }
        ]
    }
