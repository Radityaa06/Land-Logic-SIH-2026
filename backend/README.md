# Backend & Pipeline Orchestrator — Land Logic DRONE-MAPPING-AI

⚙️ **Owner**: Member 2  
🌿 **Assigned Branch**: `feature/fastapi-backend`  
🛠️ **Tech Stack**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Python-Multipart, Aiofiles  
📁 **Workspace**: `backend/`

---

## 🎯 Scope & Responsibilities
1. **API Gateway & Core Router**: FastAPI application with CORS, request validation, structured error handling, and health endpoints.
2. **Central Pipeline Coordinator**:
   Acts as the central pipeline orchestrator connecting OpenCV, AI, and GIS:
   ```text
   Frontend  ──>  POST /predict  ──>  Backend
                                        │
                                        ├──> Member 4 (OpenCV Stitching)
                                        ├──> Member 3 (AI Segmentation & VARI)
                                        └──> Member 5 (GIS Georeferencing & GeoJSON)
                                        │
   Frontend  <──  JSON Response   <─────┘
   ```
3. **Artifact & Layer Serving**: Streams stitched PNG/TIFF images and GeoJSON layers (`GET /api/v1/projects/{id}/artifacts/{filename}`).
4. **Job Monitoring & Project Sessions**: Handles background job tracking (`/api/v1/jobs/{id}`) and batch image upload staging.

---

## 📂 Directory Structure
```text
backend/
├── app/
│   ├── main.py           # FastAPI entrypoint, CORS & static artifact mounts
│   ├── routes/
│   │   ├── predict.py    # Unified POST /predict and /api/v1/predict endpoint
│   │   ├── projects.py   # Project creation and status retrieval
│   │   ├── upload.py     # Multi-image multipart upload handler
│   │   └── pipeline.py   # Background job dispatch and job status polling
│   ├── services/
│   │   ├── pipeline.py   # Central pipeline coordinator (invoking OpenCV, AI, GIS)
│   │   └── orchestrator.py # Async job queue & stage state transitions
│   ├── models/
│   │   └── schemas.py    # Pydantic models (Project, Predict, Job schemas)
│   └── utils/
│       └── logger.py     # Logging helpers
├── tests/
│   └── test_backend.py   # Unit test suite for backend pipeline
├── uploads/              # Incoming drone flight images (.gitkeep)
├── outputs/              # Stitched orthomosaics & GeoJSON exports (.gitkeep)
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🚀 Execution & Testing

```bash
# Run backend unit tests
python3 -m unittest backend/tests/test_backend.py

# Run FastAPI dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger docs available at: `http://localhost:8000/docs`

---

## ⚙️ Environment Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed origins. Before deploying to production (e.g. Render), add your deployed frontend URL (e.g. `https://your-app.onrender.com`) to `ALLOWED_ORIGINS`. |

