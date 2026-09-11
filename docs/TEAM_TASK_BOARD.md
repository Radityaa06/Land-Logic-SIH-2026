# Land Logic DRONE-MAPPING-AI — Team Task Board (6-Member Architecture)

This board delineates roles, discrete milestones, input requirements, expected outputs, and acceptance criteria for all 6 project members.

---

## 👥 Team Roles & Ownership Matrix

| Member | Role | Workspace | Assigned Git Branch |
| :--- | :--- | :--- | :--- |
| **Member 1** | Frontend & UI/UX | `frontend/` *(except `src/components/map/`)* | `feature/react-frontend` |
| **Member 2** | Backend & Pipeline Orchestrator | `backend/` | `feature/fastapi-backend` |
| **Member 3** | AI / Land Vision Engine | `ai/` | `feature/ai-integration` |
| **Member 4** | OpenCV & Orthomosaic Stitching | `opencv/` | `feature/opencv` |
| **Member 5** | GIS & Georeferencing | `gis/` | `feature/gis-geojson` |
| **Member 6** | Leaflet / Interactive Map | `frontend/src/components/map/` | `feature/leaflet-map` |

---

## 👨‍💻 Member 1 — Frontend & UI/UX

- **Workspace**: `frontend/` *(EXCEPT `frontend/src/components/map/`)*
- **Assigned Branch**: `feature/react-frontend`
- **Primary Tech**: React 18, Vite, Lucide Icons, Modern CSS
- **Current Status**: 🟢 `IN_SPRINT`

> [!IMPORTANT]
> **Strict Ownership Boundary**: Member 1 owns all frontend application shell, uploader, results, and common components. Member 1 must **NOT** modify or own `frontend/src/components/map/` (which belongs exclusively to Member 6).

### Tasks
- [x] **FE-01: Application Shell & Navigation**: Header, flight session chip, pipeline status indicator, theme support (`src/components/common/Header.jsx`).
- [x] **FE-02: Drone Image Upload Center**: Drag-and-drop batch file uploader with preview chips, validation, and upload progress (`src/components/upload/UploadZone.jsx`).
- [x] **FE-03: Real-Time Pipeline Visualizer**: Progress bars for each step (Upload -> Stitch -> AI -> Georef -> Map), log status, error handling (`src/components/common/PipelineStatus.jsx`).
- [x] **FE-04: Analytical Results Panel**: Metrics cards for survey acreage, vegetation cover %, mean NDVI/VARI, and parcel count (`src/components/results/MetricsPanel.jsx`).
- [x] **FE-05: Backend API Client Integration**: Connects UI directly to Member 2's `/predict` and `/projects` endpoints (`src/services/api.js`).

---

## ⚙️ Member 2 — Backend & Pipeline Orchestrator

- **Workspace**: `backend/`
- **Assigned Branch**: `feature/fastapi-backend`
- **Primary Tech**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Python-Multipart, Aiofiles
- **Current Status**: 🟢 `IN_SPRINT`

### Tasks
- [x] **BE-01: Core Gateway Setup**: FastAPI with CORS, request logging, structured error handling, and health endpoints (`app/main.py`).
- [x] **BE-02: Project & File Upload Manager**: Chunked file upload endpoints buffering drone images into `backend/uploads/{project_id}/` (`app/routes/upload.py`, `projects.py`).
- [x] **BE-03: Central Pipeline Coordinator**: Unified `POST /predict` and `POST /api/v1/predict` endpoint coordinating OpenCV -> AI -> GIS sequentially (`app/services/pipeline.py`, `app/routes/predict.py`).
- [x] **BE-04: Job Poller & Stage Dispatcher**: In-memory job tracker with status progression (`app/routes/pipeline.py`, `app/services/orchestrator.py`).
- [x] **BE-05: Artifact & Layer Serving**: File streaming endpoints for stitched PNGs, GeoTIFFs, and GeoJSON files (`app/main.py`).

---

## 🤖 Member 3 — AI / Land Vision Engine

- **Workspace**: `ai/`
- **Assigned Branch**: `feature/ai-integration`
- **Primary Tech**: PyTorch, Ultralytics YOLOv8 / Segment Anything, NumPy, PIL, Scikit-learn
- **Current Status**: 🟢 `IN_SPRINT`

### Canonical Land Classes
1. `agricultural_land`
2. `barren_soil`
3. `forests`
4. `water_bodies`
5. `man_made_structures`

### Tasks
- [x] **AI-01: Model Loader & Interface**: Clean model abstraction with heuristic spectral fallback when weights are not present (`ai/model.py`).
- [x] **AI-02: Image Tiling & Sliding Window**: Split high-res orthomosaics into 512x512 inference chips with overlap and reassemble masks (`ai/tiling.py`).
- [x] **AI-03: Crop & Land-Use Segmentation**: Classify the 5 canonical land categories (`ai/model.py`, `ai/inference.py`).
- [x] **AI-04: Vegetative Health Index (VARI)**: Compute spectral greenness index `(G - R) / (G + R - B)` (`ai/postprocess.py`).
- [x] **AI-05: Structured Predictions Output**: Produce structured parcel predictions (class, confidence, pixel bounding box, mean VARI) for Member 5 (`ai/inference.py`).
- [x] **AI-06: Unit Test Suite**: Comprehensive tests for tiling, VARI, and pipeline execution (`ai/tests/test_ai.py`).

---

## 👁️ Member 4 — OpenCV & Orthomosaic Stitching

- **Workspace**: `opencv/`
- **Assigned Branch**: `feature/opencv`
- **Primary Tech**: OpenCV (cv2), NumPy, Scikit-image, imutils
- **Current Status**: 🟢 `IN_SPRINT`

### Tasks
- [x] **CV-01: Image Quality Audit & Normalization**: Blur detection (Laplacian variance), exposure checks, and CLAHE normalization (`opencv/preprocess.py`).
- [x] **CV-02: Feature Extraction**: SIFT / ORB keypoint extraction and descriptor computation (`opencv/features.py`).
- [x] **CV-03: Pairwise Matching & RANSAC**: Robust k-NN matching with Lowe's ratio test and homography matrix estimation (`opencv/matching.py`).
- [x] **CV-04: Seam Blending**: Feather blending and multi-band compositing across adjacent frames (`opencv/blending.py`).
- [x] **CV-05: DroneStitcher Orchestration**: Multi-frame registration engine (`opencv/stitching.py`).
- [x] **CV-06: Unit Test Suite**: Test cases for preprocessing, feature detection, and mosaic outputs (`opencv/tests/test_opencv.py`).

---

## 🗺️ Member 5 — GIS & Georeferencing

- **Workspace**: `gis/`
- **Assigned Branch**: `feature/gis-geojson`
- **Primary Tech**: GDAL, Rasterio, GeoPandas, Shapely, PyProj, ExifRead
- **Current Status**: 🟢 `IN_SPRINT`

> [!CAUTION]
> **Strict Spatial Truth**: Never fabricate coordinates. If genuine GPS telemetry is unavailable, preserve pixel-space coordinates and set `coordinate_space = "pixel"`. If actual GPS exists, set `coordinate_space = "geographic"`.

### Tasks
- [x] **GIS-01: EXIF Metadata & Telemetry Parser**: Extract genuine GPS coordinates (lat, lon, altitude) without fake fallbacks (`gis/exif.py`).
- [x] **GIS-02: Ground Sampling Distance (GSD) Estimator**: Compute spatial resolution in cm/pixel from flight altitude and sensor parameters (`gis/gsd.py`).
- [x] **GIS-03: Georeferencing & World File**: 2D affine transformation matrices and ESRI world files (`gis/georeference.py`).
- [x] **GIS-04: Mask Vectorization**: Convert bounding boxes and parcel masks into simplified polygon rings (`gis/vectorize.py`).
- [x] **GIS-05: RFC 7946 GeoJSON Generator**: Emit valid GeoJSON FeatureCollections with explicit `coordinate_space` (`gis/geojson.py`).
- [x] **GIS-06: CRS Transformation & Validation**: WGS84, Web Mercator projection and polygon geometry validation (`gis/transform.py`, `gis/validate.py`).
- [x] **GIS-07: Unit Test Suite**: Test cases for EXIF, GSD, and GeoJSON validity (`gis/tests/test_gis.py`).

---

## 🗺️ Member 6 — Leaflet / Interactive Map

- **Workspace**: `frontend/src/components/map/` *(EXCLUSIVELY Member 6)*
- **Assigned Branch**: `feature/leaflet-map`
- **Primary Tech**: Leaflet, React, SVG Vector Canvas, CSS3
- **Current Status**: 🟢 `IN_SPRINT`

> [!IMPORTANT]
> **Exclusive Workspace**: Member 6 owns everything inside `frontend/src/components/map/`. Neither Member 1 nor other members should alter map files.

### Tasks
- [x] **MAP-01: Map Container & Basemap**: Interactive canvas/tile container with responsive scaling (`src/components/map/LeafletMap.jsx`).
- [x] **MAP-02: Dual Coordinate Space Handling**:
  - `coordinate_space === "geographic"`: Render on WGS84 coordinates.
  - `coordinate_space === "pixel"`: Render on calibrated 2D plane with prominent yellow badge: *"Pixel Space (Preserved Drone Coordinates)"*. Never presents fake coordinates as real world.
- [x] **MAP-03: GeoJSON Vector Polygon Styling**: Distinct color coding per land class (`agricultural_land`, `barren_soil`, `forests`, `water_bodies`, `man_made_structures`).
- [x] **MAP-04: Interactive Feature Inspector**: Popup inspector on parcel click displaying class, confidence, area, and VARI (`src/components/map/FeaturePopup.jsx`).
- [x] **MAP-05: Layer Controls & Legend**: Dynamic toggle switches for basemap, orthomosaic, parcel polygons, and heatmap (`LayerControl.jsx`, `Legend.jsx`).
- [x] **MAP-06: Stitched Orthomosaic Overlay**: Visualizer for stitched composite rasters (`RasterLayer.jsx`).
- [x] **MAP-07: Empty & Error State Handling**: Graceful fallback UI when awaiting flight data or if GeoJSON is invalid.

---

## 🎯 Acceptance Criteria Matrix

| Milestone | Reviewer | Verification Test | Status |
| :--- | :--- | :--- | :--- |
| **M1: Mock End-to-End** | All Members | Frontend uploads sample images -> Backend returns GeoJSON -> Member 6 Map visualizes polygons | 🟢 PASS |
| **M2: Core Engines Online** | Members 2, 4, 5 | OpenCV stitches frames into composite; GIS reads EXIF and outputs GeoJSON with strict `coordinate_space` | 🟢 PASS |
| **M3: AI Model Integrated** | Members 2, 3 | Stitched mosaic fed into AI pipeline; valid land classification masks produced | 🟢 PASS |
| **M4: Production Demo Polish** | Member 1, Team | Full responsive dashboard renders with interactive layer toggling and metric summary | 🟢 PASS |
