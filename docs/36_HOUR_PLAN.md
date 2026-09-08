# Land Logic DRONE-MAPPING-AI — 36-Hour Hackathon Execution Plan

This master plan allocates the 36-hour sprint into six distinct 6-hour operational blocks, synchronizing deliverables across all 5 team members.

---

## ⏱️ Timeline Overview

```
[00:00 - 06:00] Phase 1: Foundation, Environment & API Contracts
[06:00 - 12:00] Phase 2: Independent Core Engine Implementations
[12:00 - 18:00] Phase 3: First End-to-End Pipeline Integration Handshake
[18:00 - 24:00] Phase 4: Algorithmic Refinement, NDVI & GIS Accuracy
[24:00 - 30:00] Phase 5: UI/UX Polish, Dynamic Layer Toggles & Error Resilience
[30:00 - 36:00] Phase 6: Code Freeze, Dry Runs, Video Recording & Presentation
```

---

## 🕒 Phase 1: Hours 00:00 – 06:00 (Setup & Contracts)

### Goal
Establish local environments, agree on data structures, and create working mock endpoints for the frontend.

- **Member 1 (Frontend)**:
  - Initialize React application, configure Mapbox / Leaflet map container.
  - Implement drag-and-drop file upload UI with dummy file list.
- **Member 2 (Backend)**:
  - Initialize FastAPI skeleton, implement CORS and `/api/v1/projects` endpoints.
  - Mock responses for `/pipeline/stitch` and `/pipeline/ai-analyze` returning pre-generated fixtures.
- **Member 3 (AI)**:
  - Download pre-trained weights (YOLOv8-Seg / UNet) or build color-thresholding NDVI baseline.
  - Benchmark inference speed on sample drone tiles.
- **Member 4 (OpenCV)**:
  - Build standalone image stitcher script using OpenCV `Stitcher` class and custom SIFT matcher.
  - Test stitching on 3–5 sample overlapping aerial images.
- **Member 5 (GIS)**:
  - Implement EXIF GPS parser extracting latitude, longitude, and flight altitude.
  - Construct bounding box calculator and create initial template GeoJSON.

---

## 🕒 Phase 2: Hours 06:00 – 12:00 (Core Engines)

### Goal
Replace mock data with functional standalone processing engines.

- **Member 1 (Frontend)**:
  - Wire up file upload component with real multipart POST to Member 2's backend.
  - Render GeoJSON polygons on top of the satellite basemap.
- **Member 2 (Backend)**:
  - Implement asynchronous background worker to process pipeline stages.
  - Create Server-Sent Events (SSE) `/events` endpoint for streaming progress.
- **Member 3 (AI)**:
  - Implement sliding-window tiler (splits 4K drone orthomosaic into 512x512 tiles).
  - Run batch segmentation on crop rows vs. bare soil and output mask arrays.
- **Member 4 (OpenCV)**:
  - Handle exposure compensation and multi-band blending to eliminate seamline artifacts.
  - Add downsampling flag to generate quick preview orthophotos in < 15 seconds.
- **Member 5 (GIS)**:
  - Generate valid GeoTIFF with affine geotransform using Rasterio/GDAL.
  - Implement raster-to-vector polygonizer using `shapely` and `geopandas`.

---

## 🕒 Phase 3: Hours 12:00 – 18:00 (First End-to-End Handshake)

### Goal
Execute the complete chain from raw image upload to interactive map display with zero manual intervention.

- **Team Goal**: Run **Integration Test TC-05**:
  1. Member 1 selects 5 sample aerial photos in UI.
  2. Member 2 receives upload, triggers Member 4's OpenCV stitcher.
  3. Stitched image automatically passes to Member 3's AI pipeline for segmentation.
  4. Segmented mask passes to Member 5's GIS script for georeferencing and GeoJSON generation.
  5. Backend notifies frontend via SSE; map updates with stitched layer and clickable parcels.
- **Buffer Time**: 2 hours reserved for debugging inter-service data formatting issues.

---

## 🕒 Phase 4: Hours 18:00 – 24:00 (Refinement & Accuracy)

### Goal
Elevate output quality from basic prototype to impressive demo grade.

- **Member 1 (Frontend)**:
  - Add parcel inspection drawer (clicking a field shows area in hectares, mean NDVI, health status).
  - Add comparison slider (Raw Drone Imagery vs. AI Heatmap).
- **Member 2 (Backend)**:
  - Add project history, download buttons for GeoTIFF and Shapefile bundles.
  - Implement caching for intermediate pipeline steps.
- **Member 3 (AI)**:
  - Fine-tune classification thresholds to distinguish healthy crops, water stress, and weed patches.
  - Generate color-coded vegetative vigor heatmap.
- **Member 4 (OpenCV)**:
  - Improve feature matching robustness under low-texture conditions (e.g. dense uniform green canopies).
- **Member 5 (GIS)**:
  - Smooth polygon contours (Douglas-Peucker simplification) so vector layers load instantly in browser.
  - Calculate real-world surface areas in square meters / hectares.

---

## 🕒 Phase 5: Hours 24:00 – 30:00 (UI/UX Polish & Resilience)

### Goal
Make the web app look breathtaking, responsive, and foolproof against crashes.

- **Member 1 (Frontend)**:
  - Apply sleek dark-mode styling, glassmorphism cards, modern typography, and smooth transitions.
  - Add visual metric widgets: Total Land Area, Vegetative Index, Survey Flight Distance.
- **Member 2 (Backend)**:
  - Add robust validation and fallback mocks in case user uploads non-EXIF images.
  - Ensure zero unhandled exceptions crash the server.
- **Members 3, 4, 5 (AI, OpenCV, GIS)**:
  - Profile and optimize runtime performance; bundle utility scripts into clean modular imports.
  - Prepare high-quality demo datasets in `shared/sample_images/` and `shared/sample_outputs/`.

---

## 🕒 Phase 6: Hours 30:00 – 36:00 (Demo Prep & Code Freeze)

### Goal
Freeze code, rehearse demo pitch, and prepare submission materials.

- **Hour 30:00**: Strict **CODE FREEZE** on `main`. No new features allowed.
- **Hour 31:00**: Record 2-minute high-definition backup screen recording of the working pipeline.
- **Hour 32:00**: Assemble presentation deck (Problem statement, Solution architecture, Live demo script, Impact).
- **Hour 33:00**: Perform 3 full dry-run presentations with timing checks.
- **Hour 34:00**: Finalize documentation, update root `README.md` with demo screenshots and architecture diagram.
- **Hour 35:00 – 36:00**: Submission checklist verification & rest before final pitch!
