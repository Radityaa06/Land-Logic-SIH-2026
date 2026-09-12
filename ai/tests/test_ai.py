"""
Unit tests for Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration
"""

import os
import tempfile
import unittest
import numpy as np
from PIL import Image

from ai.model import (
    LandSegmentationModel,
    LAND_CLASSES,
    CLASS_LABEL_MAP,
    get_segmentation_model,
    clear_model_cache
)
from ai.tiling import ImageTiler
from ai.postprocess import (
    compute_vari_index,
    extract_parcels_from_mask,
    generate_dummy_land_mask
)
from ai.inference import (
    run_inference,
    validate_and_load_image,
    DEFAULT_CONFIDENCE_THRESHOLD
)


class TestAIModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_image_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "shared", "sample_images", "drone_farm_ortho.png")
        )

    def setUp(self):
        clear_model_cache()
        self.test_img = np.random.randint(40, 200, (600, 600, 3), dtype=np.uint8)

    def test_land_classes_canonical(self):
        """Confirm canonical 5 project classes and labels are intact."""
        expected = [
            "agricultural_land",
            "barren_soil",
            "forests",
            "water_bodies",
            "man_made_structures"
        ]
        self.assertEqual(LAND_CLASSES, expected)
        self.assertEqual(len(CLASS_LABEL_MAP), 6)  # 0 is unclassified + 5 classes

    def test_model_singleton_caching(self):
        """Confirm model is cached once at startup and not re-instantiated per request."""
        m1 = get_segmentation_model()
        m2 = get_segmentation_model()
        self.assertIs(m1, m2, "get_segmentation_model must return identical cached instance")

        # Test force_reload produces new instance
        m3 = get_segmentation_model(force_reload=True)
        self.assertIsNot(m1, m3, "force_reload=True must instantiate a new model")

    def test_input_validation_missing_file(self):
        """Confirm missing image path raises FileNotFoundError rather than silently fabricating fake data."""
        with self.assertRaises(FileNotFoundError):
            validate_and_load_image("non_existent_file_path_xyz.png")

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(FileNotFoundError):
                run_inference("non_existent_file_path_xyz.png", tmp_dir)

    def test_input_validation_corrupt_file(self):
        """Confirm corrupt or non-image file raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"NOT_A_VALID_IMAGE_DATA")
            tmp_path = f.name

        try:
            with self.assertRaises(ValueError):
                validate_and_load_image(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_input_validation_undersized_image(self):
        """Confirm image smaller than minimum aerial threshold (16x16) is rejected."""
        tiny_img = Image.fromarray(np.zeros((8, 8, 3), dtype=np.uint8))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tiny_img.save(f.name)
            tiny_path = f.name

        try:
            with self.assertRaises(ValueError):
                validate_and_load_image(tiny_path)
        finally:
            if os.path.exists(tiny_path):
                os.remove(tiny_path)

    def test_input_validation_valid_sample_image(self):
        """Confirm real sample image decodes into expected 3-channel RGB uint8 array."""
        self.assertTrue(os.path.exists(self.sample_image_path), f"Sample image missing at {self.sample_image_path}")
        arr = validate_and_load_image(self.sample_image_path)
        self.assertEqual(arr.ndim, 3)
        self.assertEqual(arr.shape[2], 3)
        self.assertEqual(arr.dtype, np.uint8)

    def test_vari_index_numerical_stability_and_bounds(self):
        """Test Visible Atmospherically Resistant Index (VARI) formula and numerical bounds."""
        # 1. Random noise image
        vari = compute_vari_index(self.test_img)
        self.assertEqual(vari.shape, (600, 600))
        self.assertTrue(np.all(vari >= -1.0) and np.all(vari <= 1.0))
        self.assertFalse(np.any(np.isnan(vari)), "VARI map must not contain NaNs")
        self.assertFalse(np.any(np.isinf(vari)), "VARI map must not contain Infs")

        # 2. Pure vibrant green patch (vegetation): VARI should be strongly positive
        green_patch = np.zeros((50, 50, 3), dtype=np.uint8)
        green_patch[:] = [30, 180, 40]
        vari_green = compute_vari_index(green_patch)
        self.assertTrue(np.all(vari_green > 0.5), "Healthy green vegetation must have high positive VARI")

        # 3. High blue water patch: denominator edge case should not crash or produce NaN
        water_patch = np.zeros((50, 50, 3), dtype=np.uint8)
        water_patch[:] = [20, 40, 100]
        vari_water = compute_vari_index(water_patch)
        self.assertTrue(np.all(vari_water >= -1.0) and np.all(vari_water <= 1.0))
        self.assertFalse(np.any(np.isnan(vari_water)))

        # 4. Black/shadow pixels where R=G=B=0
        black_patch = np.zeros((20, 20, 3), dtype=np.uint8)
        vari_black = compute_vari_index(black_patch)
        self.assertFalse(np.any(np.isnan(vari_black)))
        self.assertFalse(np.any(np.isinf(vari_black)))

    def test_tiling_no_duplicate_slices_and_complete_coverage(self):
        """Verify ImageTiler guarantees complete pixel coverage without yielding duplicate edge tiles."""
        test_dimensions = [(512, 512), (600, 600), (700, 900), (250, 300)]
        for h, w in test_dimensions:
            canvas = np.zeros((h, w, 3), dtype=np.uint8)
            tiler = ImageTiler(tile_size=256, overlap=32)

            visited_coords = []
            visited_pixels = np.zeros((h, w), dtype=np.int32)

            for y, x, th, tw, chip in tiler.generate_tiles(canvas):
                coord = (y, x, th, tw)
                self.assertNotIn(
                    coord, visited_coords,
                    f"Duplicate window slice emitted for shape {(h, w)}: {coord}"
                )
                visited_coords.append(coord)
                visited_pixels[y:y+th, x:x+tw] += 1

            # Assert 100% pixel coverage
            self.assertTrue(
                np.all(visited_pixels >= 1),
                f"Missed pixels detected in sliding window for shape {(h, w)}"
            )

    def test_tiling_and_assembly_overlap_protection(self):
        """Verify mask assembly reconstructs valid dimensions with center-prioritized merge."""
        tiler = ImageTiler(tile_size=256, overlap=32)
        tiles = list(tiler.generate_tiles(self.test_img))
        self.assertGreater(len(tiles), 0)

        predicted_tiles = [(y, x, np.ones((th, tw), dtype=np.uint8) * 2) for y, x, th, tw, chip in tiles]
        assembled = tiler.assemble_mask((600, 600), predicted_tiles)
        self.assertEqual(assembled.shape, (600, 600))
        self.assertTrue(np.all(assembled == 2))

    def test_connected_components_multi_parcel(self):
        """Confirm spatially distinct fields of the same class produce separate parcels."""
        mask = np.zeros((400, 400), dtype=np.uint8)
        # Field 1: agricultural_land (class 1)
        mask[20:100, 20:100] = 1
        # Field 2: agricultural_land (class 1), disconnected from Field 1
        mask[200:280, 200:280] = 1

        vari_map = np.full((400, 400), 0.5, dtype=np.float32)
        parcels = extract_parcels_from_mask(mask, vari_map=vari_map, min_area_pixels=50)

        agri_parcels = [p for p in parcels if p["class"] == "agricultural_land"]
        self.assertEqual(
            len(agri_parcels), 2,
            "Connected-component labeling must separate disconnected fields into distinct parcels"
        )
        self.assertNotEqual(agri_parcels[0]["pixel_bbox"], agri_parcels[1]["pixel_bbox"])

    def test_confidence_threshold_filtering(self):
        """Verify confidence threshold constant and filtering behavior."""
        self.assertEqual(DEFAULT_CONFIDENCE_THRESHOLD, 0.50)

        with tempfile.TemporaryDirectory() as tmp_dir:
            res_default = run_inference(self.sample_image_path, tmp_dir, confidence_threshold=0.50)
            self.assertGreater(len(res_default["predictions"]), 0)

            # Strict threshold of 0.99 should filter out lower-confidence heuristic parcels
            res_strict = run_inference(self.sample_image_path, tmp_dir, confidence_threshold=0.99)
            self.assertLessEqual(len(res_strict["predictions"]), len(res_default["predictions"]))

    def test_full_inference_pipeline_contract(self):
        """Verify the full inference pipeline output conforms exactly to Member 2 and Member 5 contract."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = run_inference(self.sample_image_path, tmp_dir)

            # Member 2 contract requirements
            self.assertEqual(res["status"], "SUCCESS")
            self.assertIn("mask_path", res)
            self.assertTrue(os.path.exists(res["mask_path"]))
            self.assertIn("mean_vari", res)
            self.assertIsInstance(res["mean_vari"], float)
            self.assertTrue(-1.0 <= res["mean_vari"] <= 1.0)
            self.assertIn("raster_shape", res)
            self.assertEqual(res["raster_shape"], [640, 640])

            # Predictions array contract for Member 5 (GIS)
            self.assertIn("predictions", res)
            predictions = res["predictions"]
            self.assertGreater(len(predictions), 0)

            for p in predictions:
                self.assertIn("parcel_id", p)
                self.assertIn("class", p)
                self.assertIn(p["class"], LAND_CLASSES, f"Invented class detected: {p['class']}")
                self.assertIn("confidence", p)
                self.assertGreaterEqual(p["confidence"], DEFAULT_CONFIDENCE_THRESHOLD)
                self.assertIn("pixel_bbox", p)
                self.assertEqual(len(p["pixel_bbox"]), 4)
                self.assertIn("pixel_area", p)
                self.assertGreater(p["pixel_area"], 0)
                self.assertIn("mean_vari", p)
                self.assertTrue(-1.0 <= p["mean_vari"] <= 1.0)


if __name__ == "__main__":
    unittest.main()

