"""
Unit tests for Member 3: AI / Land Vision Engine
"""

import os
import unittest
import numpy as np

from ai.model import LandSegmentationModel, LAND_CLASSES
from ai.tiling import ImageTiler
from ai.postprocess import compute_vari_index, extract_parcels_from_mask, generate_dummy_land_mask
from ai.inference import run_inference


class TestAIModule(unittest.TestCase):
    def setUp(self):
        self.test_img = np.random.randint(40, 200, (600, 600, 3), dtype=np.uint8)

    def test_land_classes_intact(self):
        expected = [
            "agricultural_land",
            "barren_soil",
            "forests",
            "water_bodies",
            "man_made_structures"
        ]
        self.assertEqual(LAND_CLASSES, expected)

    def test_vari_index(self):
        vari = compute_vari_index(self.test_img)
        self.assertEqual(vari.shape, (600, 600))
        self.assertTrue(np.all(vari >= -1.0) and np.all(vari <= 1.0))

    def test_tiling_and_assembly(self):
        tiler = ImageTiler(tile_size=256, overlap=32)
        tiles = list(tiler.generate_tiles(self.test_img))
        self.assertGreater(len(tiles), 0)

        predicted_tiles = [(y, x, np.ones((th, tw), dtype=np.uint8)) for y, x, th, tw, chip in tiles]
        assembled = tiler.assemble_mask((600, 600), predicted_tiles)
        self.assertEqual(assembled.shape, (600, 600))

    def test_full_inference_pipeline(self):
        out_dir = "ai/tests/temp_out"
        res = run_inference("non_existent.png", out_dir)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("predictions", res)
        self.assertIn("mean_vari", res)
        self.assertTrue(os.path.exists(res["mask_path"]))

        # Cleanup
        if os.path.exists(res["mask_path"]):
            os.remove(res["mask_path"])
        if os.path.exists(out_dir):
            os.rmdir(out_dir)


if __name__ == "__main__":
    unittest.main()
