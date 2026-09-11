# Backend & Pipeline Orchestrator — Land Logic DRONE-MAPPING-AI

⚙️ **Owner**: Member 2  
🌿 **Assigned Branch**: `feature/fastapi-backend`  
🛠️ **Tech Stack**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Python-Multipart, Aiofiles, Pillow  
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
3. **Demo Hardening & Security Controls**:
   - **Shared API Key Authentication**: Protects `/predict` and `/api/v1/predict` via `X-API-Key` header with fail-closed security. `/health` remains public for uptime checks.
   - **Safe Image Decode**: Uses PIL integrity verification (`verify()` + draft `load()`) to reject corrupted files or renamed non-images before pipeline execution.
   - **Pipeline Concurrency Guard**: Caps concurrent heavy pipeline runs (default: 3) to prevent worker OOM crashes on Render, returning HTTP 503 (`Server busy, try again in a moment`).
4. **Artifact & Layer Serving**: Streams stitched PNG/TIFF images and GeoJSON layers (`GET /api/v1/projects/{id}/artifacts/{filename}`).
5. **Job Monitoring & Project Sessions**: Handles background job tracking (`/api/v1/jobs/{id}`) and batch image upload staging.

---

## 📂 Directory Structure
```text
backend/
├── app/
│   ├── main.py           # FastAPI entrypoint, CORS, startup security audit & static artifact mounts
│   ├── dependencies.py   # API key verification & concurrency guard
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
│       └── logger.py     # Structured request and pipeline logging
├── tests/
│   └── test_backend.py   # Unit test suite for backend pipeline & security controls
├── uploads/              # Incoming drone flight images (.gitkeep)
├── outputs/              # Stitched orthomosaics & GeoJSON exports (.gitkeep)
├── .env.example          # Environment configuration template
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🚀 Execution & Testing

```bash
# Run backend unit tests (all 12 passing)
python3 -m unittest backend/tests/test_backend.py

# Run FastAPI dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive Swagger docs available at: `http://localhost:8000/docs`

---

## ⚙️ Environment Configuration

| Variable | Default | Description |
| :--- | :--- | :--- |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed origins for CORS. |
| `API_KEY` | *(None / Unset)* | Shared secret key required in `X-API-Key` header for `/predict`. Fails closed (HTTP 401) if unset. |
| `MAX_CONCURRENT_REQUESTS` | `3` | Maximum simultaneous heavy pipeline jobs. Excess requests return HTTP 503. |
| `PIPELINE_TIMEOUT_SECONDS` | `90` | Maximum execution time per pipeline run before returning HTTP 504. |
| `MAX_IMAGE_COUNT` | `60` | Maximum number of images allowed per batch upload. Excess requests return HTTP 422. |

---

## 📡 Real-Time Progress Streaming (SSE)

### Endpoint: `GET /api/v1/projects/{project_id}/events`
- **Protocol**: Server-Sent Events (`text/event-stream`)
- **Event Payload Structure**:
  ```json
  {
    "project_id": "proj_abc123",
    "stage": "stitching | gps_extraction | inference | geojson | complete",
    "status": "started | done | error",
    "message": "Human-readable description of current work",
    "timestamp": "2026-09-12T00:58:26.123456"
  }
  ```
- **Stream Lifecycle**:
  - Automatically replays any past events for late-connecting clients.
  - Streams real-time live stage transitions as they occur.
  - Sends periodic `: ping\n\n` comments to prevent reverse proxy connection drops.
  - Automatically closes the stream once stage reaches `complete` or `error`.

### Honest Architecture Disclosure
`/predict` maintains a synchronous HTTP request-response flow to preserve compatibility with existing frontend UI contracts. However, to prevent judge-facing UI spinners during the 10-60s execution:
1. `execute_pipeline()` runs off the main event loop inside Python's worker thread pool (`asyncio.to_thread`).
2. Each stage transition publishes real events into the central `PROJECT_EVENTS` event bus in `orchestrator.py`.
3. The frontend connects to `GET /api/v1/projects/{project_id}/events` to render live pipeline progress chips, while awaiting the final HTTP response. No linear fake percentages are emitted; statuses reflect actual milestone completions.

---

## 🛡️ Production & Render Deployment Instructions (Manual Steps)

### 1. Mandatory Manual Step: Set Deployed Frontend CORS in Render
Because local code cannot verify or alter live cloud configuration directly, you **must perform this manual step in the Render Dashboard**:
1. Go to your Backend Web Service on Render -> **Environment**.
2. Add or update the `ALLOWED_ORIGINS` environment variable to include your real frontend URL:
   ```env
   ALLOWED_ORIGINS=https://your-frontend-domain.onrender.com,http://localhost:5173
   ```
3. Set your secret `API_KEY`:
   ```env
   API_KEY=your-secure-demo-key-here
   ```

### 2. Infrastructure-Level Request Body Size Cap
The application layer in `predict.py` enforces a strict **15MB** per-image limit (`MAX_FILE_SIZE_BYTES`) and runs safe image decoding. However, on single-worker Render instances (512MB RAM), huge malicious uploads (e.g. 100MB+) can consume worker RAM before reaching Python's validation logic.

To mitigate this at the infrastructure/reverse-proxy tier:
- **Render Ingress Proxy**: Render enforces an overall platform-level maximum request body size (typically 32MB for standard services).
- **Custom Domain / Cloudflare Reverse Proxy**: If using Cloudflare in front of Render, configure a **WAF Request Body Size Limit** or Page Rule capping POST bodies to `25MB`.
- **Uvicorn Start Command**: On Render, start the service with explicit concurrency constraints:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT --limit-concurrency 10
  ```
