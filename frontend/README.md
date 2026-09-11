# Frontend & Geospatial Visualizer — Land Logic DRONE-MAPPING-AI

👨‍💻 **Owner**: Member 1 (Frontend Application Shell & UI/UX)  
🗺️ **Map Owner**: Member 6 (Interactive Leaflet Map — `frontend/src/components/map/`)  
🌿 **Assigned Branches**:
- Member 1: `feature/react-frontend`
- Member 6: `feature/leaflet-map`  
🛠️ **Tech Stack**: React 18, Vite, Leaflet, Lucide Icons, Modern CSS  
📁 **Workspace**: `frontend/`

---

## ⚠️ Critical Ownership Boundary Rule

```text
Member 1:
frontend/
└── everything EXCEPT:
    frontend/src/components/map/

Member 6:
frontend/src/components/map/
    ├── LeafletMap.jsx
    ├── FeaturePopup.jsx
    ├── LayerControl.jsx
    ├── Legend.jsx
    ├── RasterLayer.jsx
    └── map.css
```

---

## 🎯 Member 1 Scope & Responsibilities
1. **Application Shell & Navigation**: Header with project switcher, flight session chips, pipeline status indicator, theme support (`src/components/common/Header.jsx`).
2. **Drone Ingestion Upload Center**: Drag-and-drop batch file uploader with preview chips, validation, and upload status (`src/components/upload/UploadZone.jsx`).
3. **Pipeline Progress Visualizer**: Multi-stage progress tracking (Upload -> OpenCV Stitching -> AI Land Analysis -> GIS Georef -> Map Ready) (`src/components/common/PipelineStatus.jsx`).
4. **Analytics & Results Panel**: Land intelligence metrics cards for estimated acreage, vegetation coverage %, mean VARI/NDVI, and parcel count (`src/components/results/MetricsPanel.jsx`).
5. **API Client Integration**: Communicates with Member 2's backend orchestrator via `src/services/api.js`.

---

## 🎯 Member 6 Scope & Responsibilities (EXCLUSIVELY `components/map/`)
1. **Leaflet / Canvas Map Container**: Handles base map tiles, vector polygons, and responsive scaling (`src/components/map/LeafletMap.jsx`).
2. **Strict Spatial Truth**:
   - `coordinate_space === "geographic"`: Projects GeoJSON polygons onto WGS84 coordinates.
   - `coordinate_space === "pixel"`: Renders on calibrated 2D plane with clear pixel-space badge (never presents fake coordinates as real world).
3. **Layer Controls & Legend**: Dynamic toggle for base map, orthomosaic raster, parcel polygons, and vegetative heatmap (`LayerControl.jsx`, `Legend.jsx`).
4. **Interactive Feature Inspector**: Popup inspector displaying parcel class, confidence, area, and VARI (`FeaturePopup.jsx`).
5. **Raster Overlay**: Stitched composite display (`RasterLayer.jsx`).

---

## 📂 Directory Structure
```text
frontend/
├── src/
│   ├── components/
│   │   ├── upload/              ← MEMBER 1
│   │   │   └── UploadZone.jsx
│   │   ├── results/             ← MEMBER 1
│   │   │   └── MetricsPanel.jsx
│   │   ├── common/              ← MEMBER 1
│   │   │   ├── Header.jsx
│   │   │   └── PipelineStatus.jsx
│   │   └── map/                 ← EXCLUSIVELY MEMBER 6
│   │       ├── LeafletMap.jsx
│   │       ├── FeaturePopup.jsx
│   │       ├── LayerControl.jsx
│   │       ├── Legend.jsx
│   │       ├── RasterLayer.jsx
│   │       └── map.css
│   ├── pages/                   ← MEMBER 1
│   │   └── Dashboard.jsx
│   ├── services/                ← MEMBER 1
│   │   └── api.js
│   ├── App.jsx                  ← MEMBER 1
│   ├── main.jsx                 ← MEMBER 1
│   └── index.css                ← MEMBER 1
├── public/                      # Static assets
├── index.html                   # HTML entrypoint
├── vite.config.js               # Vite build config
├── package.json
└── README.md
```

---

## 🚀 Execution & Testing

```bash
cd frontend
npm install
npm run build    # Validates production bundle
npm run dev      # Starts local Vite development server
```
