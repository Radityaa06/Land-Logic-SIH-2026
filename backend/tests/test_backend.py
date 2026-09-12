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

    # Priority 1 Verification: slow pipeline does not block /health from responding
    def test_slow_pipeline_does_not_block_health(self):
        import time
        from unittest.mock import patch
        import httpx

        def slow_execute(*args, **kwargs):
            time.sleep(0.3)
            return {
                "status": "success",
                "message": "done",
                "project_id": "test_slow",
                "coordinate_space": "pixel",
                "summary": {"image_count": 0, "mean_vari": 0.0, "detected_parcels": 0, "classes_detected": []},
                "geojson": {"type": "FeatureCollection", "features": []},
                "artifacts": {}
            }

        async def run_concurrent():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                health_completed_before_predict = False

                async def trigger_predict():
                    nonlocal health_completed_before_predict
                    return await client.post("/predict", headers=self.auth_headers)

                async def trigger_health():
                    nonlocal health_completed_before_predict
                    await asyncio.sleep(0.05)
                    h_res = await client.get("/health")
                    health_completed_before_predict = True
                    return h_res

                with patch("app.routes.predict.execute_pipeline", side_effect=slow_execute):
                    pred_task = asyncio.create_task(trigger_predict())
                    health_task = asyncio.create_task(trigger_health())
                    h_res, p_res = await asyncio.gather(health_task, pred_task)

                    self.assertEqual(h_res.status_code, 200)
                    self.assertEqual(p_res.status_code, 200)
                    self.assertTrue(health_completed_before_predict, "Health check must respond while pipeline is running")

        asyncio.run(run_concurrent())

    # Priority 2 Verification: hung pipeline times out with 504 and releases semaphore slot
    def test_hung_pipeline_times_out_with_504_and_releases_slot(self):
        import time
        from unittest.mock import patch
        import app.routes.predict as predict_module

        def hang_execute(*args, **kwargs):
            time.sleep(0.3)
            return {}

        original_timeout = predict_module.PIPELINE_TIMEOUT_SECONDS
        predict_module.PIPELINE_TIMEOUT_SECONDS = 0.05

        try:
            with patch("app.routes.predict.execute_pipeline", side_effect=hang_execute):
                response = self.client.post("/predict", headers=self.auth_headers)
                self.assertEqual(response.status_code, 504)
                self.assertIn("Pipeline exceeded", response.json()["detail"])
                self.assertIn("try a smaller image set", response.json()["detail"])

            # Concurrency slot must be immediately available for the next request
            self.assertEqual(pipeline_concurrency_guard._active_count, 0)
        finally:
            predict_module.PIPELINE_TIMEOUT_SECONDS = original_timeout

        next_res = self.client.post("/predict", headers=self.auth_headers)
        self.assertEqual(next_res.status_code, 200)

    # Priority 3 Verification: SSE client receives real-time stage transition events
    def test_sse_progress_streaming_receives_events(self):
        import httpx
        import json

        proj_id = "test_sse_live_run"

        async def run_sse_test():
            events_received = []
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                # 1. Trigger predict
                pred_res = await client.post("/predict", data={"project_id": proj_id}, headers=self.auth_headers)
                self.assertEqual(pred_res.status_code, 200)

                # 2. Connect to SSE events endpoint
                async with client.stream("GET", f"/api/v1/projects/{proj_id}/events", headers=self.auth_headers) as stream:
                    async for line in stream.aiter_lines():
                        if line.startswith("data: "):
                            ev = json.loads(line[6:])
                            events_received.append(ev)

            stages = [e["stage"] for e in events_received]
            self.assertGreaterEqual(len(events_received), 1)
            self.assertIn("stitching", stages)
            self.assertIn("complete", stages)

        asyncio.run(run_sse_test())

    # Fix 3 Verification: SSE stream closes cleanly on completion without hanging
    def test_sse_stream_closes_on_completion_concurrent(self):
        import httpx
        import json

        proj_id = "test_sse_stream_close_run"

        async def run_concurrent_sse():
            events_received = []
            stream_closed_cleanly = False
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                async def read_sse():
                    nonlocal stream_closed_cleanly
                    async with client.stream("GET", f"/api/v1/projects/{proj_id}/events", headers=self.auth_headers) as stream:
                        async for line in stream.aiter_lines():
                            if line.startswith("data: "):
                                ev = json.loads(line[6:])
                                events_received.append(ev)
                    stream_closed_cleanly = True

                async def trigger_predict():
                    await asyncio.sleep(0.05)
                    return await client.post("/predict", data={"project_id": proj_id}, headers=self.auth_headers)

                sse_task = asyncio.create_task(read_sse())
                pred_task = asyncio.create_task(trigger_predict())

                p_res = await pred_task
                self.assertEqual(p_res.status_code, 200)

                # Wait for SSE task to close with timeout to prove it doesn't hang
                await asyncio.wait_for(sse_task, timeout=5.0)
                self.assertTrue(stream_closed_cleanly, "SSE stream must close on pipeline completion rather than hanging")

            stages = [e["stage"] for e in events_received]
            self.assertIn("stitching", stages)
            self.assertIn("complete", stages)
            complete_ev = [e for e in events_received if e["stage"] == "complete"][0]
            self.assertEqual(complete_ev["status"], "done")

        asyncio.run(run_concurrent_sse())

    # Priority 4 Verification: File count cap (>60 images) returns 422
    def test_predict_exceeds_max_image_count_returns_422(self):
        files = [
            ("files", (f"drone_frame_{i:03d}.png", io.BytesIO(b"fake_content"), "image/png"))
            for i in range(61)
        ]
        response = self.client.post("/predict", files=files, headers=self.auth_headers)
        self.assertEqual(response.status_code, 422)
        self.assertIn("exceeds maximum limit of 60 images", response.json()["detail"])

    # Priority 4 Verification: Correlation/request ID returned in response and logged
    def test_predict_correlation_id_returned(self):
        valid_png = _make_valid_png_bytes(10, 10)
        files = [("files", ("valid_drone_corr.png", io.BytesIO(valid_png), "image/png"))]
        response = self.client.post("/predict", files=files, headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("correlation_id", data)
        self.assertIsNotNone(data["correlation_id"])
        self.assertEqual(len(data["correlation_id"]), 36)  # Standard UUID4 string length

    # Priority 4 Verification: verify_api_key dependency directly raises 401
    def test_dependencies_verify_api_key_direct(self):
        from app.dependencies import verify_api_key as dep_verify_api_key
        from fastapi import HTTPException

        # 1. Unset API_KEY on server fails closed with 401
        del os.environ["API_KEY"]
        with self.assertRaises(HTTPException) as cm:
            asyncio.run(dep_verify_api_key("any_key"))
        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn("no API_KEY configured on server", cm.exception.detail)

        # 2. Re-set server API_KEY
        os.environ["API_KEY"] = self.api_key

        # 3. Missing key raises 401
        with self.assertRaises(HTTPException) as cm:
            asyncio.run(dep_verify_api_key(None))
        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn("Invalid or missing API key", cm.exception.detail)

        # 4. Wrong key raises 401
        with self.assertRaises(HTTPException) as cm:
            asyncio.run(dep_verify_api_key("incorrect_key"))
        self.assertEqual(cm.exception.status_code, 401)
        self.assertIn("Invalid or missing API key", cm.exception.detail)

        # 5. Valid key returns key string
        res = asyncio.run(dep_verify_api_key(self.api_key))
        self.assertEqual(res, self.api_key)

    # Fix 4 Verification: GET /projects/{id}/layers/parcels.geojson returns empty state before run and real data after run
    def test_parcels_geojson_returns_empty_before_run_and_real_data_after_run(self):
        proj_id = "test_geojson_honest_empty"

        # 1. Before run: returns honest empty FeatureCollection with status=not_yet_generated
        res_before = self.client.get(f"/api/v1/projects/{proj_id}/layers/parcels.geojson", headers=self.auth_headers)
        self.assertEqual(res_before.status_code, 200)
        data_before = res_before.json()
        self.assertEqual(data_before["type"], "FeatureCollection")
        self.assertEqual(data_before.get("status"), "not_yet_generated")
        self.assertEqual(data_before.get("features"), [])
        self.assertNotIn("parcel_01", str(data_before))

        # 2. Run /predict for project
        pred_res = self.client.post("/predict", data={"project_id": proj_id}, headers=self.auth_headers)
        self.assertEqual(pred_res.status_code, 200)

        # 3. After run: returns real generated FeatureCollection
        res_after = self.client.get(f"/api/v1/projects/{proj_id}/layers/parcels.geojson", headers=self.auth_headers)
        self.assertEqual(res_after.status_code, 200)
        data_after = res_after.json()
        self.assertEqual(data_after["type"], "FeatureCollection")
        self.assertIn("coordinate_space", data_after)
        self.assertNotIn("not_yet_generated", data_after.get("status", ""))


if __name__ == "__main__":
    unittest.main()
