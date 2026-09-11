# Land Logic DRONE-MAPPING-AI — API & Data Contract

**Base URL**: `http://localhost:8000` (API prefix: `/api/v1`)  
**Protocol**: HTTP/1.1 & WebSocket / SSE  
**Data Format**: JSON (`application/json`) and multipart/form-data for file uploads

---

## 1. Unified Pipeline Endpoint (Member 2 Coordinator)

This is the primary pipeline entrypoint connecting Member 1 / Member 6 to Member 2's backend orchestrator:

```text
Frontend  ──>  POST /predict  ──>  Backend
                                     │
                                     ├──> Member 4 (OpenCV Stitching)
                                     ├──> Member 3 (AI Segmentation & VARI)
                                     └──> Member 5 (GIS Georeferencing & GeoJSON)
                                     │
Frontend  <──  JSON Response   <─────┘
```

### 1.1 POST `/predict` (and `POST /api/v1/predict`)
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `files` *(optional)*: Array of binary drone image files (`.jpg`, `.jpeg`, `.png`, `.tiff`, `.dng`)
  - `project_id` *(optional)*: Existing project identifier to process buffered frames
- **Response** (`200 OK`):
  ```json
  {
    "status": "success",
    "message": "Pipeline completed successfully across OpenCV, AI, and GIS engines",
    "project_id": "proj_9f2a81b3",
    "coordinate_space": "geographic",
    "summary": {
      "image_count": 5,
      "mean_vari": 0.72,
      "detected_parcels": 4,
      "classes_detected": ["agricultural_land", "forests"]
    },
    "geojson": {
      "type": "FeatureCollection",
      "coordinate_space": "geographic",
      "features": [
        {
          "type": "Feature",
          "geometry": {
            "type": "Polygon",
            "coordinates": [
              [
                [-122.4194, 37.7749],
                [-122.4174, 37.7749],
                [-122.4174, 37.7735],
                [-122.4194, 37.7735],
                [-122.4194, 37.7749]
              ]
            ]
          },
          "properties": {
            "parcel_id": "parcel_01",
            "class": "agricultural_land",
            "confidence": 0.94,
            "mean_vari": 0.78,
            "pixel_area": 42000,
            "coordinate_space": "geographic"
          }
        }
      ]
    },
    "artifacts": {
      "stitched_image_url": "/api/v1/projects/proj_9f2a81b3/artifacts/stitched_orthomosaic.png",
      "mask_url": "/api/v1/projects/proj_9f2a81b3/artifacts/segmentation_mask.png",
      "geojson_url": "/api/v1/projects/proj_9f2a81b3/layers/parcels.geojson"
    }
  }
  ```

---

## 2. GeoJSON & Spatial Contract (CRITICAL)

Member 5 emits, and Member 6 consumes, standard RFC 7946 GeoJSON.

> [!CAUTION]
> **Coordinate Space Semantics**:
> - If genuine EXIF GPS exists on drone frames:  
>   `coordinate_space = "geographic"`  
>   Coordinates are standard `[longitude, latitude]` in EPSG:4326.
> - If genuine GPS is absent:  
>   `coordinate_space = "pixel"`  
>   Coordinates are `[pixel_x, pixel_y]` in raw image space.  
>   **Never fabricate GPS coordinates.**

---

## 3. Project Management Endpoints

### 3.1 Create Project
- **Method**: `POST /api/v1/projects`
- **Request Body**:
  ```json
  {
    "name": "Greenfield Farm Survey Alpha",
    "description": "High-altitude DJI drone flight",
    "target_crs": "EPSG:4326"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "project_id": "proj_8f3d1e92",
    "name": "Greenfield Farm Survey Alpha",
    "status": "CREATED",
    "created_at": "2026-09-11T18:00:00Z",
    "image_count": 0
  }
  ```

### 3.2 Get Project Status
- **Method**: `GET /api/v1/projects/{project_id}`
- **Response** (`200 OK`): `ProjectResponse` object.

---

## 4. Ingestion Endpoints

### 4.1 Upload Drone Images
- **Method**: `POST /api/v1/projects/{project_id}/upload`
- **Content-Type**: `multipart/form-data`
- **Files**: `files` parameter with image buffers.
- **Response** (`200 OK`): List of saved filenames, byte sizes, and status.

---

## 5. Pipeline & Job Monitoring Endpoints

### 5.1 Trigger Stitching Job
- **Method**: `POST /api/v1/projects/{project_id}/pipeline/stitch`
- **Request Body**: `{"feature_detector": "SIFT", "blend_mode": "MULTIBAND"}`
- **Response** (`202 Accepted`): `{"job_id": "job_...", "status": "QUEUED"}`

### 5.2 Query Job Status
- **Method**: `GET /api/v1/jobs/{job_id}`
- **Response** (`200 OK`): Returns `stage`, `status`, `progress_pct`, `message`, and `updated_at`.

---

## 6. Artifact & Layer Streaming

### 6.1 Download Artifact
- **Method**: `GET /api/v1/projects/{project_id}/artifacts/{filename}`
- **Response**: Binary stream with correct MIME type (`image/png`, `image/tiff`, `application/geo+json`).

### 6.2 Get Parcels GeoJSON
- **Method**: `GET /api/v1/projects/{project_id}/layers/parcels.geojson`
- **Response**: RFC 7946 FeatureCollection.
