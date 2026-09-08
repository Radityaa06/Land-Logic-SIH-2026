# Frontend — Land Logic DRONE-MAPPING-AI

👨‍💻 **Owner**: Member 1  
**Tech Stack**: React 18 / Vite, Mapbox GL JS / Leaflet, Lucide Icons, Modern CSS

---

## 🎯 Scope & Responsibilities
1. **Interactive Geospatial Map Viewer**: Display high-res aerial orthomosaic rasters alongside vector GeoJSON polygons for fields and boundaries.
2. **Batch Upload Zone**: User-friendly drag-and-drop interface for uploading high-resolution drone flight imagery.
3. **Pipeline Progress Monitor**: Real-time status display showing OpenCV stitching, AI segmentation, and GIS georeferencing status.
4. **Land Intelligence Metrics**: Interactive analytics card displaying calculated acreage, vegetation vigor (NDVI), and land parcel inspection details.

---

## 🚀 Quickstart

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env

# 3. Start local development server
npm run dev
```

---

## 📂 Directory Layout
```text
frontend/
├── public/               # Static icons, markers, and favicon
├── src/
│   ├── components/       # UI components (MapView, UploadZone, MetricsPanel)
│   └── services/         # API abstraction & WebSocket connection (api.js)
├── package.json          # Node dependencies & build scripts
└── README.md
```
