"""
Top-level AI inference pipeline runner
Member 3: AI Engineer
(Maintained for backward compatibility; delegates to ai.inference)
"""

import argparse
from ai.inference import run_inference
from ai.postprocess import compute_vari_index, generate_dummy_land_mask

__all__ = ["run_inference", "compute_vari_index", "generate_dummy_land_mask"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI drone land inference")
    parser.add_argument("--input", default="../shared/sample_images/sample.jpg", help="Path to input stitched image")
    parser.add_argument("--output", default="../shared/sample_outputs/", help="Directory to save output masks")
    args = parser.parse_args()

    run_inference(args.input, args.output)
