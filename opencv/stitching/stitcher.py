"""
OpenCV Orthomosaic Stitcher
Member 4: Computer Vision / OpenCV Engineer
(Maintained for backward compatibility; delegates to opencv.stitching)
"""

import argparse
import os
from opencv.stitching import DroneStitcher

__all__ = ["DroneStitcher"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../shared/sample_images/")
    parser.add_argument("--output", default="../shared/sample_outputs/stitched_ortho.png")
    args = parser.parse_args()

    files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith(('.jpg', '.png'))] if os.path.exists(args.input) else []
    stitcher = DroneStitcher()
    stitcher.stitch_image_list(files, args.output)
