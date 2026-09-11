"""
EXIF GPS and drone telemetry extractor
Member 5: GIS Engineer
(Maintained for backward compatibility; delegates to gis.exif)
"""

from gis.exif import extract_gps_coordinates

__all__ = ["extract_gps_coordinates"]

if __name__ == "__main__":
    coords = extract_gps_coordinates("sample.jpg")
    print(f"🗺️ [GIS Engine] Extracted Coordinates: {coords}")
