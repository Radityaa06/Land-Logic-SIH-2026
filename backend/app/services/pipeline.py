"""
Central Pipeline Coordinator Service
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Coordinates the end-to-end processing pipeline:
Raw Images -> OpenCV Stitching -> AI Segmentation -> GIS Georeferencing -> Response Payload.
Does NOT perform AI, OpenCV, or GIS math internally; acts purely as the coordinator.
"""

import os
import sys
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
    """
    project_output_dir = os.path.join(outputs_base_dir, project_id)
    os.makedirs(project_output_dir, exist_ok=True)

    stitched_img_path = os.path.join(project_output_dir, "stitched_orthomosaic.png")
    geojson_out_path = os.path.join(project_output_dir, "parcels.geojson")

    # Step 1: Member 4 — OpenCV Orthomosaic Stitching
    print(f"⚙️ [Backend Orchestrator] Invoking Member 4 (OpenCV) on {len(image_paths)} images...")
    try:
        stitcher = DroneStitcher()
        stitcher.stitch_image_list(image_paths, stitched_img_path)
    except Exception as e:
        raise PipelineStageError("stitching", str(e))

    # Step 2: Member 5 — GIS EXIF Extraction
    print("⚙️ [Backend Orchestrator] Invoking Member 5 (GIS) for EXIF telemetry...")
    try:
        gps_meta = {"has_gps": False, "coordinate_space": "pixel"}
        for p in image_paths:
            meta = extract_gps_coordinates(p)
            if meta.get("has_gps"):
                gps_meta = meta
                break
    except Exception as e:
        raise PipelineStageError("GPS extraction", str(e))

    # Step 3: Member 3 — AI Inference & Spectral Analysis
    print("⚙️ [Backend Orchestrator] Invoking Member 3 (AI) on stitched composite...")
    try:
        ai_results = run_inference(stitched_img_path, project_output_dir)
    except Exception as e:
        raise PipelineStageError("inference", str(e))

    # Step 4: Member 5 — GIS GeoJSON Polygon Generation
    print("⚙️ [Backend Orchestrator] Invoking Member 5 (GIS) to generate GeoJSON...")
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
    except Exception as e:
        raise PipelineStageError("GeoJSON generation", str(e))

    detected_classes = list({p["class"] for p in ai_results.get("predictions", [])})

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
