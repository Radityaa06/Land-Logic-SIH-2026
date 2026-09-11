"""
Ground Sampling Distance (GSD) Estimator
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Computes spatial resolution in cm/pixel from drone flight height and camera parameters.
"""

from typing import Dict, Any


def calculate_gsd(
    flight_height_m: float,
    focal_length_mm: float = 8.8,
    sensor_width_mm: float = 13.2,
    sensor_height_mm: float = 8.8,
    image_width_px: int = 5472,
    image_height_px: int = 3648
) -> Dict[str, Any]:
    """
    Computes horizontal and vertical GSD:
    GSD = (flight_height_m * sensor_dimension_mm * 100) / (focal_length_mm * image_dimension_px)
    """
    if flight_height_m <= 0 or focal_length_mm <= 0:
        return {
            "gsd_cm_per_px": 2.5,
            "estimated": True,
            "note": "Default estimate; valid flight telemetry required for precision"
        }

    gsd_h = (flight_height_m * sensor_width_mm * 100.0) / (focal_length_mm * image_width_px)
    gsd_v = (flight_height_m * sensor_height_mm * 100.0) / (focal_length_mm * image_height_px)
    mean_gsd = (gsd_h + gsd_v) / 2.0

    return {
        "gsd_h_cm": round(gsd_h, 3),
        "gsd_v_cm": round(gsd_v, 3),
        "gsd_cm_per_px": round(mean_gsd, 3),
        "estimated": False
    }
