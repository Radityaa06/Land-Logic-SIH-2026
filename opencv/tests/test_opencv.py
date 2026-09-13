"""
Unit tests for Member 4: OpenCV Stitching & Preprocessing
Workspace: opencv/
Branch: feature/opencv
"""

import os
import unittest
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image
except ImportError:
    Image = None

from opencv.preprocess import (
    balance_exposure,
    check_image_quality,
    normalize_image,
    correct_exif_orientation,
    load_and_preprocess_image,
)
from opencv.features import FeatureExtractor
from opencv.matching import FeatureMatcher
from opencv.stitching import DroneStitcher


class TestOpenCVModule(unittest.TestCase):
    def setUp(self):
        # Create a synthetic image frame with good texture
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_fixtures")
        os.makedirs(self.test_dir, exist_ok=True)
        self.dummy_img = np.random.randint(40, 220, (200, 200, 3), dtype=np.uint8)

        # Save two sample frames
        self.frame1_path = os.path.join(self.test_dir, "frame1.png")
        self.frame2_path = os.path.join(self.test_dir, "frame2.png")
        self.corrupt_path = os.path.join(self.test_dir, "corrupt.png")

        if cv2 is not None:
            cv2.imwrite(self.frame1_path, self.dummy_img)
            cv2.imwrite(self.frame2_path, self.dummy_img)
        elif Image is not None:
            Image.fromarray(self.dummy_img).save(self.frame1_path)
            Image.fromarray(self.dummy_img).save(self.frame2_path)

        with open(self.corrupt_path, "wb") as f:
            f.write(b"NOT_A_VALID_IMAGE_CONTENT_XYZ")

    def tearDown(self):
        for p in [self.frame1_path, self.frame2_path, self.corrupt_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
        if os.path.exists(self.test_dir):
            try:
                os.rmdir(self.test_dir)
            except OSError:
                pass

    def test_balance_exposure(self):
        result = balance_exposure(self.dummy_img)
        self.assertEqual(result.shape, self.dummy_img.shape)
        self.assertEqual(result.dtype, self.dummy_img.dtype)

    def test_check_image_quality(self):
        is_ok, score, msg = check_image_quality(self.dummy_img)
        self.assertIsInstance(is_ok, bool)
        self.assertIsInstance(score, float)
        self.assertTrue(is_ok)

    def test_features_extractor_sift(self):
        extractor = FeatureExtractor(detector_type="SIFT")
        self.assertEqual(extractor.detector_type, "SIFT")
        kp, desc = extractor.detect_and_compute(self.dummy_img)
        self.assertIsInstance(kp, list)

    def test_features_extractor_orb(self):
        extractor = FeatureExtractor(detector_type="ORB")
        self.assertEqual(extractor.detector_type, "ORB")
        kp, desc = extractor.detect_and_compute(self.dummy_img)
        self.assertIsInstance(kp, list)

    def test_feature_matcher(self):
        matcher = FeatureMatcher(detector_type="SIFT")
        self.assertEqual(matcher.detector_type, "SIFT")

    def test_exif_orientation_correction(self):
        corrected = correct_exif_orientation(self.frame1_path)
        self.assertEqual(len(corrected.shape), 3)
        self.assertEqual(corrected.shape[2], 3)
        self.assertEqual(corrected.dtype, np.uint8)

    def test_load_and_preprocess_image(self):
        img = load_and_preprocess_image(self.frame1_path)
        self.assertEqual(img.shape, self.dummy_img.shape)
        self.assertEqual(img.dtype, np.uint8)

    def test_robustness_empty_input(self):
        stitcher = DroneStitcher(detector_type="SIFT")
        out_path = os.path.join(self.test_dir, "mosaic.png")
        with self.assertRaises(ValueError) as ctx:
            stitcher.stitch_image_list([], out_path)
        self.assertIn("at least 2 image frames", str(ctx.exception))

    def test_robustness_single_image(self):
        stitcher = DroneStitcher(detector_type="SIFT")
        out_path = os.path.join(self.test_dir, "mosaic.png")
        with self.assertRaises(ValueError) as ctx:
            stitcher.stitch_image_list([self.frame1_path], out_path)
        self.assertIn("Cannot stitch a single frame", str(ctx.exception))

    def test_robustness_corrupted_image(self):
        stitcher = DroneStitcher(detector_type="SIFT")
        out_path = os.path.join(self.test_dir, "mosaic.png")
        with self.assertRaises(ValueError) as ctx:
            stitcher.stitch_image_list([self.frame1_path, self.corrupt_path], out_path)
        self.assertIn("Failed to process image", str(ctx.exception))

    def test_robustness_nonexistent_file(self):
        stitcher = DroneStitcher(detector_type="SIFT")
        out_path = os.path.join(self.test_dir, "mosaic.png")
        with self.assertRaises(ValueError) as ctx:
            stitcher.stitch_image_list([self.frame1_path, "does_not_exist_99.png"], out_path)
        self.assertIn("Failed to process image", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
