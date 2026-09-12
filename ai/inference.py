"""
Top-level AI Inference Pipeline
Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration

Runs sliding-window segmentation, vegetative index mapping, and formats structured
parcel predictions for downstream GIS vectorization by Member 5 and coordination by Member 2.
"""

import os
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image

from ai.model import get_segmentation_model, LAND_CLASSES
from ai.tiling import ImageTiler
from ai.postprocess import compute_vari_index, extract_parcels_from_mask

# Grounded confidence threshold constant:
# Detections below this score are filtered to eliminate low-agreement speckles
# and boundary seam noise. Documented and exported for inter-module clarity.
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.50

# Minimum spatial resolution required for aerial sliding window analysis
MIN_IMAGE_DIMENSION: int = 16


def validate_and_load_image(image_path: str) -> np.ndarray:
    """
    Validates that the input image exists on disk, is a readable image file, and
    decodes into an RGB numpy array of uint8 dtype with valid spatial dimensions.

    Raises:
        FileNotFoundError: If image_path does not exist on disk.
        ValueError: If image cannot be decoded, is corrupt, or has invalid dimensions/channels.
    """
    if not isinstance(image_path, str) or not image_path.strip():
        raise ValueError(f"Invalid image path: '{image_path}'. Expected non-empty string.")

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Input image not found on disk: {image_path}")

    try:
        with Image.open(image_path) as pil_img:
            pil_img.verify()
    except Exception as e:
        raise ValueError(
            f"Failed to decode image at '{image_path}': corrupted or unreadable format ({e})"
        ) from e

    try:
        with Image.open(image_path) as pil_img:
            rgb_img = pil_img.convert("RGB")
            arr = np.array(rgb_img, dtype=np.uint8)
    except Exception as e:
        raise ValueError(f"Failed to convert image '{image_path}' to RGB array: {e}") from e

    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(f"Expected 3-channel RGB image, got array with shape {arr.shape}")

    h, w = arr.shape[:2]
    if h < MIN_IMAGE_DIMENSION or w < MIN_IMAGE_DIMENSION:
        raise ValueError(
            f"Image dimensions ({w}x{h}) are too small for aerial inference "
            f"(minimum {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} required)."
        )

    return arr


def run_inference(
    image_path: str,
    output_dir: str,
    tile_size: int = 512,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    checkpoint_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the complete AI land-use and vegetative health inference pipeline.
    Uses cached model instance (loaded once at startup/first call, not per request).

    Parameters:
        image_path: Path to valid RGB stitched orthomosaic image.
        output_dir: Directory where output artifacts (masks) will be written.
        tile_size: Chip size for sliding window inference (default 512).
        confidence_threshold: Minimum parcel confidence cutoff (default 0.50).
        checkpoint_path: Optional path to weights; uses cached instance if already loaded.

    Returns:
        Dictionary conforming to Member 2 and Member 5 integration contract.
    """
    print(f"🤖 [AI Engine] Loading and validating input orthomosaic from: {image_path}")
    os.makedirs(output_dir, exist_ok=True)

    img_np = validate_and_load_image(image_path)
    h, w = img_np.shape[:2]

    # 1. Compute Vegetative Health Index (VARI)
    print("🤖 [AI Engine] Computing Visible Atmospherically Resistant Index (VARI)...")
    vari_map = compute_vari_index(img_np)
    mean_vari = float(np.mean(vari_map))

    # 2. Sliding Window Inference using Cached Model (reused across requests)
    print(f"🤖 [AI Engine] Running sliding-window inference ({tile_size}x{tile_size})...")
    model = get_segmentation_model(checkpoint_path=checkpoint_path)
    overlap = min(64, max(8, tile_size // 8))
    tiler = ImageTiler(tile_size=tile_size, overlap=overlap)

    predicted_tiles = []
    for y_start, x_start, th, tw, chip in tiler.generate_tiles(img_np):
        chip_mask = model.predict_chip(chip)
        predicted_tiles.append((y_start, x_start, chip_mask))

    full_mask = tiler.assemble_mask((h, w), predicted_tiles)

    # 3. Extract structured parcel predictions with connected components
    raw_parcels = extract_parcels_from_mask(full_mask, vari_map)
    filtered_parcels = [p for p in raw_parcels if p["confidence"] >= confidence_threshold]

    # 4. Save artifacts
    mask_out_path = os.path.join(output_dir, "segmentation_mask.png")
    # Scale mask values for visual contrast if viewing as grayscale
    display_mask = (full_mask * 50).astype(np.uint8)
    Image.fromarray(display_mask).save(mask_out_path)
    print(f"✅ [AI Engine] Segmentation mask saved to: {mask_out_path}")

    return {
        "status": "SUCCESS",
        "mask_path": mask_out_path,
        "mean_vari": round(mean_vari, 3),
        "classes_supported": LAND_CLASSES,
        "predictions": filtered_parcels,
        "raster_shape": [h, w]
    }


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_sample = os.path.join(repo_root, "shared", "sample_images", "drone_farm_ortho.png")
    default_out = os.path.join(repo_root, "shared", "sample_outputs")

    print("🤖 [AI Engine] Running standalone inference on default sample dataset...")
    out = run_inference(default_sample, default_out)
    print(f"✅ [AI Engine] Output status: {out['status']} | Parcels detected: {len(out['predictions'])}")


