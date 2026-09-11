"""
OpenCV Feature Extraction
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
Branch: feature/opencv

Provides SIFT and ORB keypoint detection and local feature descriptor extraction.
"""

from typing import Tuple, List, Any, Optional
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


class FeatureExtractor:
    """
    Extracts keypoints and descriptors from drone imagery using SIFT or ORB.
    """
    def __init__(self, detector_type: str = "SIFT", n_features: int = 2000):
        self.detector_type = detector_type.upper()
        self.n_features = n_features
        self.detector = None

        if cv2 is not None:
            if self.detector_type == "SIFT" and hasattr(cv2, "SIFT_create"):
                self.detector = cv2.SIFT_create(nfeatures=n_features)
            elif hasattr(cv2, "ORB_create"):
                self.detector = cv2.ORB_create(nfeatures=n_features)
                self.detector_type = "ORB"

    def detect_and_compute(self, image: np.ndarray) -> Tuple[List[Any], Optional[np.ndarray]]:
        """
        Detects keypoints and extracts descriptors from an image.
        Returns: (keypoints, descriptors)
        """
        if self.detector is None or cv2 is None:
            # Fallback stub when cv2 is not installed
            return [], None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        keypoints, descriptors = self.detector.detectAndCompute(gray, None)
        return keypoints, descriptors
