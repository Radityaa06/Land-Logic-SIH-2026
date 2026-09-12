"""
Standalone CLI Runner for OpenCV Orthomosaic Stitching
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
"""

import os
import sys
import argparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from opencv.stitching import DroneStitcher

__all__ = ["DroneStitcher"]


def main():
    default_input = os.path.abspath(
        os.path.join(REPO_ROOT, "shared", "sample_images")
    )
    default_output = os.path.abspath(
        os.path.join(REPO_ROOT, "shared", "sample_outputs", "stitched_ortho.png")
    )

    parser = argparse.ArgumentParser(description="Run OpenCV drone orthomosaic stitching")
    parser.add_argument("--input", default=default_input, help="Directory containing input drone image frames")
    parser.add_argument("--output", default=default_output, help="Path where stitched orthomosaic will be saved")
    parser.add_argument("--detector", default="SIFT", choices=["SIFT", "ORB"], help="Feature detector type")
    args = parser.parse_args()

    files = [
        os.path.join(args.input, f)
        for f in sorted(os.listdir(args.input))
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))
    ] if os.path.exists(args.input) and os.path.isdir(args.input) else []

    stitcher = DroneStitcher(detector_type=args.detector)
    stitcher.stitch_image_list(files, args.output)
    print(f"✅ [OpenCV CLI] Stitching process completed -> {args.output}")


if __name__ == "__main__":
    main()
