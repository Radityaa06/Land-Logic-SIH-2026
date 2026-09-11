"""
Central Pipeline Coordinator Service
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Coordinates the end-to-end processing pipeline:
Raw Images -> OpenCV Stitching -> AI Segmentation -> GIS Georeferencing -> Response Payload.
Does NOT perform AI, OpenCV, or GIS math internally; acts purely as the coordinator.
Emits real-time stage-transition events for live progress streaming via SSE.
"""

import os
import sys
import time
import uuid
from typing import Dict, Any, List

# Ensure project root is on sys.path for cross-module orchestration
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from opencv.stitching import DroneStitcher
from ai.inference import run_inference
from gis.exif import extract_gps_coordinates
from gis.gsd import calculate_gsd
from gis.geojson import generate_parcels_geojson
from app.services.errors import PipelineStageError
from app.services.orchestrator import emit_stage_event
from app.utils.logger import logger, log_request


def execute_pipeline(
    project_id: str,
    image_paths: List[str],
    outputs_base_dir: str
) -> Dict[str, Any]:
    """
    Executes the modular pipeline across Members 4, 3, and 5:
    1. OpenCV: Stitches input frames into composite orthomosaic
    2. GIS: Checks genuine EXIF GPS coordinates (no fake coords)
    3. AI: Runs segmentation & VARI spectral vegetation index
    4. GIS: Formats parcels into RFC 7946 GeoJSON with coordinate_space
    Emits real-time stage transition events for frontend SSE listeners.
    """
    request_id = str(uuid.uuid4())
    project_output_dir = os.path.join(outputs_base_dir, project_id)
    os.makedirs(project_output_dir, exist_ok=True)

    stitched_img_path = os.path.join(project_output_dir, "stitched_orthomosaic.png")
    geojson_out_path = os.path.join(project_output_dir, "parcels.geojson")

    # Step 1: Member 4 — OpenCV Orthomosaic Stitching
    emit_stage_event(project_id, "stitching", "started", f"OpenCV: Stitching {len(image_paths)} flight frames into composite orthomosaic")
    logger.info(f"Invoking Member 4 (OpenCV) on {len(image_paths)} images...")
    t0 = time.perf_counter()
    try:
        stitcher = DroneStitcher()
        stitcher.stitch_image_list(image_paths, stitched_img_path)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "stitching", duration_ms, "success")
        emit_stage_event(project_id, "stitching", "done", "OpenCV: Orthomosaic stitched successfully")
    except Exception as e:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "stitching", duration_ms, "failure")
        emit_stage_event(project_id, "stitching", "error", f"OpenCV stitching failed: {str(e)}")
        raise PipelineStageError("stitching", str(e))

    # Step 2: Member 5 — GIS EXIF Extraction
    emit_stage_event(project_id, "gps_extraction", "started", "GIS: Extracting genuine EXIF GPS telemetry")
    logger.info("Invoking Member 5 (GIS) for EXIF telemetry...")
    t0 = time.perf_counter()
    try:
        gps_meta = {"has_gps": False, "coordinate_space": "pixel"}
        for p in image_paths:
            meta = extract_gps_coordinates(p)
            if meta.get("has_gps"):
                gps_meta = meta
                break
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "GPS extraction", duration_ms, "success")
        emit_stage_event(project_id, "gps_extraction", "done", f"GIS: Telemetry parsed (coordinate space: {gps_meta.get('coordinate_space', 'pixel')})")
    except Exception as e:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "GPS extraction", duration_ms, "failure")
        emit_stage_event(project_id, "gps_extraction", "error", f"GIS telemetry extraction failed: {str(e)}")
        raise PipelineStageError("GPS extraction", str(e))

    # Step 3: Member 3 — AI Inference & Spectral Analysis
    emit_stage_event(project_id, "inference", "started", "AI: Running 512x512 tile inference & VARI spectral analysis")
    logger.info("Invoking Member 3 (AI) on stitched composite...")
    t0 = time.perf_counter()
    try:
        ai_results = run_inference(stitched_img_path, project_output_dir)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "inference", duration_ms, "success")
        emit_stage_event(project_id, "inference", "done", f"AI: Detected {len(ai_results.get('predictions', []))} parcels")
    except Exception as e:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "inference", duration_ms, "failure")
        emit_stage_event(project_id, "inference", "error", f"AI inference failed: {str(e)}")
        raise PipelineStageError("inference", str(e))

    # Step 4: Member 5 — GIS GeoJSON Polygon Generation
    emit_stage_event(project_id, "geojson", "started", "GIS: Generating RFC 7946 GeoJSON parcels")
    logger.info("Invoking Member 5 (GIS) to generate GeoJSON...")
    t0 = time.perf_counter()
    try:
        geo_reference = None
        if gps_meta.get("has_gps") and gps_meta.get("coordinate_space") == "geographic":
            altitude = gps_meta.get("altitude_m", 120.0)
            gsd_info = calculate_gsd(flight_height_m=altitude)
            geo_reference = {
                "coordinate_space": "geographic",
                "latitude": gps_meta["latitude"],
                "longitude": gps_meta["longitude"],
                "gsd_cm": gsd_info["gsd_cm_per_px"]
            }

        geojson_doc = generate_parcels_geojson(
            parcels=ai_results.get("predictions", []),
            output_path=geojson_out_path,
            geo_reference=geo_reference
        )
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "GeoJSON generation", duration_ms, "success")
        emit_stage_event(project_id, "geojson", "done", "GIS: GeoJSON generated successfully")
    except Exception as e:
        duration_ms = (time.perf_counter() - t0) * 1000.0
        log_request(request_id, "GeoJSON generation", duration_ms, "failure")
        emit_stage_event(project_id, "geojson", "error", f"GIS GeoJSON generation failed: {str(e)}")
        raise PipelineStageError("GeoJSON generation", str(e))

    detected_classes = list({p["class"] for p in ai_results.get("predictions", [])})

    emit_stage_event(project_id, "complete", "done", "Pipeline execution complete across OpenCV, AI, and GIS engines")

    return {
        "status": "success",
        "message": "Pipeline completed successfully across OpenCV, AI, and GIS engines",
        "project_id": project_id,
        "coordinate_space": geojson_doc.get("coordinate_space", "pixel"),
        "summary": {
            "image_count": len(image_paths),
            "mean_vari": ai_results.get("mean_vari", 0.0),
            "detected_parcels": len(ai_results.get("predictions", [])),
            "classes_detected": detected_classes
        },
        "geojson": geojson_doc,
        "artifacts": {
            "stitched_image_path": stitched_img_path,
            "mask_path": ai_results.get("mask_path", ""),
            "geojson_path": geojson_out_path
        }
    }
