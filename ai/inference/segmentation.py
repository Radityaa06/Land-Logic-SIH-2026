"""
Segmentation and NDVI/VARI mathematical routines
"""

import numpy as np


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
    Generates a structured synthetic parcel mask (0: Background, 100: Crop, 200: Bare soil)
    """
    mask = np.zeros((height, width), dtype=np.uint8)
    # Split into 4 distinct agricultural quadrangles
    h_mid, w_mid = height // 2, width // 2
    mask[20:h_mid-20, 20:w_mid-20] = 100        # Field A: Healthy Crop
    mask[20:h_mid-20, w_mid+20:width-20] = 150  # Field B: Water Stress
    mask[h_mid+20:height-20, 20:w_mid-20] = 200 # Field C: Harvested / Bare Soil
    mask[h_mid+20:height-20, w_mid+20:width-20] = 250 # Field D: High Density
    return mask
