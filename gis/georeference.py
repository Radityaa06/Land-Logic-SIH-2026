"""
Georeferencing & World File Generator
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Calculates 2D affine transformation matrices and emits ESRI World Files (.tfw / .pgw).
Respects coordinate_space mode strictly.
"""

from typing import Dict, Any, Optional, Tuple


def compute_world_file_params(
    top_left_coord: Optional[Tuple[float, float]],
    pixel_size_x: float,
    pixel_size_y: float,
    rotation_x: float = 0.0,
    rotation_y: float = 0.0
) -> Optional[str]:
    """
    Constructs a 6-line ESRI World File content:
    Line 1: Pixel X dimension (size)
    Line 2: Rotation term Y
    Line 3: Rotation term X
    Line 4: Negative Pixel Y dimension (size)
    Line 5: Top-left pixel center X (e.g. Longitude or pixel X)
    Line 6: Top-left pixel center Y (e.g. Latitude or pixel Y)
    """
    if top_left_coord is None:
        return None

    tl_x, tl_y = top_left_coord
    lines = [
        f"{pixel_size_x:.10f}",
        f"{rotation_y:.10f}",
        f"{rotation_x:.10f}",
        f"{-abs(pixel_size_y):.10f}",
        f"{tl_x:.10f}",
        f"{tl_y:.10f}"
    ]
    return "\n".join(lines) + "\n"
