"""
Unit tests for Member 5: GIS & Georeferencing
"""

import os
import unittest
from gis.exif import extract_gps_coordinates
from gis.gsd import calculate_gsd
from gis.georeference import compute_world_file_params
from gis.vectorize import bbox_to_polygon_ring
from gis.geojson import generate_parcels_geojson
from gis.validate import validate_geojson


class TestGISModule(unittest.TestCase):
    def test_exif_no_fake_coordinates(self):
        # Must NOT fabricate coordinates when image doesn't exist
        coords = extract_gps_coordinates("non_existent_drone_frame.jpg")
        self.assertFalse(coords["has_gps"])
        self.assertEqual(coords["coordinate_space"], "pixel")
        self.assertNotIn("latitude", coords)
        self.assertNotIn("longitude", coords)

    def test_gsd_calculation(self):
        gsd = calculate_gsd(flight_height_m=120.0)
        self.assertIn("gsd_cm_per_px", gsd)
        self.assertGreater(gsd["gsd_cm_per_px"], 0)

    def test_pixel_space_geojson(self):
        sample_parcels = [
            {
                "parcel_id": "p01",
                "class": "agricultural_land",
                "confidence": 0.95,
                "pixel_bbox": [10, 20, 100, 150],
                "pixel_area": 11700,
                "crop_health": "healthy"
            }
        ]
        geojson_doc = generate_parcels_geojson(sample_parcels)
        self.assertEqual(geojson_doc["coordinate_space"], "pixel")
        self.assertEqual(len(geojson_doc["features"]), 1)
        self.assertEqual(geojson_doc["features"][0]["properties"]["crop_health"], "healthy")
        is_valid, errors = validate_geojson(geojson_doc)
        self.assertTrue(is_valid, f"Validation errors: {errors}")

    def test_geographic_space_geojson(self):
        sample_parcels = [
            {
                "parcel_id": "p02",
                "class": "forests",
                "confidence": 0.91,
                "pixel_bbox": [50, 50, 200, 200],
                "pixel_area": 22500,
                "crop_health": "moderate"
            }
        ]
        geo_ref = {
            "coordinate_space": "geographic",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "gsd_cm": 3.0
        }
        geojson_doc = generate_parcels_geojson(sample_parcels, geo_reference=geo_ref)
        self.assertEqual(geojson_doc["coordinate_space"], "geographic")
        self.assertEqual(len(geojson_doc["features"]), 1)
        self.assertEqual(geojson_doc["features"][0]["properties"]["crop_health"], "moderate")
        is_valid, errors = validate_geojson(geojson_doc)
        self.assertTrue(is_valid, f"Validation errors: {errors}")

    def test_geojson_crop_health_default_fallback(self):
        sample_parcels = [
            {
                "parcel_id": "p03",
                "class": "barren_soil",
                "confidence": 0.88,
                "pixel_bbox": [0, 0, 50, 50],
                "pixel_area": 2500
            }
        ]
        geojson_doc = generate_parcels_geojson(sample_parcels)
        self.assertEqual(geojson_doc["features"][0]["properties"]["crop_health"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
