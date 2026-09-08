"""
Project management routes
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ProjectCreate, ProjectResponse
from datetime import datetime
import uuid

router = APIRouter()

# In-memory session store for hackathon sprint
PROJECTS_DB = {}


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate):
    proj_id = f"proj_{uuid.uuid4().hex[:8]}"
    project = {
        "project_id": proj_id,
        "name": payload.name,
        "description": payload.description,
        "status": "CREATED",
        "created_at": datetime.utcnow(),
        "image_count": 0,
        "metrics": None
    }
    PROJECTS_DB[proj_id] = project
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    return PROJECTS_DB[project_id]
