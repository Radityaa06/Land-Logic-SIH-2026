"""
OpenCV Feature Matching & Homography
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
Branch: feature/opencv

Provides pairwise feature matching, Lowe's ratio test, and RANSAC homography calculation.
"""

from typing import Tuple, Optional, List, Any
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


class FeatureMatcher:
    """
    Performs robust pairwise descriptor matching and homography matrix estimation.
    """
    def __init__(self, detector_type: str = "SIFT", ratio_thresh: float = 0.75):
        self.detector_type = detector_type.upper()
        self.ratio_thresh = ratio_thresh

        if cv2 is not None:
            if self.detector_type == "SIFT":
                self.matcher = cv2.BFMatcher(cv2.NORM_L2)
            else:
                self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            self.matcher = None

    def match_features(self, desc1: np.ndarray, desc2: np.ndarray) -> List[Any]:
        """
        Applies k-Nearest Neighbors (k=2) matching and filters with Lowe's ratio test.
        """
        if self.matcher is None or desc1 is None or desc2 is None or len(desc1) < 2 or len(desc2) < 2:
            return []

        raw_matches = self.matcher.knnMatch(desc1, desc2, k=2)
        good_matches = []
        for pair in raw_matches:
            if len(pair) == 2:
                m, n = pair
                if m.distance < self.ratio_thresh * n.distance:
                    good_matches.append(m)
        return good_matches

    def estimate_homography(
        self,
        kp1: List[Any],
        kp2: List[Any],
        matches: List[Any],
        ransac_reproj_thresh: float = 4.0
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Computes the 3x3 homography matrix between two image planes using RANSAC.
        Returns: (homography_matrix, inliers_mask)
        """
        if cv2 is None or len(matches) < 4:
            return None, None

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_reproj_thresh)
        return H, mask
