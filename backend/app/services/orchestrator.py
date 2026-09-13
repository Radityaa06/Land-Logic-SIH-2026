"""
Pipeline Orchestrator Service
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Coordinates asynchronous execution of Member 4 (OpenCV), Member 3 (AI), and Member 5 (GIS),
and manages real-time stage-transition event pub-sub for SSE streaming.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

# In-memory store of stage transition events per project
PROJECT_EVENTS: Dict[str, List[Dict[str, Any]]] = {}
PROJECT_LISTENERS: Dict[str, List[asyncio.Queue]] = {}


def emit_stage_event(project_id: str, stage: str, status: str, message: str) -> Dict[str, Any]:
    """
    Emits a structured stage-transition event to historical log and live SSE subscribers.
    Payload contains: stage, status (started/done/error), and human-readable message.
    """
    event = {
        "project_id": project_id,
        "stage": stage,
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    if project_id not in PROJECT_EVENTS:
        PROJECT_EVENTS[project_id] = []
    PROJECT_EVENTS[project_id].append(event)

    # Dispatch to all active SSE queues for this project
    queues = PROJECT_LISTENERS.get(project_id, [])
    for q in queues:
        try:
            q.put_nowait(event)
        except Exception:
            pass

    return event


def subscribe_project_events(project_id: str) -> asyncio.Queue:
    """Registers an SSE listener queue for real-time stage transitions."""
    q = asyncio.Queue()
    if project_id not in PROJECT_LISTENERS:
        PROJECT_LISTENERS[project_id] = []
    PROJECT_LISTENERS[project_id].append(q)
    return q


def unsubscribe_project_events(project_id: str, q: asyncio.Queue) -> None:
    """Unregisters an SSE listener queue upon client disconnect."""
    if project_id in PROJECT_LISTENERS and q in PROJECT_LISTENERS[project_id]:
        PROJECT_LISTENERS[project_id].remove(q)


UPLOAD_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))


async def run_full_pipeline(project_id: str, job_id: str, jobs_db: dict, stitch_request: Optional[Any] = None):
    """
    Executes the multi-stage pipeline as an async background task:
    1. OpenCV Orthomosaic Stitching (Member 4)
    2. AI Semantic Land & Crop Health Segmentation (Member 3)
    3. GIS Georeferencing & Vector GeoJSON Generation (Member 5)
    Drives job status and SSE updates via real event callbacks — no fabricated percentages.
    """
    from app.services.pipeline import execute_pipeline

    try:
        # Gather images for project
        project_dir = os.path.join(UPLOAD_BASE_DIR, project_id)
        image_paths = []
        if os.path.exists(project_dir):
            for f in os.listdir(project_dir):
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".dng", ".tiff")):
                    image_paths.append(os.path.join(project_dir, f))

        def orchestrator_progress_callback(p_id: str, stage: str, status: str, message: str) -> None:
            emit_stage_event(p_id, stage, status, message)
            if job_id in jobs_db:
                jobs_db[job_id]["stage"] = stage.upper()
                jobs_db[job_id]["status"] = "PROCESSING" if status in ("started", "done") and stage != "complete" else ("COMPLETED" if stage == "complete" else "FAILED")
                jobs_db[job_id]["message"] = message
                jobs_db[job_id]["updated_at"] = datetime.utcnow()

        detector = getattr(stitch_request, "feature_detector", "SIFT") if stitch_request else "SIFT"
        blend = getattr(stitch_request, "blend_mode", "MULTIBAND") if stitch_request else "MULTIBAND"
        downscale = getattr(stitch_request, "downscale_factor", 1.0) if stitch_request else 1.0

        # Execute blocking pipeline in worker thread with live stage transition callback
        result = await asyncio.to_thread(
            execute_pipeline,
            project_id,
            image_paths,
            OUTPUT_BASE_DIR,
            orchestrator_progress_callback,
            detector,
            blend,
            downscale,
        )

        # Finalize on genuine completion
        detected_count = result.get("summary", {}).get("detected_parcels", 0)
        jobs_db[job_id]["stage"] = "COMPLETE"
        jobs_db[job_id]["status"] = "COMPLETED"
        jobs_db[job_id]["progress_pct"] = 100.0
        jobs_db[job_id]["message"] = f"Pipeline completed successfully: {detected_count} parcels detected"
        jobs_db[job_id]["updated_at"] = datetime.utcnow()
        jobs_db[job_id]["result_summary"] = result.get("summary")

    except Exception as exc:
        jobs_db[job_id]["status"] = "FAILED"
        jobs_db[job_id]["message"] = f"Pipeline execution failed: {str(exc)}"
        jobs_db[job_id]["updated_at"] = datetime.utcnow()
        emit_stage_event(project_id, "complete", "error", f"Pipeline execution failed: {str(exc)}")
