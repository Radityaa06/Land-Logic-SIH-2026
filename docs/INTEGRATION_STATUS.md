# Land Logic DRONE-MAPPING-AI — Integration Status (6-Member Setup)

This document tracks all inter-module contracts, integration test cases, interface owners, and active blockers across the 6 project members.

---

## 1. Interface Integration Matrix

| Interface ID | Producer Module | Consumer Module | Data Contract | Status | Description / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **INT-01** | Frontend (M1) | Backend (M2) | `POST /predict` (Multipart image batch) | 🟢 READY | Primary pipeline trigger sending raw images directly to backend |
| **INT-02** | Backend (M2) | OpenCV (M4) | `stitcher.stitch_image_list(paths, out_path)` | 🟢 READY | OpenCV stitches flight images into orthomosaic composite |
| **INT-03** | Backend (M2) | GIS (M5) | `extract_gps_coordinates(path)` | 🟢 READY | Extracts telemetry; enforces `coordinate_space` without fake GPS |
| **INT-04** | OpenCV (M4) | AI (M3) | Stitched composite (`stitched_orthomosaic.png`) | 🟢 READY | Input image for 512x512 sliding-window inference |
| **INT-05** | AI (M3) | GIS (M5) | Structured parcel records (`predictions` list) | 🟢 READY | Land classes, confidence, pixel bounding box, mean VARI |
| **INT-06** | GIS (M5) | Backend (M2) | RFC 7946 FeatureCollection (`parcels.geojson`) | 🟢 READY | Explicit `coordinate_space` ('geographic' or 'pixel') |
| **INT-07** | Backend (M2) | Member 6 Map | `GET /layers/parcels.geojson` or inline GeoJSON | 🟢 READY | Consumed directly by `LeafletMap.jsx` |
| **INT-08** | Backend (M2) | Member 6 Map | `GET /artifacts/stitched_orthomosaic.png` | 🟢 READY | Rendered as image overlay via `RasterLayer.jsx` |
| **INT-09** | Member 1 | Member 6 Map | Props passing in `Dashboard.jsx` | 🟢 READY | Strict boundary: M1 mounts M6's `LeafletMap` as a black box |
| **INT-10** | Backend (M2) | Frontend (M1) | Metrics summary payload (`summary` dict) | 🟢 READY | Drives `MetricsPanel.jsx` analytics cards |

---

## 2. Integration Test Checklist

- [x] **TC-01: Ingestion Handshake (M1 -> M2)**
  - **Steps**: Member 1 submits image files via `api.predictDirect()` to `POST /predict`.
  - **Result**: Backend buffers files, triggers orchestrator, and returns 200 OK JSON response.

- [x] **TC-02: OpenCV Stitching Pipeline (M4)**
  - **Steps**: `DroneStitcher` called on input image frames.
  - **Result**: Valid stitched PNG composite emitted with CLAHE balance and contrast audit.

- [x] **TC-03: AI Segmentation & Spectral Analysis (M3)**
  - **Steps**: `run_inference()` invoked on stitched mosaic.
  - **Result**: Computes VARI index and segments the 5 canonical land categories.

- [x] **TC-04: GIS Telemetry & GeoJSON Pipeline (M5)**
  - **Steps**: Reads genuine EXIF tags, calculates GSD, and polygonizes AI masks into GeoJSON.
  - **Result**: Emits valid RFC 7946 GeoJSON with strict `coordinate_space` ('geographic' or 'pixel').

- [x] **TC-05: Leaflet Map Rendering (M6)**
  - **Steps**: `LeafletMap.jsx` receives GeoJSON data and raster overlay.
  - **Result**: Correctly styles polygons by land-use class; displays yellow badge if in pixel space and green badge if geographic.

- [x] **TC-06: Frontend Build (M1 & M6)**
  - **Steps**: Execute `npm run build` in `frontend/`.
  - **Result**: Vite compiles with 0 errors (`dist/` generated).

---

## 3. Strict Boundary Verification

```text
Member 1:
frontend/src/components/upload/
frontend/src/components/results/
frontend/src/components/common/
frontend/src/pages/
frontend/src/services/

Member 6:
frontend/src/components/map/ (LeafletMap.jsx, FeaturePopup.jsx, LayerControl.jsx, Legend.jsx, RasterLayer.jsx, map.css)
```
No overlapping ownership files detected.
