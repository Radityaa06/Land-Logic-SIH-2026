"""
Land Logic DRONE-MAPPING-AI — Safe Image Decoding & Validation
Member 2: Backend & Pipeline Orchestrator
Workspace: backend/
Branch: feature/fastapi-backend

Security Addendum: Safe Image Decode
Guards against malformed payloads, corrupted image streams, zero-byte uploads,
and decompression bombs masquerading as valid drone images.
"""

import io
import os
from fastapi import HTTPException, status
from PIL import Image, UnidentifiedImageError

# Protect against decompression bomb denial of service (DoS)
MAX_PIXELS = 100_000_000  # 100 Megapixels
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".dng"}


def validate_and_decode_image(content: bytes, filename: str) -> None:
    """
    Safely inspects and decodes the image bytes before saving or processing.
    Ensures:
    1. File is non-empty.
    2. File extension is allowed.
    3. Image headers and data streams are valid and uncorrupted.
    4. Image dimensions are positive and within safe limits.
    """
    if not content or len(content) == 0:
        raise HTTPException(
            status_code=422,
            detail=f"File '{filename}' is empty (0 bytes)."
        )

    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file format '{ext}' in '{filename}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
        )

    # Handle DNG (Digital Negative / TIFF-based raw)
    if ext == ".dng":
        # DNG files are based on TIFF structure (II*\x00 for little-endian, MM\x00* for big-endian)
        if len(content) < 4 or (content[:4] != b"II*\x00" and content[:4] != b"MM\x00*"):
            raise HTTPException(
                status_code=422,
                detail=f"Corrupted or invalid DNG image header in '{filename}'."
            )
        return

    # Standard formats (.jpg, .jpeg, .png)
    try:
        buffer = io.BytesIO(content)
        with Image.open(buffer) as img:
            # 1. Verify headers
            img.verify()

        # 2. Re-open to verify image decoding integrity (verify() invalidates image object)
        buffer.seek(0)
        with Image.open(buffer) as img:
            width, height = img.size
            if width <= 0 or height <= 0:
                raise ValueError(f"Invalid image dimensions: {width}x{height}")

            # Verify image content can be decoded without syntax or buffer errors
            img.draft(img.mode, (32, 32))
            img.load()

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=422,
            detail=f"Unrecognized or corrupted image file: '{filename}'. Unable to decode image data."
        )
    except Image.DecompressionBombError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Decompression bomb detected in '{filename}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Corrupted or unreadable image file '{filename}': {str(e)}"
        )
