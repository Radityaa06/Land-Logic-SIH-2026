"""
Coordinate Reference System (CRS) Transformation
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Transforms between WGS84 (EPSG:4326), Web Mercator (EPSG:3857), and pixel coordinates.
"""

import math
from typing import Tuple


def wgs84_to_web_mercator(lon: float, lat: float) -> Tuple[float, float]:
    """
    Projects WGS84 (lat/lon in degrees) to Spherical Web Mercator (EPSG:3857 in meters).
    """
    x = lon * 20037508.34 / 180.0
    y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * 20037508.34 / 180.0
    return x, y


def web_mercator_to_wgs84(x: float, y: float) -> Tuple[float, float]:
    """
    Unprojects Web Mercator (meters) back to WGS84 (degrees).
    """
    lon = (x / 20037508.34) * 180.0
    lat = (y / 20037508.34) * 180.0
    lat = 180.0 / math.pi * (2.0 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return lon, lat
