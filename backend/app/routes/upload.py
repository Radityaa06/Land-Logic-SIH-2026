"""
Drone image batch upload routes
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend
"""

import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import aiofiles

from gis.exif import extract_gps_coordinates
from app.utils.auth import verify_api_key
from app.utils.image_safety import validate_and_decode_image, ALLOWED_IMAGE_EXTENSIONS

router = APIRouter(dependencies=[Depends(verify_api_key)])

UPLOAD_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15MB


@router.post("/{project_id}/upload")
async def upload_drone_images(project_id: str, files: List[UploadFile] = File(...)):
    """
    Saves incoming drone frames and performs telemetry check.
    Enforces format, size, safe decode, and API key validation.
    """
    project_dir = os.path.join(UPLOAD_BASE_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)

    # Validate all files before writing to disk
    validated_files = []
    for file in files:
        safe_name = os.path.basename(file.filename or "uploaded_image")
        ext = os.path.splitext(safe_name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported file format '{ext}' in '{safe_name}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=422,
                detail=f"File '{safe_name}' exceeds 15MB limit ({len(content) / (1024 * 1024):.1f}MB)"
            )

        # Safe Image Decode verification
        validate_and_decode_image(content, safe_name)
        validated_files.append((safe_name, content))

    saved_files = []
    has_any_gps = False

    for safe_name, content in validated_files:
        file_path = os.path.join(project_dir, safe_name)
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)

        gps_info = extract_gps_coordinates(file_path)
        if gps_info.get("has_gps"):
            has_any_gps = True

        saved_files.append({
            "filename": safe_name,
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
