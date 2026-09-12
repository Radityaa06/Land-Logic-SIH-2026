"""
AI Post-Processing, Spectral Indices & Contour Extraction
Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration

Computes Visible Atmospherically Resistant Index (VARI), extracts individual parcel
contours via connected-component analysis, and formats predictions for downstream
consumption by Member 5 (GIS) and Member 2 (Pipeline).
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from ai.model import CLASS_LABEL_MAP

try:
    from scipy.ndimage import label, find_objects
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def compute_vari_index(rgb_image: np.ndarray) -> np.ndarray:
    """
    Visible Atmospherically Resistant Index (VARI)
    Formula: (Green - Red) / (Green + Red - Blue)

    Measures relative vegetation greenness/vitality using standard RGB drone sensors.
    Includes numerical stabilization to prevent divide-by-zero or sign-inversion spikes
    in deep shadows or high-blue water bodies.
    """
    r = rgb_image[:, :, 0].astype(np.float32)
    g = rgb_image[:, :, 1].astype(np.float32)
    b = rgb_image[:, :, 2].astype(np.float32)

    denom = g + r - b
    # Avoid zero division and near-zero instability with small signed epsilon
    epsilon = 1e-5
    denom = np.where(np.abs(denom) < epsilon, np.sign(denom + 1e-6) * epsilon, denom)

    vari = (g - r) / denom
    # Replace any non-finite entries resulting from edge-case calculations
    vari = np.nan_to_num(vari, nan=0.0, posinf=1.0, neginf=-1.0)
    return np.clip(vari, -1.0, 1.0)


def generate_dummy_land_mask(height: int, width: int) -> np.ndarray:
    """
    Generates a structured synthetic parcel mask (preserved for backward compatibility):
    1: Agricultural Land, 2: Bare Soil, 3: Forests, 5: Man-made Structures
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
    vari_map: Optional[np.ndarray] = None,
    min_area_pixels: int = 100
) -> List[Dict[str, Any]]:
    """
    Discovers individual connected parcel regions per land class using connected-component
    labeling. Computes pixel bounding boxes, grounded confidence scores, and mean VARI.

    Separates multiple distinct fields of the same class rather than merging them,
    and filters out edge-boundary noise and sub-threshold fragments.
    """
    h, w = mask.shape[:2]
    parcels: List[Dict[str, Any]] = []
    parcel_idx = 1

    unique_classes = np.unique(mask)
    for cls_id in unique_classes:
        if cls_id == 0:
            continue
        cls_name = CLASS_LABEL_MAP.get(int(cls_id), "unclassified")
        cls_binary = (mask == cls_id)

        if HAS_SCIPY:
            labeled, num_features = label(cls_binary)
            slices = find_objects(labeled)
            for comp_id, sl in enumerate(slices, 1):
                comp_pixels = (labeled == comp_id)
                pixel_count = int(np.sum(comp_pixels))
                if pixel_count < min_area_pixels:
                    continue

                min_y, max_y = int(sl[0].start), int(sl[0].stop - 1)
                min_x, max_x = int(sl[1].start), int(sl[1].stop - 1)

                mean_vari_val = (
                    float(np.mean(vari_map[comp_pixels]))
                    if vari_map is not None
                    else 0.0
                )

                # Grounded confidence scoring:
                # Base heuristic confidence 0.80, with bounded adjustment based on
                # spectral coherence (VARI agreement) and spatial size
                bbox_area = max(1, (max_y - min_y + 1) * (max_x - min_x + 1))
                fill_ratio = pixel_count / bbox_area  # compactness metric
                conf = 0.75 + min(0.15, fill_ratio * 0.15)
                # Agricultural land agreement check: higher confidence if positive VARI
                if cls_name == "agricultural_land" and mean_vari_val > 0.05:
                    conf += 0.05
                confidence = float(np.clip(conf, 0.55, 0.95))

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
        else:
            # Fallback if scipy is unavailable
            pixel_count = int(np.sum(cls_binary))
            if pixel_count < min_area_pixels:
                continue

            y_indices, x_indices = np.where(cls_binary)
            min_y, max_y = int(np.min(y_indices)), int(np.max(y_indices))
            min_x, max_x = int(np.min(x_indices)), int(np.max(x_indices))

            mean_vari_val = (
                float(np.mean(vari_map[cls_binary]))
                if vari_map is not None
                else 0.0
            )
            confidence = float(np.clip(0.80 + (pixel_count / (h * w)) * 0.1, 0.60, 0.90))

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

