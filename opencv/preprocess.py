"""
OpenCV Image Preprocessing
Member 4: Computer Vision / OpenCV Engineer
Workspace: opencv/
Branch: feature/opencv

Provides EXIF-orientation normalization, CLAHE exposure balancing,
image quality auditing, and safe input ingestion.
"""

import os
from typing import Tuple, Optional, Union
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None


def correct_exif_orientation(image_input: Union[str, np.ndarray]) -> np.ndarray:
    """
    Normalizes camera rotation using EXIF orientation tags so drone flight frames
    share a consistent upright orientation before feature extraction.
    Returns: BGR numpy array (dtype=uint8).
    """
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise ValueError(f"Image file does not exist: '{image_input}'")

        if Image is not None and ImageOps is not None:
            try:
                with Image.open(image_input) as pil_img:
                    # Normalizes EXIF rotation tag (1-8) to canonical orientation
                    transposed = ImageOps.exif_transpose(pil_img)
                    rgb_arr = np.array(transposed.convert("RGB"), dtype=np.uint8)
                    # Convert PIL RGB to OpenCV BGR color ordering
                    return cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR) if cv2 is not None else rgb_arr[..., ::-1].copy()
            except Exception:
                pass

        if cv2 is not None:
            img = cv2.imread(image_input)
            if img is None:
                raise ValueError(f"Failed to decode image file: '{image_input}'. File may be corrupted or unreadable.")
            return img

        raise ValueError(f"Unable to read image without OpenCV or Pillow: '{image_input}'")

    elif isinstance(image_input, np.ndarray):
        if image_input.size == 0:
            raise ValueError("Input image array is empty.")
        return image_input

    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")


def balance_exposure(image: np.ndarray) -> np.ndarray:
    """
    Applies CLAHE to the L-channel in LAB color space to equalize lighting
    disparities across adjacent drone flight strips without distorting chrominance.
    """
    if cv2 is None or image is None or image.size == 0:
        return image.copy() if image is not None else image

    # CLAHE operates on lightness (L) to preserve A and B color opponent channels
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    merged = cv2.merge((cl, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def check_image_quality(image: np.ndarray) -> Tuple[bool, float, str]:
    """
    Audits input image for severe blur (Laplacian variance) and extreme exposure.
    Returns: (is_acceptable, blur_score, message)
    """
    if cv2 is None:
        return True, 100.0, "OpenCV not present; quality check bypassed."

    if image is None or image.size == 0:
        return False, 0.0, "Empty or unreadable image frame."

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_brightness = float(np.mean(gray))

    if laplacian_var < 5.0:
        return False, laplacian_var, f"Image severely blurred (Laplacian variance {laplacian_var:.1f} < 5.0)."
    if mean_brightness < 10.0:
        return False, laplacian_var, f"Image severely underexposed (mean brightness {mean_brightness:.1f} < 10.0)."
    if mean_brightness > 250.0:
        return False, laplacian_var, f"Image severely overexposed (mean brightness {mean_brightness:.1f} > 250.0)."

    return True, laplacian_var, "Quality acceptable."


def load_and_preprocess_image(path: str) -> np.ndarray:
    """
    Deterministic ingestion pipeline: file validation -> EXIF orientation ->
    quality audit -> CLAHE exposure balancing. Returns BGR uint8 ndarray.
    """
    if not os.path.exists(path):
        raise ValueError(f"Image file does not exist: '{path}'")

    try:
        img = correct_exif_orientation(path)
    except Exception as e:
        raise ValueError(f"Failed to read image '{path}': {str(e)}")

    if img is None or img.size == 0:
        raise ValueError(f"Failed to decode image '{path}'. File is empty or corrupt.")

    # Ensure 3-channel BGR format
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if cv2 is not None else np.stack([img]*3, axis=-1)
    elif len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if cv2 is not None else img[:, :, :3]

    is_ok, score, msg = check_image_quality(img)
    if not is_ok:
        raise ValueError(f"Image '{os.path.basename(path)}' failed quality check: {msg}")

    return balance_exposure(img)


def normalize_image(image: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
    """
    Resizes and normalizes drone frame contrast for feature extraction.
    """
    if image is None:
        raise ValueError("Cannot normalize None image")

    balanced = balance_exposure(image)
    if target_size is not None and cv2 is not None:
        balanced = cv2.resize(balanced, target_size, interpolation=cv2.INTER_AREA)
    return balanced
