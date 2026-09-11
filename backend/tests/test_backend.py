"""
Unit tests for Member 2: Backend Orchestration & Pipeline Service
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.models.schemas import ProjectCreate, PredictResponse
from app.services.pipeline import execute_pipeline


class TestBackendModule(unittest.TestCase):
    def test_pipeline_execution(self):
        outputs_dir = "backend/outputs/test_run"
        res = execute_pipeline(
            project_id="test_run",
            image_paths=[],
            outputs_base_dir="backend/outputs"
        )
        self.assertEqual(res["status"], "success")
        self.assertIn(res["coordinate_space"], ["geographic", "pixel"])
        self.assertIn("summary", res)
        self.assertIn("geojson", res)
        self.assertEqual(res["geojson"]["type"], "FeatureCollection")
        self.assertTrue(os.path.exists(res["artifacts"]["stitched_image_path"]))
        self.assertTrue(os.path.exists(res["artifacts"]["geojson_path"]))

        # Cleanup
        for path_key in ("stitched_image_path", "mask_path", "geojson_path"):
            p = res["artifacts"].get(path_key)
            if p and os.path.exists(p):
                os.remove(p)
        if os.path.exists(outputs_dir):
            os.rmdir(outputs_dir)


if __name__ == "__main__":
    unittest.main()
