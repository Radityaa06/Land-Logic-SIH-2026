"""
Unit tests for Member 4: OpenCV Stitching & Preprocessing
"""

import os
import unittest
import numpy as np

from opencv.preprocess import balance_exposure, check_image_quality, normalize_image
from opencv.features import FeatureExtractor
from opencv.matching import FeatureMatcher
from opencv.stitching import DroneStitcher


class TestOpenCVModule(unittest.TestCase):
    def setUp(self):
        self.dummy_img = np.random.randint(40, 220, (200, 200, 3), dtype=np.uint8)

    def test_balance_exposure(self):
        result = balance_exposure(self.dummy_img)
        self.assertEqual(result.shape, self.dummy_img.shape)

    def test_check_image_quality(self):
        is_ok, score, msg = check_image_quality(self.dummy_img)
        self.assertIsInstance(is_ok, bool)
        self.assertIsInstance(score, float)

    def test_features_extractor(self):
        extractor = FeatureExtractor(detector_type="SIFT")
        kp, desc = extractor.detect_and_compute(self.dummy_img)
        self.assertIsInstance(kp, list)

    def test_drone_stitcher_output(self):
        stitcher = DroneStitcher()
        out_path = "opencv/tests/temp_test_mosaic.png"
        res = stitcher.stitch_image_list([], out_path)
        self.assertTrue(os.path.exists(out_path))
        if os.path.exists(out_path):
            os.remove(out_path)


if __name__ == "__main__":
    unittest.main()
