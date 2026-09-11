"""
Top-level AI Inference Pipeline
Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration

Runs sliding-window segmentation, vegetative index mapping, and formats structured
parcel predictions for downstream GIS vectorization by Member 5.
"""

import os
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image

from ai.model import LandSegmentationModel, LAND_CLASSES
from ai.tiling import ImageTiler
from ai.postprocess import compute_vari_index, extract_parcels_from_mask, generate_dummy_land_mask


def run_inference(
    image_path: str,
    output_dir: str,
    tile_size: int = 512,
    confidence_threshold: float = 0.50,
    checkpoint_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the complete AI land-use and vegetative health inference pipeline.
    Preserves and extends the interface from the existing codebase.
    """
    print(f"🤖 [AI Engine] Loading input orthomosaic from: {image_path}")
    os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(image_path):
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)
    else:
        print("🤖 [AI Engine] Image path not found on disk. Generating 1024x1024 test array.")
        img_np = np.random.randint(50, 200, (1024, 1024, 3), dtype=np.uint8)

    h, w = img_np.shape[:2]

    # 1. Compute Vegetative Health Index (VARI)
    print("🤖 [AI Engine] Computing Visible Atmospherically Resistant Index (VARI)...")
    vari_map = compute_vari_index(img_np)
    mean_vari = float(np.mean(vari_map))

    # 2. Sliding Window Inference
    print(f"🤖 [AI Engine] Running sliding-window inference ({tile_size}x{tile_size})...")
    model = LandSegmentationModel(checkpoint_path=checkpoint_path)
    tiler = ImageTiler(tile_size=tile_size, overlap=64)

    predicted_tiles = []
    for y, x, th, tw, chip in tiler.generate_tiles(img_np):
        chip_mask = model.predict_chip(chip)
        predicted_tiles.append((y, x, chip_mask))

    full_mask = tiler.assemble_mask((h, w), predicted_tiles)

    # 3. Extract structured parcel predictions
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
