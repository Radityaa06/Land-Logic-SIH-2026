"""
GIS GeoJSON & Geometry Validator
Member 5: GIS & Georeferencing
Workspace: gis/
Branch: feature/gis-geojson

Validates polygon topology, ring closure, and GeoJSON compliance.
"""

from typing import Dict, Any, Tuple, List


def validate_geojson(geojson_doc: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a FeatureCollection according to RFC 7946 standards.
    Returns: (is_valid, error_messages)
    """
    errors = []

    if not isinstance(geojson_doc, dict):
        return False, ["Root GeoJSON must be a JSON object"]

    if geojson_doc.get("type") != "FeatureCollection":
        errors.append("Root type must be 'FeatureCollection'")

    features = geojson_doc.get("features")
    if not isinstance(features, list):
        errors.append("'features' must be an array")
        return False, errors

    coord_space = geojson_doc.get("coordinate_space")
    if coord_space not in ("geographic", "pixel"):
        errors.append("GeoJSON should explicitly declare coordinate_space as 'geographic' or 'pixel'")

    for idx, feat in enumerate(features):
        if feat.get("type") != "Feature":
            errors.append(f"Feature {idx} type must be 'Feature'")
            continue

        geom = feat.get("geometry")
        if not geom or geom.get("type") != "Polygon":
            errors.append(f"Feature {idx} geometry must be a Polygon")
            continue

        coords = geom.get("coordinates")
        if not coords or not isinstance(coords, list) or len(coords) == 0:
            errors.append(f"Feature {idx} has empty polygon coordinates")
            continue

        # Check ring closure
        exterior_ring = coords[0]
        if len(exterior_ring) < 4:
            errors.append(f"Feature {idx} ring has < 4 vertices")
        elif exterior_ring[0] != exterior_ring[-1]:
            errors.append(f"Feature {idx} ring is not closed (first vertex != last vertex)")

    return len(errors) == 0, errors
