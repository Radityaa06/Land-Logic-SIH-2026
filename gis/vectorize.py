"""
Mask Vectorization & Polygon Simplification
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Converts raster segmentation parcels into simplified polygon rings.
"""

from typing import List, Dict, Any, Tuple


def bbox_to_polygon_ring(bbox: List[int]) -> List[List[float]]:
    """
    Converts a [min_x, min_y, max_x, max_y] bounding box into a closed polygon ring.
    Coordinates are [x, y] format as required by GeoJSON specifications.
    """
    min_x, min_y, max_x, max_y = bbox
    return [
        [float(min_x), float(min_y)],
        [float(max_x), float(min_y)],
        [float(max_x), float(max_y)],
        [float(min_x), float(max_y)],
        [float(min_x), float(min_y)]  # Closing vertex
    ]


def simplify_ring(ring: List[List[float]], tolerance: float = 1.0) -> List[List[float]]:
    """
    Simple Douglas-Peucker reduction / vertex filter for polygon rings.
    """
    if len(ring) <= 5:
        return ring

    simplified = [ring[0]]
    for i in range(1, len(ring) - 1):
        prev = simplified[-1]
        curr = ring[i]
        dist = ((curr[0] - prev[0]) ** 2 + (curr[1] - prev[1]) ** 2) ** 0.5
        if dist >= tolerance:
            simplified.append(curr)

    simplified.append(ring[-1])
    return simplified
