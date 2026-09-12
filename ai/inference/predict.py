"""
Top-level AI inference pipeline runner
Member 3: AI Engineer
(Maintained for backward compatibility; delegates to ai.inference)
"""

import os
import sys
import argparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ai.inference import run_inference
from ai.postprocess import compute_vari_index, generate_dummy_land_mask


__all__ = ["run_inference", "compute_vari_index", "generate_dummy_land_mask"]

if __name__ == "__main__":
    default_input = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "shared", "sample_images", "drone_farm_ortho.png")
    )
    default_output = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "shared", "sample_outputs")
    )

    parser = argparse.ArgumentParser(description="Run AI drone land inference")
    parser.add_argument("--input", default=default_input, help="Path to input stitched image")
    parser.add_argument("--output", default=default_output, help="Directory to save output masks")
    args = parser.parse_args()

    run_inference(args.input, args.output)

