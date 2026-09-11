# Land Logic DRONE-MAPPING-AI — SIH 2026

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Sprint-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-6--Member%20Modular%20Pipeline-orange.svg)

An AI-powered drone imagery analysis and geospatial mapping platform designed for agricultural monitoring, land boundary extraction, elevation mapping, and automated orthomosaic generation.

---

## 🏗️ 6-Member Repository Architecture

```text
Land-Logic-SIH-2026/
│
├── frontend/                         👨‍💻 Member 1: Application Shell, Uploader & Results Panel
│   ├── src/
│   │   ├── components/
│   │   │   ├── upload/              # Drag-and-drop drone batch uploader (Member 1)
│   │   │   ├── results/             # Land intelligence & statistics metrics (Member 1)
│   │   │   ├── common/              # Header, navigation & pipeline progress (Member 1)
│   │   │   └── map/                 🗺️ Member 6: Leaflet & Interactive Map (EXCLUSIVELY Member 6)
│   │   │       ├── LeafletMap.jsx   # Vector polygon renderer & spatial canvas
│   │   │       ├── FeaturePopup.jsx # Interactive parcel inspector
│   │   │       ├── LayerControl.jsx # Basemap, ortho & parcel toggles
│   │   │       ├── Legend.jsx       # Land class color coding
│   │   │       ├── RasterLayer.jsx  # Stitched mosaic overlay
│   │   │       └── map.css          # Map-specific styling
│   │   ├── pages/                   # Dashboard page
│   │   ├── services/                # API client connecting to Member 2's backend
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/                      # Static assets & icons
│   ├── index.html                   # HTML entrypoint
│   ├── vite.config.js               # Vite build configuration
│   └── package.json
│
├── backend/                          ⚙️ Member 2: Central Pipeline Orchestrator & API Gateway
│   ├── app/
│   │   ├── routes/
│   │   │   ├── predict.py           # Unified POST /predict coordinator route
│   │   │   ├── projects.py          # Session & project lifecycle
│   │   │   ├── upload.py            # Drone image upload staging
│   │   │   └── pipeline.py          # Job status polling & background workers
│   │   ├── services/
│   │   │   ├── pipeline.py          # Pipeline coordinator (OpenCV -> AI -> GIS)
│   │   │   └── orchestrator.py      # Async task status progression
│   │   ├── models/schemas.py        # Pydantic data contracts (Predict, Project, Job)
│   │   └── main.py                  # FastAPI gateway & artifact file streaming
│   ├── tests/                       # Backend test suite
│   ├── uploads/                     # Buffered raw drone imagery
│   └── outputs/                     # Generated orthomosaics, masks & GeoJSON layers
│
├── ai/                               🤖 Member 3: AI & Land Vision Engine
│   ├── model.py                     # Canonical 5-class model abstraction & loader
│   ├── inference.py                 # Top-level inference runner coordinating tiling & postprocess
│   ├── tiling.py                    # 512x512 sliding-window chip generation & mask reassembly
│   ├── postprocess.py               # VARI spectral vegetation index & contour extraction
│   ├── tests/test_ai.py             # AI unit test suite
│   └── models/                      # Checkpoints & weights (.gitkeep)
│
├── opencv/                           👁️ Member 4: OpenCV & Orthomosaic Stitching
│   ├── preprocess.py                # CLAHE exposure balance & image quality audit
│   ├── features.py                  # SIFT / ORB keypoint detector & descriptors
│   ├── matching.py                  # k-NN matching & RANSAC homography estimation
│   ├── blending.py                  # Feather & multi-band seam blending
│   ├── stitching.py                 # DroneStitcher registration engine
│   └── tests/test_opencv.py         # OpenCV unit test suite
│
├── gis/                              🗺️ Member 5: GIS & Georeferencing
│   ├── exif.py                      # Genuine EXIF GPS extraction (strict coordinate_space)
│   ├── gsd.py                       # Ground Sampling Distance (GSD) estimator
│   ├── georeference.py              # 2D affine transformation matrices & world files
│   ├── vectorize.py                 # Bounding box & mask-to-polygon conversion
│   ├── geojson.py                   # RFC 7946 GeoJSON generator (pixel / geographic)
│   ├── transform.py                 # Coordinate conversions (WGS84, Web Mercator)
│   ├── validate.py                  # GeoJSON topological validation
│   └── tests/test_gis.py            # GIS unit test suite
│
├── shared/                           📦 Shared test artifacts & sample drone datasets
│   ├── sample_images/               # Raw drone input test frames
│   └── sample_outputs/              # Sample stitched orthophotos & GeoJSON outputs
│
└── docs/                             📚 Specifications & Team Workflow
    ├── TEAM_TASK_BOARD.md           # 6-Member task matrix & definition of done
    ├── GIT_WORKFLOW.md              # 6-Branch Git conventions & review standards
    ├── API_CONTRACT.md              # REST specification & GeoJSON spatial contract
    └── INTEGRATION_STATUS.md        # Cross-module integration matrix & blocker log
```

---

## 👥 6-Member Ownership Matrix

| Member | Role | Workspace | Git Branch | Primary Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Member 1** | Frontend & UI/UX | `frontend/` *(excl. `components/map/`)* | `feature/react-frontend` | React SPA, upload dropzone, progress bars, analytics cards |
| **Member 2** | Backend Orchestrator | `backend/` | `feature/fastapi-backend` | FastAPI gateway, `POST /predict`, pipeline coordinator, artifact server |
| **Member 3** | AI / Land Vision | `ai/` | `feature/ai-integration` | 5-class segmentation, sliding window tiler, VARI spectral index |
| **Member 4** | OpenCV Stitching | `opencv/` | `feature/opencv` | CLAHE exposure balance, SIFT/ORB features, homography, orthomosaic stitcher |
| **Member 5** | GIS / Georeferencing | `gis/` | `feature/gis-geojson` | EXIF extraction (no fake GPS), GSD, world files, RFC 7946 GeoJSON |
| **Member 6** | Leaflet / Interactive Map | `frontend/src/components/map/` | `feature/leaflet-map` | Vector polygon styling, popups, legend, layer controls, coordinate space handling |

---

## ⚡ Pipeline Flow

```text
Frontend (Member 1)
   │
   ▼ POST /predict (Multipart Drone Images)
Backend Orchestrator (Member 2)
   │
   ├──> Member 4 (OpenCV): Stitching & Preprocessing -> Stitched Orthomosaic
   │
   ├──> Member 3 (AI): Inference & Spectral Analysis -> Segmentation Mask & VARI Index
   │
   └──> Member 5 (GIS): Telemetry & Vectorization -> RFC 7946 GeoJSON (Strict coordinate_space)
   │
   ▼ JSON Response (GeoJSON, Metrics Summary & Artifact URLs)
Frontend & Leaflet Map (Member 6 & Member 1)
```

---

## ⚡ Quick Start

### 1. Backend Setup (Member 2)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (Members 1 & 6)
```bash
cd frontend
npm install
npm run dev      # Starts Vite dev server at http://localhost:5173
npm run build    # Validates production build
```

### 3. Running Unit Tests Across Modules
```bash
# OpenCV (Member 4)
python3 -m unittest opencv/tests/test_opencv.py

# AI Engine (Member 3)
python3 -m unittest ai/tests/test_ai.py

# GIS Engine (Member 5)
python3 -m unittest gis/tests/test_gis.py

# Backend (Member 2)
python3 -m unittest backend/tests/test_backend.py
```

---

## 📖 Documentation Quick Links
- **[Team Task Board (6 Members)](docs/TEAM_TASK_BOARD.md)**: Role boundaries, milestones, and acceptance criteria.
- **[Git Workflow (6 Branches)](docs/GIT_WORKFLOW.md)**: Branch assignments, PR requirements, and commit conventions.
- **[API Contract](docs/API_CONTRACT.md)**: REST endpoints, `POST /predict`, and GeoJSON schemas.
- **[Integration Status](docs/INTEGRATION_STATUS.md)**: Cross-module interface tracking and blocker resolutions.
