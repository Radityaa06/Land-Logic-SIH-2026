"""
Drone image batch upload routes
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""

import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
import aiofiles

from gis.exif import extract_gps_coordinates

router = APIRouter()

UPLOAD_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))


@router.post("/{project_id}/upload")
async def upload_drone_images(project_id: str, files: List[UploadFile] = File(...)):
    """
    Saves incoming drone frames and performs telemetry check.
    """
    project_dir = os.path.join(UPLOAD_BASE_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)

    saved_files = []
    has_any_gps = False

    for file in files:
        file_path = os.path.join(project_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        gps_info = extract_gps_coordinates(file_path)
        if gps_info.get("has_gps"):
            has_any_gps = True

        saved_files.append({
            "filename": file.filename,
            "size_bytes": len(content),
            "status": "SAVED",
            "has_gps": gps_info.get("has_gps", False),
            "coordinate_space": gps_info.get("coordinate_space", "pixel")
        })

    return {
        "project_id": project_id,
        "total_uploaded": len(saved_files),
        "coordinate_space": "geographic" if has_any_gps else "pixel",
        "files": saved_files,
        "status": "READY_FOR_PROCESSING"
    }
