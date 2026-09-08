# Land Logic DRONE-MAPPING-AI — API Contract

**Base URL**: `http://localhost:8000/api/v1`  
**Protocol**: HTTP/1.1 & WebSocket / SSE for progress streaming  
**Data Format**: JSON (application/json) and multipart/form-data for file uploads

---

## 1. Project Management Endpoints

### 1.1 Create Project
- **Method**: `POST /projects`
- **Description**: Initializes a new mapping project session.
- **Request Body**:
  ```json
  {
    "name": "Greenfield Farm Survey Alpha",
    "description": "High-altitude DJI Mavic 3 survey for corn crop health & parcel boundaries",
    "target_crs": "EPSG:4326"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "project_id": "proj_8f3d1e92",
    "name": "Greenfield Farm Survey Alpha",
    "status": "CREATED",
    "created_at": "2026-09-08T14:30:00Z",
    "image_count": 0
  }
  ```

### 1.2 Get Project Status & Summary
- **Method**: `GET /projects/{project_id}`
- **Response** (`200 OK`):
  ```json
  {
    "project_id": "proj_8f3d1e92",
    "name": "Greenfield Farm Survey Alpha",
    "status": "COMPLETED",
    "image_count": 42,
    "artifacts": {
      "stitched_ortho_url": "/api/v1/projects/proj_8f3d1e92/artifacts/ortho.png",
      "geotiff_url": "/api/v1/projects/proj_8f3d1e92/artifacts/ortho.tif",
      "geojson_url": "/api/v1/projects/proj_8f3d1e92/artifacts/parcels.geojson"
    },
    "metrics": {
      "total_area_hectares": 12.45,
      "vegetation_coverage_pct": 78.2,
      "mean_ndvi": 0.68
    }
  }
  ```

---

## 2. Ingestion Endpoints

### 2.1 Upload Drone Images
- **Method**: `POST /projects/{project_id}/upload`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `files`: Array of binary image files (`.jpg`, `.jpeg`, `.png`, `.dng`)
- **Response** (`200 OK`):
  ```json
  {
    "project_id": "proj_8f3d1e92",
    "uploaded_files": [
      {
        "filename": "DJI_0041.JPG",
        "size_bytes": 8420110,
        "has_gps": true,
        "lat": 37.774929,
        "lon": -122.419416,
        "altitude_m": 120.4
      }
    ],
    "total_uploaded": 42,
    "status": "READY_FOR_PROCESSING"
  }
  ```

---

## 3. Pipeline Execution Endpoints

### 3.1 Start Stitching (OpenCV)
- **Method**: `POST /projects/{project_id}/pipeline/stitch`
- **Request Body**:
  ```json
  {
    "feature_detector": "SIFT",
    "blend_mode": "MULTIBAND",
    "downscale_factor": 1.0,
    "confidence_threshold": 0.65
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "job_id": "job_stitch_9182",
    "project_id": "proj_8f3d1e92",
    "stage": "STITCHING",
    "status": "QUEUED"
  }
  ```

### 3.2 Run AI Land Analysis
- **Method**: `POST /projects/{project_id}/pipeline/ai-analyze`
- **Request Body**:
  ```json
  {
    "tasks": ["land_use_segmentation", "crop_health_ndvi", "boundary_extraction"],
    "confidence_threshold": 0.50,
    "tile_size": 512
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "job_id": "job_ai_3310",
    "project_id": "proj_8f3d1e92",
    "stage": "AI_INFERENCE",
    "status": "QUEUED"
  }
  ```

### 3.3 Run Georeferencing (GIS)
- **Method**: `POST /projects/{project_id}/pipeline/georeference`
- **Request Body**:
  ```json
  {
    "target_crs": "EPSG:4326",
    "export_format": "GeoTIFF",
    "generate_contours": true,
    "contour_interval_m": 2.0
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "job_id": "job_gis_5521",
    "project_id": "proj_8f3d1e92",
    "stage": "GEOREFERENCING",
    "status": "QUEUED"
  }
  ```

---

## 4. Job Status & Real-Time Monitoring

### 4.1 Query Job Status
- **Method**: `GET /jobs/{job_id}`
- **Response** (`200 OK`):
  ```json
  {
    "job_id": "job_stitch_9182",
    "stage": "STITCHING",
    "status": "IN_PROGRESS",
    "progress_pct": 64.5,
    "message": "Blending seamlines across frame 28/42",
    "updated_at": "2026-09-08T14:34:12Z"
  }
  ```

### 4.2 Stream Pipeline Events (Server-Sent Events)
- **Method**: `GET /projects/{project_id}/events`
- **Headers**: `Accept: text/event-stream`
- **Event Schema**:
  ```
  event: pipeline_update
  data: {"stage": "AI_INFERENCE", "progress": 82.0, "step": "Segmenting crop polygons"}
  ```

---

## 5. Artifact & Layer Export Endpoints

### 5.1 Download GeoJSON Polygons
- **Method**: `GET /projects/{project_id}/layers/parcels.geojson`
- **Response**: Standard RFC 7946 FeatureCollection GeoJSON.
  ```json
  {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-122.419, 37.774], [-122.418, 37.774], [-122.418, 37.773], [-122.419, 37.773], [-122.419, 37.774]]]
        },
        "properties": {
          "id": "parcel_01",
          "class": "healthy_crop",
          "area_sq_m": 10540.2,
          "mean_ndvi": 0.74
        }
      }
    ]
  }
  ```

### 5.2 Download Georeferenced Orthomosaic (GeoTIFF)
- **Method**: `GET /projects/{project_id}/layers/orthomosaic.tif`
- **Response**: Binary stream (`image/tiff`).
