# Land Logic DRONE-MAPPING-AI — Integration Status

This document tracks all inter-module contracts, integration test cases, interface owners, and active blockers.

---

## 1. Interface Integration Matrix

| Interface ID | Producer Module | Consumer Module | Data Contract | Status | Blockers / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **INT-01** | Frontend (M1) | Backend (M2) | `POST /projects/{id}/upload` (Multipart images) | 🟢 READY (Contract defined) | Awaiting frontend UI dropzone wire-up |
| **INT-02** | Backend (M2) | OpenCV (M4) | CLI / Python method: `stitch_images(image_paths, output_path)` | 🟢 READY (Callable service) | Large memory footprint on >50 images |
| **INT-03** | OpenCV (M4) | GIS (M5) | Stitched mosaic (`ortho.png`) + EXIF coordinates table | 🟢 READY (Schema agreed) | Ensure coordinate ordering is consistently `(lat, lon)` |
| **INT-04** | OpenCV (M4) | AI (M3) | Stitched composite (`ortho.png`) | 🟢 READY (File path reference) | Tile generator required for gigapixel images |
| **INT-05** | AI (M3) | GIS (M5) | Binary / Categorical Segmentation Mask (`mask.png` / NumPy array) | 🟢 READY (NumPy / GeoTIFF array) | Class index mapping needs standardization |
| **INT-06** | GIS (M5) | Backend (M2) | Georeferenced GeoTIFF (`ortho.tif`) + `parcels.geojson` | 🟢 READY (File path + JSON) | Storage location: `backend/outputs/{id}/` |
| **INT-07** | Backend (M2) | Frontend (M1) | `GET /projects/{id}/layers/parcels.geojson` | 🟢 READY (RFC 7946 GeoJSON) | Frontend parser requires valid EPSG:4326 coords |
| **INT-08** | Backend (M2) | Frontend (M1) | `GET /projects/{id}/events` (SSE Progress stream) | 🟢 READY (SSE JSON payloads) | Handle reconnect on network hiccup |

---

## 2. Integration Test Checklist

- [ ] **TC-01: Ingestion Handshake**
  - **Steps**: Member 1 submits 3 sample drone photos from `shared/sample_images/` through the API.
  - **Success Criteria**: Files buffered in `backend/uploads/test_run/` with valid file sizes and SHA256 checksums.

- [ ] **TC-02: OpenCV Stitching Pipeline**
  - **Steps**: Member 4's script invoked on sample images.
  - **Success Criteria**: Output `sample_stitched.png` generated with no black border artifacts or shearing.

- [ ] **TC-03: AI Segmentation Pipeline**
  - **Steps**: Member 3 runs inference on `sample_stitched.png`.
  - **Success Criteria**: Returns class map matrix with classifications for vegetation, soil, and structures.

- [ ] **TC-04: GIS Georeferencing & GeoJSON Pipeline**
  - **Steps**: Member 5 reads image EXIFs, aligns the stitched photo to real-world lat/lon, and vectorizes AI masks.
  - **Success Criteria**: Valid GeoTIFF passes `gdalinfo` without projection errors; `parcels.geojson` validates on `geojson.io`.

- [ ] **TC-05: Full Round-Trip Demonstration**
  - **Steps**: Execute end-to-end execution from frontend click to interactive map rendering.
  - **Success Criteria**: Web viewer displays drone raster overlay and interactive vector polygons within < 60 seconds.

---

## 3. Active Blockers & Resolution Log

| Date | Module | Blocker Description | Owner | Status | Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| *Sprint Start* | OpenCV / GIS | Determining coordinate alignment when flight path is irregular | M4, M5 | 🟢 Solved | Fallback to bounding box affine transform using corner EXIF coordinates |
| *Sprint Start* | AI / Backend | Handling memory limits when segmenting high-res 4K drone mosaics | M2, M3 | 🟢 Solved | Implemented 512x512 sliding window tiling with overlap blending |
