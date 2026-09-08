"""
EXIF GPS and drone telemetry extractor
Member 5: GIS Engineer
"""

import os
import exifread


def extract_gps_coordinates(image_path: str) -> dict:
    """
    Extracts latitude, longitude, and altitude from image EXIF metadata
    """
    if not os.path.exists(image_path):
        # Return fallback mock coordinates for development testing
        return {
            "has_gps": True,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "altitude_m": 120.0,
            "source": "MOCK_FALLBACK"
        }

    with open(image_path, "rb") as f:
        tags = exifread.process_file(f, details=False)

    lat_tag = tags.get("GPS GPSLatitude")
    lat_ref = tags.get("GPS GPSLatitudeRef")
    lon_tag = tags.get("GPS GPSLongitude")
    lon_ref = tags.get("GPS GPSLongitudeRef")
    alt_tag = tags.get("GPS GPSAltitude")

    if not (lat_tag and lon_tag):
        return {"has_gps": False, "source": "NO_EXIF_GPS"}

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
        "latitude": lat,
        "longitude": lon,
        "altitude_m": alt,
        "source": "EXIF"
    }


if __name__ == "__main__":
    coords = extract_gps_coordinates("sample.jpg")
    print(f"🗺️ [GIS Engine] Extracted Coordinates: {coords}")
