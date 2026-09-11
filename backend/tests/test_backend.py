"""
Unit tests for Member 2: Backend Orchestration & Pipeline Service
Hardening & Security Addendum Verification:
1. /health works without an API key
2. /predict without X-API-Key header returns 401
3. /predict with correct key + renamed .txt as .jpg returns 422 with decode-failure message
4. Existing extension/size validation still runs
5. Concurrency guard returns 503 when worker is busy
"""

import os
import sys
import io
import asyncio
import unittest
from PIL import Image
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.main import app
from app.services.pipeline import execute_pipeline
from app.dependencies import pipeline_concurrency_guard


def _make_valid_png_bytes(w: int = 10, h: int = 10) -> bytes:
    """Generates structurally valid PNG image bytes."""
    buf = io.BytesIO()
    img = Image.new("RGB", (w, h), color=(46, 139, 87))
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestBackendModule(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.api_key = "test_sih_drone_key"
        os.environ["API_KEY"] = self.api_key
        self.auth_headers = {"X-API-Key": self.api_key}
        pipeline_concurrency_guard.reset()

    def tearDown(self):
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]
        pipeline_concurrency_guard.reset()

    # 1. Health check works without any API key
    def test_health_check_unauthenticated(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    # 2. /predict without X-API-Key returns 401
    def test_predict_without_api_key_returns_401(self):
        response = self.client.post("/predict")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid or missing API key", response.json()["detail"])

    def test_predict_with_wrong_api_key_returns_401(self):
        response = self.client.post("/predict", headers={"X-API-Key": "wrong_key_value"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid or missing API key", response.json()["detail"])

    def test_predict_api_key_unset_fails_closed_401(self):
        del os.environ["API_KEY"]
        response = self.client.post("/predict", headers={"X-API-Key": "any_key"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("no API_KEY configured", response.json()["detail"])

    # 3. /predict with correct key + renamed .txt file as .jpg returns 422 with decode failure
    def test_predict_renamed_txt_as_jpg_returns_422(self):
        fake_jpg_content = b"This is plain text disguised as a drone image flight frame."
        files = [("files", ("renamed_notes.jpg", io.BytesIO(fake_jpg_content), "image/jpeg"))]
        response = self.client.post("/predict", files=files, headers=self.auth_headers)
        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        self.assertEqual(detail, "File 'renamed_notes.jpg' is not a valid, decodable image")

    # 4. Existing extension and size validation still runs
    def test_predict_invalid_extension(self):
        file_content = b"sample text"
        files = [("files", ("script.sh", io.BytesIO(file_content), "text/plain"))]
        response = self.client.post("/predict", files=files, headers=self.auth_headers)
        self.assertEqual(response.status_code, 422)
        self.assertIn("Unsupported file format", response.json()["detail"])

    def test_predict_oversized_file(self):
        oversized = b"0" * (15 * 1024 * 1024 + 1024)
        files = [("files", ("huge_frame.png", io.BytesIO(oversized), "image/png"))]
        response = self.client.post("/predict", files=files, headers=self.auth_headers)
        self.assertEqual(response.status_code, 422)
        self.assertIn("exceeds 15MB limit", response.json()["detail"])

    # Valid image predict end-to-end
    def test_predict_valid_small_image(self):
        valid_png = _make_valid_png_bytes(10, 10)
        files = [("files", ("valid_drone_1.png", io.BytesIO(valid_png), "image/png"))]
        response = self.client.post("/predict", files=files, headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("coordinate_space", data)
        self.assertIn("summary", data)
        self.assertIn("geojson", data)
        self.assertIn("artifacts", data)

    # 5. Concurrency guard returns 503 when cap is reached
    def test_concurrency_guard_returns_503_when_busy(self):
        pipeline_concurrency_guard.set_limit(1)
        asyncio.run(pipeline_concurrency_guard.acquire())

        try:
            response = self.client.post("/predict", headers=self.auth_headers)
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()["detail"], "Server busy, try again in a moment")
        finally:
            asyncio.run(pipeline_concurrency_guard.release())
            pipeline_concurrency_guard.set_limit(3)

    # Core pipeline execution test
    def test_pipeline_execution_direct(self):
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
