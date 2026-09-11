"""
Drone image preprocessing: color balance, vignetting, and contrast correction
Member 4: Computer Vision / OpenCV Engineer
(Maintained for backward compatibility; delegates to opencv.preprocess)
"""

from opencv.preprocess import balance_exposure, check_image_quality, normalize_image

__all__ = ["balance_exposure", "check_image_quality", "normalize_image"]
