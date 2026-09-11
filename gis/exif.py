"""
EXIF Metadata & Telemetry Parser
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Extracts real drone GPS coordinates (lat, lon, altitude) and camera metadata from image EXIF.
CRITICAL: Never fabricates coordinates. If genuine GPS is absent, sets coordinate_space = 'pixel'.
"""

import os
from typing import Dict, Any, Optional

try:
    import exifread
except ImportError:
    exifread = None


def extract_gps_coordinates(image_path: str) -> Dict[str, Any]:
    """
    Extracts genuine GPS coordinates from EXIF metadata.
    Returns dictionary with explicit 'coordinate_space' ('geographic' or 'pixel').
    """
    if not os.path.exists(image_path) or exifread is None:
        return {
            "has_gps": False,
            "coordinate_space": "pixel",
            "source": "NO_EXIF_GPS" if exifread else "EXIFREAD_UNAVAILABLE"
        }

    try:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        lat_tag = tags.get("GPS GPSLatitude")
        lat_ref = tags.get("GPS GPSLatitudeRef")
        lon_tag = tags.get("GPS GPSLongitude")
        lon_ref = tags.get("GPS GPSLongitudeRef")
        alt_tag = tags.get("GPS GPSAltitude")

        if not (lat_tag and lon_tag):
            return {
                "has_gps": False,
                "coordinate_space": "pixel",
                "source": "NO_EXIF_GPS"
            }

        def _convert_to_degrees(value):
            d = float(value.values[0].num) / float(value.values[0].den)
            m = float(value.values[1].num) / float(value.values[1].den)
            s = float(value.values[2].num) / float(value.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)

        lat = _convert_to_degrees(lat_tag)
        if str(lat_ref) != "N":
            lat = -lat

        lon = _convert_to_degrees(lon_tag)
        if str(lon_ref) != "E":
            lon = -lon

        alt = 0.0
        if alt_tag:
            alt = float(alt_tag.values[0].num) / float(alt_tag.values[0].den)

        return {
            "has_gps": True,
            "coordinate_space": "geographic",
            "latitude": round(lat, 7),
            "longitude": round(lon, 7),
            "altitude_m": round(alt, 2),
            "source": "EXIF"
        }
    except Exception as exc:
        return {
            "has_gps": False,
            "coordinate_space": "pixel",
            "source": f"EXIF_ERROR: {str(exc)}"
        }
