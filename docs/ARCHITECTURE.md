# Land Logic DRONE-MAPPING-AI — System Architecture

## 1. Executive Summary
Land Logic DRONE-MAPPING-AI is an end-to-end aerial processing and geospatial artificial intelligence platform. It transforms unstitched, high-resolution drone flight photos into georeferenced orthomosaics, analyzes land parcels using computer vision models (crop health, land boundary delineation, vegetative coverage), and delivers interactive vector and raster layers via a modern web interface.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                👨‍💻 CLIENT LAYER (Member 1)                          |
|                                                                                   |
|  [React + Vite / Next.js SPA]                                                     |
|  - Multi-File Drone Imagery Dropzone (Chunked Uploads)                            |
|  - Interactive Mapbox GL / Leaflet Vector Layer Visualizer                        |
|  - Real-Time Job Progress Tracker (Server-Sent Events / WebSockets)               |
|  - Land Analytics Dashboard (NDVI Heatmaps, Area Estimation, Polygon Inspections) |
+------------------------------------------+----------------------------------------+
                                           |
                              HTTP / REST & WebSocket
                                           v
+-----------------------------------------------------------------------------------+
|                               ⚙️ API GATEWAY & ORCHESTRATOR (Member 2)            |
|                                                                                   |
|  [FastAPI Backend Engine]                                                         |
|  - Routes: /api/v1/projects, /upload, /pipeline/stitch, /pipeline/ai, /export     |
|  - Job Queue & Background Task Dispatcher                                         |
|  - File Staging System: uploads/ & outputs/ storage management                    |
|  - Pipeline Orchestrator coordinating OpenCV, AI, and GIS execution               |
+------------+-----------------------------+-----------------------------+----------+
             |                             |                             |
             v                             v                             v
+------------------------+   +------------------------+   +-------------------------+
|    👁️ OPENCV ENGINE    |   |     🤖 AI/ML ENGINE    |   |       🗺️ GIS ENGINE     |
|       (Member 4)       |   |       (Member 3)       |   |        (Member 5)       |
|                        |   |                        |   |                         |
| - Lens & Color Balance |   | - Semantic Segmentation|   | - EXIF GPS Parsing      |
| - SIFT/ORB Keypoints   |   |   (UNet / YOLOv8-Seg)  |   | - Ground Sample Distance|
| - RANSAC Homography    |   | - Crop Health / NDVI   |   | - GeoTIFF Georeferencing|
| - Multi-Band Blending  |   | - Boundary Detection   |   | - CRS Projection        |
| - Orthomosaic Assembly |   | - Anomaly & Weed Class.|   | - GeoJSON Layer Gen     |
+------------+-----------+   +------------+-----------+   +-------------+-----------+
             \                             |                             /
              \____________________________|____________________________/
                                           |
                                           v
                     +-------------------------------------------+
                     |             📦 ARTIFACT STORAGE           |
                     |  - raw_images/ (Uploaded JPGs/DNGs)       |
                     |  - stitched/ (High-Res Composite PNG)     |
                     |  - georeferenced/ (GeoTIFF EPSG:4326/3857)|
                     |  - vectors/ (Exportable GeoJSON & SHP)    |
                     +-------------------------------------------+
```

---

## 3. End-to-End Pipeline Data Flow

1. **Ingestion**:
   - The user drops 10–100+ raw drone images (with embedded EXIF GPS tags) onto the frontend uploader.
   - The FastAPI backend buffers files into `backend/uploads/{project_id}/`.

2. **Phase 1: Metadata Extraction & Verification (GIS - Member 5)**:
   - GIS engine extracts flight altitude, focal length, sensor dimensions, and latitude/longitude coordinates from each image header.
   - Calculates spatial bounding envelope and validates adequate flight overlap (minimum 60% forward, 40% lateral).

3. **Phase 2: Orthomosaic Stitching (OpenCV - Member 4)**:
   - Preprocessing: Vignetting correction, histogram equalization.
   - Feature Detection: SIFT/ORB feature point extraction and descriptor matching.
   - Homography & Warping: Pairwise perspective transformation matrices calculated via RANSAC.
   - Seamline selection and multiband blend to produce a seamless aerial composite image.

4. **Phase 3: AI Inference & Land Segmentation (AI - Member 3)**:
   - The stitched composite is tiled into standard model chips (e.g., 512x512 or 1024x1024).
   - Semantic segmentation models segment agricultural fields, roads, waterways, and structures.
   - NDVI / spectral index calculation estimates vegetative vigor and anomalies.
   - Reassembly of model prediction masks into full-resolution raster overlays.

5. **Phase 4: Georeferencing & Vector Generation (GIS - Member 5)**:
   - Associates pixel coordinates with real-world spatial coordinates using Ground Control Points (GCPs) or flight trajectory bounding boxes.
   - Exports georeferenced GeoTIFF (EPSG:4326 / EPSG:3857).
   - Converts segmentation raster boundaries into optimized GeoJSON polygon features with area calculations in hectares/acres.

6. **Phase 5: Visualization & Export (Frontend - Member 1)**:
   - GeoTIFF served as slippy map tiles or raster overlay.
   - GeoJSON polygons rendered as interactive layers with color-coded classification attributes.
   - Real-time statistics displayed (total arable area, vegetation health index, water surface percentage).

---

## 4. Hardware & Scaling Considerations
- **Memory Optimization**: Tiled processing pipeline ensures large gigapixel orthomosaics can be processed on systems with 16GB–32GB RAM without OOM crashes.
- **GPU Acceleration**: AI inference and OpenCV CUDA modules are dynamically enabled when an NVIDIA CUDA device is detected; falls back gracefully to multi-core CPU.
