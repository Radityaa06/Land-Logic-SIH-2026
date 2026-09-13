"""
OpenCV Orthomosaic Stitcher Engine
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
Branch: feature/opencv

Coordinates raw drone frame validation, EXIF-orientation handling,
CLAHE exposure normalization, SIFT feature matching, homography
registration, and global orthomosaic composite creation.
"""

import os
from typing import List, Optional
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from opencv.preprocess import load_and_preprocess_image
from opencv.features import FeatureExtractor
from opencv.matching import FeatureMatcher


class DroneStitcher:
    """
    Primary orthomosaic stitching engine for aerial drone image sets.
    """
    def __init__(
        self,
        detector_type: str = "SIFT",
        blend_mode: str = "MULTIBAND",
        downscale_factor: float = 1.0
    ):
        self.detector_type = (detector_type or "SIFT").upper()
        self.blend_mode = (blend_mode or "MULTIBAND").upper()
        self.downscale_factor = float(downscale_factor) if downscale_factor else 1.0
        self.extractor = FeatureExtractor(detector_type=self.detector_type)
        self.matcher = FeatureMatcher(detector_type=self.detector_type)

    def stitch_image_list(self, image_paths: List[str], output_path: str) -> str:
        """
        Stitches an array of overlapping aerial image frames into a composite orthomosaic.
        Raises catchable ValueError or RuntimeError on failures for API error propagation.
        """
        if not image_paths or len(image_paths) == 0:
            raise ValueError("Stitching requires at least 2 image frames. Received an empty image set.")

        if len(image_paths) == 1:
            raise ValueError(
                f"Stitching requires at least 2 image frames to construct a mosaic. "
                f"Received only 1 image: '{image_paths[0]}'. Cannot stitch a single frame."
            )

        print(f"[OpenCV] Received {len(image_paths)} images for stitching.")
        images = []
        for p in image_paths:
            try:
                img = load_and_preprocess_image(p)
                if self.downscale_factor < 1.0 and cv2 is not None:
                    # Apply downscaling if requested by StitchRequest to reduce memory footprint
                    new_w = max(1, int(img.shape[1] * self.downscale_factor))
                    new_h = max(1, int(img.shape[0] * self.downscale_factor))
                    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                images.append(img)
            except Exception as e:
                raise ValueError(f"Failed to process image '{p}' for stitching: {str(e)}")

        if len(images) < 2:
            raise ValueError(
                f"Stitching requires at least 2 valid image frames. "
                f"Only {len(images)} valid images could be loaded from {len(image_paths)} inputs."
            )

        if cv2 is None:
            raise RuntimeError("OpenCV (cv2) is not installed. Cannot perform feature matching and stitching.")

        print(f"[OpenCV] Initializing OpenCV Stitcher pipeline (detector: {self.detector_type})...")
        # Stitcher_SCANS is optimized for planar aerial/satellite ortho imagery
        stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)

        # Configure feature detector to match StitchRequest (default: SIFT)
        if self.detector_type == "SIFT" and hasattr(cv2, "SIFT_create"):
            try:
                stitcher.setFeaturesFinder(cv2.SIFT_create())
            except (AttributeError, cv2.error):
                pass
        elif self.detector_type == "ORB" and hasattr(cv2, "ORB_create"):
            try:
                stitcher.setFeaturesFinder(cv2.ORB_create())
            except (AttributeError, cv2.error):
                pass

        status, composite = stitcher.stitch(images)
        if status != cv2.Stitcher_OK:
            status_messages = {
                1: "Insufficient visual feature overlap between frames to estimate alignment (ERR_NEED_MORE_IMGS). Ensure flight frames have >=60% overlap.",
                2: "Homography estimation failed (ERR_HOMOGRAPHY_EST_FAIL). RANSAC could not find a consistent geometric transformation.",
                3: "Camera parameter adjustment failed (ERR_CAMERA_PARAMS_ADJUST_FAIL).",
            }
            detail = status_messages.get(status, f"OpenCV stitcher returned error code {status}.")
            raise RuntimeError(f"Orthomosaic stitching failed: {detail}")

        if composite is None or composite.size == 0:
            raise RuntimeError("Stitching produced an empty or null composite output.")

        # Ensure output directory exists and write BGR image
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        success = cv2.imwrite(output_path, composite)
        if not success or not os.path.exists(output_path):
            raise RuntimeError(f"Failed to write stitched image output to: {output_path}")

        print(f"[OpenCV] Stitched orthomosaic saved to: {output_path} (shape={composite.shape}, dtype={composite.dtype})")
        return output_path

    def process(self, image_paths: List[str], output_path: str) -> str:
        """
        Alias for pipeline orchestrator compatibility.
        """
        return self.stitch_image_list(image_paths, output_path)
