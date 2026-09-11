"""
AI Image Tiling & Sliding-Window Reassembly
Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration

Splits large orthomosaics into manageable inference chips (e.g. 512x512)
with overlap, and merges the tile predictions back into full-scale masks.
"""

from typing import List, Tuple, Generator
import numpy as np


class ImageTiler:
    """
    Handles sliding-window chip extraction and seamless mask reconstruction.
    """
    def __init__(self, tile_size: int = 512, overlap: int = 64):
        self.tile_size = tile_size
        self.overlap = overlap
        self.step = tile_size - overlap

    def generate_tiles(self, image: np.ndarray) -> Generator[Tuple[int, int, int, int, np.ndarray], None, None]:
        """
        Yields (y, x, height, width, chip_array) for every window position.
        """
        h, w = image.shape[:2]

        for y in range(0, h, self.step):
            for x in range(0, w, self.step):
                # Ensure boundary coverage
                y_end = min(y + self.tile_size, h)
                x_end = min(x + self.tile_size, w)
                y_start = max(0, y_end - self.tile_size)
                x_start = max(0, x_end - self.tile_size)

                chip = image[y_start:y_end, x_start:x_end]
                yield y_start, x_start, y_end - y_start, x_end - x_start, chip

    def assemble_mask(
        self,
        full_shape: Tuple[int, int],
        predicted_tiles: List[Tuple[int, int, np.ndarray]]
    ) -> np.ndarray:
        """
        Reconstructs the full-size mask from individual predicted chips.
        """
        h, w = full_shape[:2]
        full_mask = np.zeros((h, w), dtype=np.uint8)

        for y_start, x_start, chip_mask in predicted_tiles:
            ch, cw = chip_mask.shape[:2]
            # Write into full mask (in overlapping regions, later tiles overwrite gracefully)
            full_mask[y_start:y_start + ch, x_start:x_start + cw] = chip_mask

        return full_mask
