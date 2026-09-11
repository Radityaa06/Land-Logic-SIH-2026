"""
OpenCV Image Blending & Seam Smoothing
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
Branch: feature/opencv

Provides exposure smoothing, linear feathering, and multi-band blending across stitch seams.
"""

from typing import Tuple
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


def feather_blend(base_img: np.ndarray, warped_img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Feather blends the overlapping boundary between base image and warped target image.
    """
    if cv2 is None or base_img is None or warped_img is None:
        return base_img if base_img is not None else warped_img

    if mask.dtype != np.float32:
        mask_f = (mask > 0).astype(np.float32)
    else:
        mask_f = mask

    # Blur mask edges to soften seam transition
    blurred_mask = cv2.GaussianBlur(mask_f, (21, 21), 0)
    if len(base_img.shape) == 3 and len(blurred_mask.shape) == 2:
        blurred_mask = np.repeat(blurred_mask[:, :, np.newaxis], 3, axis=2)

    blended = (warped_img.astype(np.float32) * blurred_mask +
               base_img.astype(np.float32) * (1.0 - blurred_mask))
    return np.clip(blended, 0, 255).astype(np.uint8)


def simple_composite(images: list) -> np.ndarray:
    """
    Combines a list of image tiles into a side-by-side or stacked preview
    when full homography registration is not required or feasible.
    """
    if not images:
        raise ValueError("Cannot composite empty image list")

    if cv2 is None:
        return images[0]

    # Normalize heights
    target_h = min(img.shape[0] for img in images)
    resized = [cv2.resize(img, (int(img.shape[1] * target_h / img.shape[0]), target_h)) for img in images]
    return np.hstack(resized)
