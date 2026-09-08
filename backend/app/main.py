"""
Land Logic DRONE-MAPPING-AI — FastAPI Application Entrypoint
Member 2: Backend Orchestrator
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import projects, upload, pipeline

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
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(upload.router, prefix="/api/v1/projects", tags=["Upload"])
app.include_router(pipeline.router, prefix="/api/v1", tags=["Pipeline & Jobs"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "Land Logic Drone API Gateway"}
