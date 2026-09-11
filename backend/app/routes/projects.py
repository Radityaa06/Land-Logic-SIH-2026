"""
Project management routes
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""

from typing import List
from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, Depends

from app.models.schemas import ProjectCreate, ProjectResponse
from app.utils.auth import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])

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


@router.get("", response_model=List[ProjectResponse])
async def list_projects():
    return list(PROJECTS_DB.values())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    return PROJECTS_DB[project_id]
