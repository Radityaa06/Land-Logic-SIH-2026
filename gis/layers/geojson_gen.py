"""
Raster-to-Vector GeoJSON polygon generator
Member 5: GIS Engineer
(Maintained for backward compatibility; delegates to gis.geojson)
"""

import argparse
from gis.geojson import generate_parcels_geojson


def generate_legacy_parcels_geojson(mask_path: str, output_path: str, base_lat: float = 37.7749, base_lon: float = -122.4194):
    """
    Adapter wrapper matching legacy signature.
    """
    mock_parcels = [
        {
            "parcel_id": "field_sector_01",
            "class": "agricultural_land",
            "confidence": 0.94,
            "mean_vari": 0.78,
            "pixel_bbox": [20, 20, 220, 220],
            "pixel_area": 40000
        },
        {
            "parcel_id": "field_sector_02",
            "class": "forests",
            "confidence": 0.88,
            "mean_vari": 0.52,
            "pixel_bbox": [240, 20, 440, 220],
            "pixel_area": 40000
        }
    ]
    geo_ref = {
        "coordinate_space": "geographic",
        "latitude": base_lat,
        "longitude": base_lon,
        "gsd_cm": 2.5
    }
    return generate_parcels_geojson(mock_parcels, output_path=output_path, geo_reference=geo_ref)


__all__ = ["generate_parcels_geojson", "generate_legacy_parcels_geojson"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../shared/sample_outputs/segmentation_mask.png")
    parser.add_argument("--output", default="../shared/sample_outputs/parcels.geojson")
    args = parser.parse_args()

    generate_legacy_parcels_geojson(args.input, args.output)
