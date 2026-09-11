"""
AI Post-Processing, Spectral Indices & Contour Extraction
Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration

Computes Visible Atmospherically Resistant Index (VARI), extracts parcel contours,
and formats predictions for downstream consumption by Member 5 (GIS).
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from ai.model import CLASS_LABEL_MAP


def compute_vari_index(rgb_image: np.ndarray) -> np.ndarray:
    """
    Visible Atmospherically Resistant Index (VARI)
    Formula: (Green - Red) / (Green + Red - Blue + 1e-6)
    Measures vegetation greenness using standard RGB drone cameras.
    """
    r = rgb_image[:, :, 0].astype(np.float32)
    g = rgb_image[:, :, 1].astype(np.float32)
    b = rgb_image[:, :, 2].astype(np.float32)

    denominator = g + r - b
    denominator[denominator == 0] = 1e-6

    vari = (g - r) / denominator
    return np.clip(vari, -1.0, 1.0)


def generate_dummy_land_mask(height: int, width: int) -> np.ndarray:
    """
    Generates a structured synthetic parcel mask (preserved from existing codebase):
    1: Agricultural Land, 2: Bare Soil, 3: Forests, 4: Water Bodies
    """
    mask = np.zeros((height, width), dtype=np.uint8)
    h_mid, w_mid = height // 2, width // 2
    mask[20:h_mid-20, 20:w_mid-20] = 1        # Field A: agricultural_land
    mask[20:h_mid-20, w_mid+20:width-20] = 3  # Field B: forests
    mask[h_mid+20:height-20, 20:w_mid-20] = 2 # Field C: barren_soil
    mask[h_mid+20:height-20, w_mid+20:width-20] = 5 # Field D: man_made_structures
    return mask


def extract_parcels_from_mask(
    mask: np.ndarray,
    vari_map: np.ndarray,
    min_area_pixels: int = 100
) -> List[Dict[str, Any]]:
    """
    Discovers connected parcels and regions per land class, estimating
    pixel bounding boxes, confidence, and mean VARI.
    """
    h, w = mask.shape[:2]
    parcels = []
    parcel_idx = 1

    unique_classes = np.unique(mask)
    for cls_id in unique_classes:
        if cls_id == 0:
            continue
        cls_name = CLASS_LABEL_MAP.get(int(cls_id), "unclassified")
        cls_pixels = (mask == cls_id)
        pixel_count = int(np.sum(cls_pixels))

        if pixel_count < min_area_pixels:
            continue

        # Compute bounding box in pixel space
        y_indices, x_indices = np.where(cls_pixels)
        min_y, max_y = int(np.min(y_indices)), int(np.max(y_indices))
        min_x, max_x = int(np.min(x_indices)), int(np.max(x_indices))

        mean_vari_val = float(np.mean(vari_map[cls_pixels])) if vari_map is not None else 0.0

        # Heuristic confidence based on area coherence
        confidence = float(np.clip(0.85 + (pixel_count / (h * w)) * 0.1, 0.80, 0.99))

        parcels.append({
            "parcel_id": f"parcel_{parcel_idx:02d}",
            "class": cls_name,
            "class_id": int(cls_id),
            "confidence": round(confidence, 2),
            "pixel_bbox": [min_x, min_y, max_x, max_y],
            "pixel_area": pixel_count,
            "mean_vari": round(mean_vari_val, 3)
        })
        parcel_idx += 1

    return parcels
