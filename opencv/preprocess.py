"""
OpenCV Image Preprocessing
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
Branch: feature/opencv

Provides CLAHE exposure normalization, contrast adjustment, and image quality verification.
"""

import os
from typing import Tuple, Optional
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


def balance_exposure(image: np.ndarray) -> np.ndarray:
    """
    Applies CLAHE (Contrast Limited Adaptive Histogram Equalization)
    to normalize lighting variations across adjacent drone flight paths.
    """
    if cv2 is None:
        # Pure numpy fallback if cv2 not installed
        return image.copy()

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    merged = cv2.merge((cl, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def check_image_quality(image: np.ndarray) -> Tuple[bool, float, str]:
    """
    Audits input image for blurriness (via Laplacian variance) and brightness issues.
    Returns: (is_acceptable, blur_score, message)
    """
    if cv2 is None:
        return True, 100.0, "OpenCV not present; quality check bypassed."

    if image is None or image.size == 0:
        return False, 0.0, "Empty or unreadable image frame"

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_brightness = float(np.mean(gray))

    if laplacian_var < 20.0:
        return False, laplacian_var, f"Image blurred (Laplacian variance {laplacian_var:.1f} < 20.0)"
    if mean_brightness < 20.0:
        return False, laplacian_var, f"Image underexposed (mean brightness {mean_brightness:.1f})"
    if mean_brightness > 245.0:
        return False, laplacian_var, f"Image overexposed (mean brightness {mean_brightness:.1f})"

    return True, laplacian_var, "Quality acceptable"


def normalize_image(image: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
    """
    Resizes and normalizes drone frame contrast for feature extraction.
    """
    if image is None:
        raise ValueError("Cannot normalize None image")

    balanced = balance_exposure(image)
    if target_size is not None and cv2 is not None:
        balanced = cv2.resize(balanced, target_size, interpolation=cv2.INTER_AREA)
    return balanced
