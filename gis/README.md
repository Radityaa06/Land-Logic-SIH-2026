# GIS & Georeferencing — Land Logic DRONE-MAPPING-AI

🗺️ **Owner**: Member 5  
**Tech Stack**: GDAL, Rasterio, GeoPandas, Shapely, PyProj, ExifRead

---

## 🎯 Scope & Responsibilities
1. **EXIF GPS Extraction**: Reads latitude, longitude, and flight altitude tags directly from drone image metadata.
2. **Ground Sample Distance (GSD)**: Calculates the physical ground dimension represented by each image pixel (e.g. 2.5 cm/pixel).
3. **GeoTIFF Generation**: Applies spatial affine transformations and projects stitched composites into standard coordinate reference systems (EPSG:4326 / EPSG:3857).
4. **Vector Polygonization**: Converts AI raster masks into simplified GeoJSON polygons with computed area attributes (hectares / acres).

---

## 🚀 Quickstart

```bash
cd gis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run GeoJSON parcel generator
python layers/geojson_gen.py --input ../shared/sample_outputs/segmentation_mask.png --output ../shared/sample_outputs/parcels.geojson
```

---

## 📂 Directory Layout
```text
gis/
├── geo_processing/
│   └── geotag_extractor.py # EXIF GPS & telemetry extraction
├── layers/
│   └── geojson_gen.py      # Raster polygonizer & GeoJSON generator
├── requirements.txt        # Geospatial dependencies
└── README.md
```
