# Land Logic DRONE-MAPPING-AI — 36-Hour Hackathon Execution Plan (6 Members)

This master plan allocates the 36-hour sprint into six distinct 6-hour operational blocks, synchronizing deliverables across all **6 team members**.

---

## ⏱️ Timeline Overview

```text
[00:00 - 06:00] Phase 1: Environment Setup, 6-Branch Structure & API Contracts
[06:00 - 12:00] Phase 2: Independent Core Engine Implementations (M1-M6)
[12:00 - 18:00] Phase 3: First End-to-End Pipeline Integration Handshake
[18:00 - 24:00] Phase 4: Algorithmic Refinement, VARI Index & Strict GIS Accuracy
[24:00 - 30:00] Phase 5: Map Polish, Dual Coordinate Space & Error Handling
[30:00 - 36:00] Phase 6: Code Freeze, Dry Runs, Video Recording & Presentation
```

---

## 🕒 Phase 1: Hours 00:00 – 06:00 (Setup & Contracts)

### Goal
Establish local environments, verify 6 feature branches, and agree on data contracts.

- **Member 1 (Frontend)**:
  - Application shell (`Header.jsx`, `PipelineStatus.jsx`), drag-and-drop file uploader (`UploadZone.jsx`).
- **Member 2 (Backend)**:
  - FastAPI skeleton, CORS, `/predict` unified route, and `/api/v1/projects` endpoints.
- **Member 3 (AI)**:
  - Baseline model abstraction with the 5 canonical land categories, VARI mathematical routines.
- **Member 4 (OpenCV)**:
  - Image stitcher script with SIFT/ORB feature matching and CLAHE preprocessing.
- **Member 5 (GIS)**:
  - EXIF GPS parser, GSD estimator, and initial RFC 7946 GeoJSON schema generator.
- **Member 6 (Leaflet Map)**:
  - Initialize `frontend/src/components/map/`, configure map container, layer controls, and legend.

---

## 🕒 Phase 2: Hours 06:00 – 12:00 (Core Engines)

### Goal
Replace mock data with functional standalone processing engines.

- **Member 1 (Frontend)**: Wire up uploader with `api.predictDirect()` and implement `MetricsPanel.jsx`.
- **Member 2 (Backend)**: Implement `execute_pipeline()` coordinator calling OpenCV $\rightarrow$ AI $\rightarrow$ GIS.
- **Member 3 (AI)**: Implement sliding-window tiler (`ai/tiling.py`) and parcel contour extraction.
- **Member 4 (OpenCV)**: Implement feather blending (`opencv/blending.py`) and quality checks (`preprocess.py`).
- **Member 5 (GIS)**: Implement vectorization (`vectorize.py`) and strict `coordinate_space` enforcement.
- **Member 6 (Leaflet Map)**: Render GeoJSON polygons with class-specific color ramp and `FeaturePopup.jsx`.

---

## 🕒 Phase 3: Hours 12:00 – 18:00 (First End-to-End Handshake)

### Goal
Execute the complete chain from raw image upload to interactive map display with zero manual intervention.

- **Team Goal**: Run **Integration Test TC-05**:
  1. Member 1 drops drone photos in `UploadZone`.
  2. Member 2 receives upload, triggers Member 4's OpenCV stitcher.
  3. Stitched image passes to Member 3's AI pipeline for segmentation and VARI calculation.
  4. Segmented masks pass to Member 5's GIS script for vectorization and GeoJSON generation.
  5. Member 6's map updates with the stitched layer and clickable parcel polygons.
  6. Member 1's metrics panel renders area and health stats.

---

## 🕒 Phase 4: Hours 18:00 – 24:00 (Refinement & Accuracy)

### Goal
Elevate output quality from prototype to production demo grade.

- **Member 1**: Add responsive mobile view and error state banners.
- **Member 2**: Implement artifact file streaming (`GET /artifacts/{filename}`) and error logging.
- **Member 3**: Fine-tune classification thresholds and confidence scores.
- **Member 4**: Handle low-texture canopies with adaptive SIFT/ORB fallback.
- **Member 5**: Enforce Douglas-Peucker ring simplification and calculate real hectare acreage.
- **Member 6**: Add raster overlay support (`RasterLayer.jsx`) and dual coordinate-space badge.

---

## 🕒 Phase 5: Hours 24:00 – 30:00 (Polish & Production Build)

### Goal
Finalize user experience and execute verification test suites.

- Validate `npm run build` in `frontend/`.
- Run all 4 Python unit test suites (`opencv/tests`, `ai/tests`, `gis/tests`, `backend/tests`).
- Ensure no fake GPS coordinates are emitted anywhere.

---

## 🕒 Phase 6: Hours 30:00 – 36:00 (Code Freeze & Presentation)

### Goal
Record demo flight scenarios and finalize documentation.

- Rehearse live demonstration flow.
- Ensure all 6 feature branches are synchronized with `main`.
