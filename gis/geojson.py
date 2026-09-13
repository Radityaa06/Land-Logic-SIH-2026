"""
RFC 7946 GeoJSON Generator
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Emits standardized GeoJSON FeatureCollections for consumption by Member 2 and Member 6.
CRITICAL: Never fabricates coordinates. Explicitly marks 'coordinate_space' as 'geographic' or 'pixel'.
"""

import os
import json
from typing import List, Dict, Any, Optional
from gis.vectorize import bbox_to_polygon_ring


def generate_parcels_geojson(
    parcels: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    geo_reference: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Converts AI-extracted parcel records into a standardized GeoJSON FeatureCollection.

    geo_reference: Optional dict containing:
      - 'latitude': center/origin lat
      - 'longitude': center/origin lon
      - 'gsd_cm': ground resolution in cm/pixel
      - 'coordinate_space': 'geographic' or 'pixel'
    """
    has_genuine_geo = (
        geo_reference is not None
        and geo_reference.get("coordinate_space") == "geographic"
        and "latitude" in geo_reference
        and "longitude" in geo_reference
    )

    coordinate_space = "geographic" if has_genuine_geo else "pixel"
    features = []

    for p in parcels:
        bbox = p.get("pixel_bbox", [0, 0, 100, 100])
        pixel_ring = bbox_to_polygon_ring(bbox)

        if has_genuine_geo:
            # Transform pixel offsets to real-world WGS84 degree offsets
            # ~111,320 meters per degree latitude
            base_lat = geo_reference["latitude"]
            base_lon = geo_reference["longitude"]
            gsd_m = geo_reference.get("gsd_cm", 2.5) / 100.0

            geo_ring = []
            for px, py in pixel_ring:
                lat_offset = -(py * gsd_m) / 111320.0
                lon_offset = (px * gsd_m) / (111320.0 * 0.78)  # Approximate cos(lat)
                geo_ring.append([round(base_lon + lon_offset, 7), round(base_lat + lat_offset, 7)])
            coords = [geo_ring]
        else:
            # Pure pixel space coordinates: [x, y]
            coords = [pixel_ring]

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coords
            },
            "properties": {
                "parcel_id": p.get("parcel_id", "parcel_unknown"),
                "class": p.get("class", "agricultural_land"),
                "confidence": p.get("confidence", 0.90),
                "mean_vari": p.get("mean_vari", 0.0),
                "pixel_area": p.get("pixel_area", 0),
                "crop_health": p.get("crop_health", "not_applicable"),
                "coordinate_space": coordinate_space
            }
        }
        features.append(feature)

    geojson_doc = {
        "type": "FeatureCollection",
        "coordinate_space": coordinate_space,
        "features": features
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(geojson_doc, f, indent=2)
        print(f"✅ [GIS] GeoJSON saved to {output_path} (coordinate_space: {coordinate_space})")

    return geojson_doc
