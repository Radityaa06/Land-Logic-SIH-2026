# Backend — Land Logic DRONE-MAPPING-AI

⚙️ **Owner**: Member 2  
**Tech Stack**: Python 3.10+, FastAPI, Uvicorn, Pydantic, Python-Multipart

---

## 🎯 Scope & Responsibilities
1. **API Gateway**: Provides RESTful endpoints for project management, batch image upload, and pipeline execution.
2. **Pipeline Orchestrator**: Coordinates inter-process execution between Member 4 (OpenCV Stitcher), Member 3 (AI Inference), and Member 5 (GIS Georeferencer).
3. **Task Queue & Streaming**: Manages background job status and emits real-time Server-Sent Events (SSE) to the frontend.
4. **Artifact Management**: Organizes file staging in `backend/uploads/` and exportable layers in `backend/outputs/`.

---

## 🚀 Quickstart

```bash
# 1. Navigate to backend directory
cd backend

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start FastAPI server with live reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API documentation available at `http://localhost:8000/docs` (Swagger UI).

---

## 📂 Directory Layout
```text
backend/
├── app/
│   ├── main.py           # FastAPI entrypoint & middleware configuration
│   ├── routes/           # projects.py, upload.py, pipeline.py
│   ├── services/         # orchestrator.py (Job coordinator)
│   ├── models/           # schemas.py (Pydantic data models)
│   └── utils/            # logger.py, file_helpers.py
├── uploads/              # Incoming drone image staging (.gitkeep)
├── outputs/              # Stitched orthomosaics & GeoJSON exports (.gitkeep)
├── requirements.txt      # Python dependencies
└── README.md
```
