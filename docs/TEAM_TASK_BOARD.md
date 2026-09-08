# Land Logic DRONE-MAPPING-AI — Team Task Board

This board delineates roles, discrete milestones, input requirements, expected outputs, and acceptance criteria for all 5 project members.

---

## 👨‍💻 Member 1 — Frontend & Geospatial Visualizer

- **Workspace**: `frontend/`
- **Primary Tech**: React (Vite / Next.js), Mapbox GL JS / Leaflet, Tailwind CSS or Modern Vanilla CSS, Lucide icons
- **Current Status**: 🟡 `IN_SPRINT`

### Tasks
- [ ] **FE-01: Application Shell & Navigation**: Header, project switcher, status badge, dark/light theme toggle.
- [ ] **FE-02: Drone Image Upload Center**: Drag-and-drop file uploader with chunking support, preview grid, and EXIF summary chips.
- [ ] **FE-03: Real-Time Pipeline Visualizer**: Progress bars for each step (Upload -> Stitch -> AI -> Georef), log drawer, error modal.
- [ ] **FE-04: Interactive Map Viewer**: Dual-layer map component capable of displaying base satellite imagery, custom stitched GeoTIFF/PNG rasters, and GeoJSON polygon overlays.
- [ ] **FE-05: Analytical Panel & Layer Toggles**: Checkboxes for NDVI heatmap, boundary lines, crop stress zones, and parcel inspection stats modal.

---

## ⚙️ Member 2 — Backend & Pipeline Orchestrator

- **Workspace**: `backend/`
- **Primary Tech**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Python-Multipart
- **Current Status**: 🟡 `IN_SPRINT`

### Tasks
- [ ] **BE-01: Core Gateway Setup**: Initialize FastAPI with CORS, request logging, structured error handling, and health endpoints.
- [ ] **BE-02: Project & File Upload Manager**: Chunked file upload endpoints buffering drone images into `backend/uploads/{project_id}/`.
- [ ] **BE-03: Modular Pipeline Runner**: Asynchronous job dispatcher executing OpenCV stitching, AI inference, and GIS modules sequentially or concurrently.
- [ ] **BE-04: SSE / WebSocket Job Poller**: Publish progress updates (0–100%) and stage notifications to frontend clients.
- [ ] **BE-05: Artifact Serving & Export**: Safe file-streaming endpoints for stitched PNGs, GeoTIFFs, and GeoJSON files with correct MIME types.

---

## 🤖 Member 3 — AI & Land Vision Engine

- **Workspace**: `ai/`
- **Primary Tech**: PyTorch, Ultralytics YOLOv8 / Segment Anything, OpenCV, NumPy, Scikit-learn
- **Current Status**: 🟡 `IN_SPRINT`

### Tasks
- [ ] **AI-01: Model Ingestion & Weight Check**: Set up lightweight semantic segmentation and object detection model checkpoints.
- [ ] **AI-02: Image Tiling & Sliding Window**: Implement tiling logic to split high-res (10,000x10,000+) orthomosaics into 512x512 inference chips with overlap.
- [ ] **AI-03: Crop & Land-Use Segmentation**: Classify agricultural land, barren soil, forests, water bodies, and man-made structures.
- [ ] **AI-04: Vegetative Health (NDVI / VARI Index)**: Compute spectral indices from RGB bands (Visible Atmospherically Resistant Index - VARI) or multispectral channels.
- [ ] **AI-05: Mask Reassembly & Vector Boundary Output**: Merge chip predictions into a full-scale binary/multiclass mask and emit contour arrays for GIS conversion.

---

## 👁️ Member 4 — OpenCV & Orthomosaic Stitching

- **Workspace**: `opencv/`
- **Primary Tech**: OpenCV (cv2), NumPy, Scikit-image, imutils
- **Current Status**: 🟡 `IN_SPRINT`

### Tasks
- [ ] **CV-01: Image Quality Audit & Normalization**: Lens distortion correction, histogram matching, and contrast enhancement.
- [ ] **CV-02: Feature Extraction**: SIFT (Scale-Invariant Feature Transform) / ORB keypoint extraction and descriptor calculation.
- [ ] **CV-03: Pairwise Matching & RANSAC**: Robust feature matching using FLANN / BFMatcher with geometric outlier rejection.
- [ ] **CV-04: Global Registration & Seam Carving**: Stitch overlapping image pairs into an unified mosaic coordinate plane using homography transformations.
- [ ] **CV-05: Multi-Band Blending**: Smooth exposure differences across adjacent frames using Gaussian/Laplacian pyramid blending.

---

## 🗺️ Member 5 — GIS & Georeferencing

- **Workspace**: `gis/`
- **Primary Tech**: GDAL, Rasterio, GeoPandas, Shapely, PyProj, ExifRead
- **Current Status**: 🟡 `IN_SPRINT`

### Tasks
- [ ] **GIS-01: EXIF Metadata & Telemetry Parser**: Extract GPS coordinates (lat, lon, altitude), gimbal yaw/pitch/roll, and camera sensor parameters from raw images.
- [ ] **GIS-02: Ground Sampling Distance (GSD) Estimator**: Compute spatial resolution per pixel based on flight height and sensor focal length.
- [ ] **GIS-03: World File & GeoTIFF Writer**: Compute affine transformation matrices and burn spatial reference systems (EPSG:4326 / WGS84) into the stitched output.
- [ ] **GIS-04: Polygon Polygonization & Smoothing**: Convert AI raster masks into simplified GeoJSON polygons with Douglas-Peucker algorithm.
- [ ] **GIS-05: Coordinate Transformation**: Project coordinates seamlessly between UTM zones, WGS84, and Web Mercator (EPSG:3857).

---

## 🎯 Acceptance Criteria Matrix

| Milestone | Reviewer | Verification Test |
| :--- | :--- | :--- |
| **M1: Mock End-to-End** | All Members | Frontend uploads 5 sample images -> Backend returns mock stitched result & GeoJSON -> Map visualizes polygons |
| **M2: Core Engines Online** | Members 2, 4, 5 | OpenCV stitches real drone frames into PNG; GIS reads EXIF and outputs GeoTIFF |
| **M3: AI Model Integrated** | Members 2, 3 | Stitched mosaic fed into AI pipeline; valid land classification masks produced |
| **M4: Production Demo Polish** | Member 1, Team | Full responsive dashboard renders with interactive layer toggling and metric summary |
