# Land Logic DRONE-MAPPING-AI

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active%20Sprint-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular%20Microservices-orange.svg)

An AI-powered drone imagery analysis and geospatial mapping platform designed for agricultural monitoring, land boundary extraction, elevation mapping, and automated orthomosaic generation.

---

## 🏗️ Repository Architecture

```text
Land-Logic-DRONE-MAPPING-AI/
│
├── frontend/                 👨‍💻 Member 1: Interactive Web Dashboard & Geospatial Map Viewer
│   ├── src/
│   │   ├── components/       # MapView, LayerControl, UploadDropzone, AnalyticsCard
│   │   └── services/         # API clients & WebSocket listeners
│   └── public/               # Static assets & icons
│
├── backend/                  ⚙️ Member 2: Orchestration API, Task Queue & Storage Gateway
│   ├── app/
│   │   ├── routes/           # REST endpoints (upload, jobs, pipeline, export)
│   │   ├── services/         # Pipeline orchestration, storage & background workers
│   │   ├── models/           # Pydantic data schemas & project entities
│   │   └── utils/            # Logging, image & coordinate helpers
│   ├── uploads/              # Staging zone for uploaded drone imagery
│   └── outputs/              # Generated orthophotos, GeoTIFFs & GeoJSON layers
│
├── ai/                       🤖 Member 3: Computer Vision, Land-Use & Crop Segmentation
│   ├── models/               # Model weights & ONNX / PyTorch checkpoints
│   └── inference/            # Prediction pipelines, NDVI calculation, boundary detection
│
├── opencv/                   👁️ Member 4: Orthomosaic Stitching & Image Preprocessing
│   ├── stitching/            # SIFT/ORB feature matching, homography & blending
│   └── preprocessing/        # Lens calibration, color balancing & shadow removal
│
├── gis/                      🗺️ Member 5: Geospatial Georeferencing & Vector Polygons
│   ├── geo_processing/       # EXIF GPS extraction, GeoTIFF creation, CRS transformation
│   └── layers/               # GeoJSON generation, cadastral overlays & elevation contours
│
├── shared/                   📦 Shared test artifacts & sample drone datasets
│   ├── sample_images/        # Raw drone input test frames
│   └── sample_outputs/       # Sample stitched orthophotos & GeoJSON outputs
│
└── docs/                     📚 System Specifications & Hackathon Guides
    ├── ARCHITECTURE.md       # High-level architecture & sequence diagrams
    ├── API_CONTRACT.md       # REST & WebSocket API specification
    ├── TEAM_TASK_BOARD.md    # Member responsibilities & task assignments
    ├── INTEGRATION_STATUS.md # Cross-team integration matrix & blockers
    ├── GIT_WORKFLOW.md       # Branching conventions & PR standards
    └── 36_HOUR_PLAN.md       # 36-Hour hackathon milestone schedule
```

---

## 👥 Team Roles & Responsibilities

| Role | Member | Primary Focus | Output Deliverables |
| :--- | :--- | :--- | :--- |
| **Frontend** | 👨‍💻 Member 1 | UI/UX, Mapbox/Leaflet viewer, layer toggles, job progress dashboard | React SPA, GeoJSON rendering, upload UI |
| **Backend** | ⚙️ Member 2 | FastAPI orchestrator, job queue, data persistence, REST endpoints | Unified REST API & background task runner |
| **AI / ML** | 🤖 Member 3 | Land use classification, crop health (NDVI), semantic segmentation | PyTorch / YOLO / Segment Anything pipeline |
| **OpenCV** | 👁️ Member 4 | Image alignment, feature detection, homography, orthomosaic stitcher | High-res stitched aerial composite |
| **GIS** | 🗺️ Member 5 | Georeferencing, EXIF GPS parsing, CRS transformation, GeoJSON creation | Geotagged GeoTIFF & exportable vector layers |

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm / yarn
- GDAL / Rasterio native dependencies (for GIS)
- OpenCV compatible build

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Running Sample Pipelines
Inspect each module's `README.md` in `ai/`, `opencv/`, and `gis/` for standalone execution commands.

---

## 📖 Documentation Quick Links
- **[System Architecture](docs/ARCHITECTURE.md)**: Deep dive into the data flow and system topology.
- **[API Contract](docs/API_CONTRACT.md)**: Schemas, payload formats, and endpoint documentation.
- **[Team Task Board](docs/TEAM_TASK_BOARD.md)**: Member task matrix and definition of done.
- **[Integration Status](docs/INTEGRATION_STATUS.md)**: Status of cross-module connections.
- **[Git Workflow](docs/GIT_WORKFLOW.md)**: Branching, pull requests, and commit standards.
- **[36-Hour Plan](docs/36_HOUR_PLAN.md)**: Hour-by-hour milestones for the project sprint.
