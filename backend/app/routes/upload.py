"""
Drone image batch upload routes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import aiofiles

router = APIRouter()

UPLOAD_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")


@router.post("/{project_id}/upload")
async def upload_drone_images(project_id: str, files: List[UploadFile] = File(...)):
    project_dir = os.path.join(UPLOAD_BASE_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)

    saved_files = []
    for file in files:
        file_path = os.path.join(project_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        saved_files.append({
            "filename": file.filename,
            "size_bytes": len(content),
            "status": "SAVED"
        })

    return {
        "project_id": project_id,
        "total_uploaded": len(saved_files),
        "files": saved_files,
        "status": "READY_FOR_PROCESSING"
    }
