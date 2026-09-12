"""
Standalone CLI Runner for AI Drone Land Inference
Member 3: AI Engineer
Workspace: ai/
"""

import os
import sys
import argparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.inference import run_inference, DEFAULT_CONFIDENCE_THRESHOLD
from ai.postprocess import compute_vari_index, generate_dummy_land_mask

__all__ = ["run_inference", "compute_vari_index", "generate_dummy_land_mask"]


def main():
    default_input = os.path.abspath(
        os.path.join(REPO_ROOT, "shared", "sample_images", "drone_farm_ortho.png")
    )
    default_output = os.path.abspath(
        os.path.join(REPO_ROOT, "shared", "sample_outputs")
    )

    parser = argparse.ArgumentParser(description="Run AI drone land inference")
    parser.add_argument("--input", default=default_input, help="Path to input stitched orthomosaic")
    parser.add_argument("--output", default=default_output, help="Directory to save output masks")
    parser.add_argument("--tile-size", type=int, default=512, help="Sliding window tile size")
    parser.add_argument("--conf", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD, help="Confidence cutoff")
    args = parser.parse_args()

    res = run_inference(
        image_path=args.input,
        output_dir=args.output,
        tile_size=args.tile_size,
        confidence_threshold=args.conf
    )
    print(f"✅ [AI CLI] Completed successfully: {len(res['predictions'])} parcels detected.")


if __name__ == "__main__":
    main()
