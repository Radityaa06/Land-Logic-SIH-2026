"""
Top-level AI inference pipeline runner
Member 3: AI Engineer
"""

import argparse
import os
import numpy as np
from PIL import Image
from ai.inference.segmentation import compute_vari_index, generate_dummy_land_mask


def run_inference(image_path: str, output_dir: str):
    print(f"🤖 [AI Engine] Loading input orthomosaic from: {image_path}")
    os.makedirs(output_dir, exist_ok=True)

    # In a real environment: load image and model weights
    # Here we demonstrate the full pipeline logic
    if os.path.exists(image_path):
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)
    else:
        # Generate synthetic raster for testing
        print("🤖 [AI Engine] Using synthetic 1024x1024 test array")
        img_np = np.random.randint(50, 200, (1024, 1024, 3), dtype=np.uint8)

    # 1. Compute Vegetative Health Index (VARI)
    print("🤖 [AI Engine] Computing Visible Atmospherically Resistant Index (VARI)...")
    vari_map = compute_vari_index(img_np)

    # 2. Segment Land Boundaries
    print("🤖 [AI Engine] Extracting land parcels and field classification masks...")
    mask = generate_dummy_land_mask(img_np.shape[0], img_np.shape[1])

    # 3. Save output artifacts
    mask_out_path = os.path.join(output_dir, "segmentation_mask.png")
    Image.fromarray(mask).save(mask_out_path)
    print(f"✅ [AI Engine] Segmentation mask saved to: {mask_out_path}")

    return {
        "mask_path": mask_out_path,
        "mean_vari": float(np.mean(vari_map)),
        "status": "SUCCESS"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI drone land inference")
    parser.add_argument("--input", default="../shared/sample_images/sample.jpg", help="Path to input stitched image")
    parser.add_argument("--output", default="../shared/sample_outputs/", help="Directory to save output masks")
    args = parser.parse_args()

    run_inference(args.input, args.output)
