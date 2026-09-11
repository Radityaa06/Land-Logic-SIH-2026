# Land Logic DRONE-MAPPING-AI — System Architecture (6-Member Modular System)

## 1. Executive Summary
Land Logic DRONE-MAPPING-AI is an end-to-end aerial processing and geospatial artificial intelligence platform designed for the Smart India Hackathon (SIH 2026). It transforms unstitched drone flight photos into georeferenced orthomosaics, analyzes land parcels using computer vision models (crop health, land boundary delineation, vegetative coverage), and delivers interactive vector and raster layers via a modern web interface.

The system is partitioned into **6 distinct member roles** with strict ownership boundaries and clean interface contracts.

---

## 2. High-Level Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                                👨‍💻 CLIENT LAYER (Member 1)                          |
|                                                                                   |
|  [React 18 + Vite SPA]                                                            |
|  - Drag-and-Drop Batch Drone Ingestion (Validation & Previews)                    |
|  - Real-Time Pipeline Progress Visualizer (Upload -> OpenCV -> AI -> GIS -> Map)  |
|  - Land Intelligence Dashboard (VARI/NDVI Heatmaps, Area Estimation, Parcel Stats)|
+------------------------------------------+----------------------------------------+
                                           |
                              POST /predict (Multipart Batch)
                                           v
+-----------------------------------------------------------------------------------+
|                     ⚙️ CENTRAL PIPELINE ORCHESTRATOR (Member 2)                    |
|                                                                                   |
|  [FastAPI Backend Gateway]                                                        |
|  - Endpoints: /predict, /api/v1/projects, /upload, /jobs/{id}, /artifacts/{name}   |
|  - Modular Pipeline Coordinator executing OpenCV, AI, and GIS sequentially        |
|  - Artifact Server & MIME Streaming: PNG orthophotos, GeoJSON, and GeoTIFFs       |
|  - Session Store & Background Task Execution                                      |
+------------+-----------------------------+-----------------------------+----------+
             |                             |                             |
             v                             v                             v
+------------------------+   +------------------------+   +-------------------------+
|    👁️ OPENCV ENGINE    |   |     🤖 AI/ML ENGINE    |   |       🗺️ GIS ENGINE     |
|       (Member 4)       |   |       (Member 3)       |   |        (Member 5)       |
|                        |   |                        |   |                         |
| - Preprocessing & CLAHE|   | - 5-Class Segmentation |   | - Genuine EXIF GPS Parse|
| - Blur/Quality Audit   |   |   (Agricultural, Soil, |   | - GSD Spatial Resolution|
| - SIFT/ORB Keypoints   |   |    Forest, Water, Road)|   | - Affine Georeferencing |
| - Pairwise Homography  |   | - VARI Greenness Index |   | - World Files (.tfw)    |
| - Feather Blending     |   | - Sliding-Window 512px |   | - RFC 7946 GeoJSON Gen  |
| - Stitched Orthomosaic |   | - Structured Parcels   |   | - Strict coordinate_spc |
+------------+-----------+   +------------+-----------+   +-------------+-----------+
             \                             |                             /
              \____________________________|____________________________/
                                           |
                                           v
                 +---------------------------------------------------+
                 |        🗺️ LEAFLET / INTERACTIVE MAP (Member 6)    |
                 |      Workspace: frontend/src/components/map/      |
                 |                                                   |
                 |  - Dual Coordinate Space Canvas                   |
                 |    * Geographic Mode (WGS84 GPS Leaflet tiles)    |
                 |    * Pixel Space Mode (Preserved Drone Coords)    |
                 |  - Color-Coded Land Class Polygons                |
                 |  - Interactive FeaturePopup Inspector             |
                 |  - Layer Controls (Satellite, Ortho, Parcels)     |
                 |  - Stitched Mosaic RasterLayer Overlay            |
                 +---------------------------------------------------+
```

---

## 3. End-to-End Pipeline Data Flow

1. **Ingestion (Member 1 $\rightarrow$ Member 2)**:
   - The user selects or drops drone flight imagery in `UploadZone.jsx`.
   - Member 1 transmits the images via `api.predictDirect()` to Member 2's `POST /predict`.

2. **Phase 1: Orthomosaic Stitching (Member 4 — OpenCV)**:
   - Validates frame sharpness (Laplacian variance) and normalizes illumination via CLAHE.
   - Extracts SIFT/ORB keypoints and computes perspective homography matrices with RANSAC.
   - Blends seams using feather blending, generating a composite orthomosaic image.

3. **Phase 2: Land-Use & Crop Health Analysis (Member 3 — AI Engine)**:
   - Chunks large aerial mosaics into 512x512 tiles with overlap (`ai/tiling.py`).
   - Classifies land into 5 canonical categories:
     1. `agricultural_land`
     2. `barren_soil`
     3. `forests`
     4. `water_bodies`
     5. `man_made_structures`
   - Computes Visible Atmospherically Resistant Index (`VARI = (G - R) / (G + R - B)`).
   - Emits structured parcel prediction records for Member 5.

4. **Phase 3: Georeferencing & Vector Generation (Member 5 — GIS)**:
   - Parses genuine EXIF tags. If GPS is absent, explicitly marks `coordinate_space = "pixel"`. Never fabricates GPS coordinates.
   - Calculates Ground Sampling Distance (GSD) from flight height and camera sensor geometry.
   - Converts AI prediction bounding boxes into RFC 7946 GeoJSON polygon rings.

5. **Phase 4: Map Visualization (Member 6 — Leaflet Map)**:
   - Member 6's `LeafletMap.jsx` receives GeoJSON data and raster overlays from Member 2.
   - Automatically detects coordinate space: renders onto satellite basemap if geographic, or onto calibrated 2D plane if pixel space.
   - Allows interactive click inspection via `FeaturePopup.jsx` and layer toggling via `LayerControl.jsx`.

6. **Phase 5: Analytics & Metrics Display (Member 1 — Frontend)**:
   - Summarizes calculated survey area (hectares), vegetation vigor %, mean VARI, and detected parcel counts in `MetricsPanel.jsx`.

---

## 4. Hardware & Scaling Considerations
- **Tiled Processing**: 512x512 sliding window prevents Out-Of-Memory (OOM) errors on large gigapixel images.
- **Graceful Fallbacks**: Every module operates with pure Python and heuristic fallbacks if external native packages (OpenCV, GDAL) are missing.
