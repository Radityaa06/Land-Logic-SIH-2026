# GIS & Georeferencing — Land Logic DRONE-MAPPING-AI

🗺️ **Owner**: Member 5  
🌿 **Assigned Branch**: `feature/gis-geojson`  
🛠️ **Tech Stack**: GDAL, Rasterio, GeoPandas, Shapely, PyProj, ExifRead  
📁 **Workspace**: `gis/`

---

## 🎯 Scope & Responsibilities
1. **EXIF GPS Extraction**: Reads latitude, longitude, and flight altitude tags from raw drone imagery (`gis/exif.py`).
2. **Strict Spatial Truth (CRITICAL)**:
   - Never fabricates coordinates.
   - If genuine GPS is unavailable, sets `coordinate_space = "pixel"` and preserves pixel coordinates.
   - If genuine GPS is available, sets `coordinate_space = "geographic"`.
3. **Ground Sample Distance (GSD)**: Calculates the physical ground dimension represented by each pixel based on altitude and focal length (`gis/gsd.py`).
4. **World Files & Georeferencing**: Emits 2D affine transformation matrices and ESRI world files (`gis/georeference.py`).
5. **Vector Polygonization**: Converts AI raster predictions into simplified polygon rings (`gis/vectorize.py`).
6. **RFC 7946 GeoJSON Generation**: Emits standardized GeoJSON FeatureCollections consumed by Member 2 (Backend) and Member 6 (Leaflet Map) (`gis/geojson.py`). Feature properties include `parcel_id`, `class`, `confidence`, `mean_vari`, `pixel_area`, `crop_health` (`healthy`, `moderate`, `stressed`, `not_applicable`), and `coordinate_space`.
7. **Coordinate Transformations & Validation**: Projects across WGS84, Web Mercator, and validates topology (`gis/transform.py`, `gis/validate.py`).

---

## 📂 Directory Structure
```text
gis/
├── exif.py               # EXIF GPS extraction & telemetry (no fabricated GPS)
├── gsd.py                # Ground Sampling Distance (GSD) estimator
├── georeference.py       # World file generation & affine matrix calculation
├── vectorize.py          # Polygon ring creation & simplification
├── geojson.py            # RFC 7946 GeoJSON generator (pixel / geographic)
├── transform.py          # Coordinate conversions (WGS84 / Web Mercator)
├── validate.py           # GeoJSON FeatureCollection validation
├── tests/
│   └── test_gis.py       # Unit test suite for GIS modules
├── geo_processing/
│   └── geotag_extractor.py # Backward-compatibility wrapper
├── layers/
│   └── geojson_gen.py      # Backward-compatibility wrapper
├── requirements.txt      # Geospatial dependencies
└── README.md
```

---

## 🚀 Execution & Testing

```bash
# Run unit tests
python3 -m unittest gis/tests/test_gis.py

# Run standalone parcel generator
python3 -m gis.geojson
```
