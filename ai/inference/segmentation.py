"""
Segmentation and NDVI/VARI mathematical routines
Member 3: AI Engineer
(Maintained for backward compatibility; delegates to ai.postprocess)
"""

from ai.postprocess import compute_vari_index, generate_dummy_land_mask

__all__ = ["compute_vari_index", "generate_dummy_land_mask"]
