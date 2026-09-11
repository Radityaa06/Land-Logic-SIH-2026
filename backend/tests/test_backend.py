"""
Unit tests for Member 2: Backend Orchestration & Pipeline Service
"""

import os
import sys
import io
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.main import app
from app.models.schemas import ProjectCreate, PredictResponse
from app.services.pipeline import execute_pipeline
from app.services.errors import PipelineStageError


class TestBackendModule(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

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

    def test_predict_invalid_extension(self):
        file_content = b"dummy text content"
        files = [("files", ("test.txt", io.BytesIO(file_content), "text/plain"))]
        response = self.client.post("/predict", files=files)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Unsupported file format", response.json()["detail"])

    def test_predict_oversized_file(self):
        # Create an oversized payload > 15MB
        oversized = b"0" * (15 * 1024 * 1024 + 1024)
        files = [("files", ("large_flight.png", io.BytesIO(oversized), "image/png"))]
        response = self.client.post("/predict", files=files)
        self.assertEqual(response.status_code, 422)
        self.assertIn("exceeds 15MB limit", response.json()["detail"])

    def test_predict_valid_small_image(self):
        # Small 10x10 PNG header/content
        dummy_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = [("files", ("drone_sample.png", io.BytesIO(dummy_png), "image/png"))]
        response = self.client.post("/predict", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("coordinate_space", data)
        self.assertIn("summary", data)
        self.assertIn("geojson", data)
        self.assertIn("artifacts", data)


if __name__ == "__main__":
    unittest.main()
