"""
Land Logic DRONE-MAPPING-AI — FastAPI Application Entrypoint
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routes import projects, upload, pipeline, predict

app = FastAPI(
    title="Land Logic DRONE-MAPPING-AI API",
    description="Backend orchestration gateway for drone image stitching, AI land segmentation, and GIS georeferencing.",
    version="1.0.0"
)

# Enable CORS for Member 1's Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(predict.router)  # Handles /predict and /api/v1/predict
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(upload.router, prefix="/api/v1/projects", tags=["Upload"])
app.include_router(pipeline.router, prefix="/api/v1", tags=["Pipeline & Jobs"])

OUTPUT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))


@app.get("/api/v1/projects/{project_id}/artifacts/{filename}", tags=["Artifacts"])
async def get_artifact_file(project_id: str, filename: str):
    """
    Streams generated stitched images, AI masks, or GeoTIFFs.
    """
    safe_filename = os.path.basename(filename)
    target_path = os.path.join(OUTPUT_BASE_DIR, project_id, safe_filename)
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Artifact {safe_filename} not found")

    media_type = "image/png"
    if safe_filename.endswith(".geojson"):
        media_type = "application/geo+json"
    elif safe_filename.endswith((".tif", ".tiff")):
        media_type = "image/tiff"

    return FileResponse(target_path, media_type=media_type)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "Land Logic Drone API Gateway",
        "team_structure": "6-member architecture",
        "orchestration": ["OpenCV", "AI", "GIS"]
    }
