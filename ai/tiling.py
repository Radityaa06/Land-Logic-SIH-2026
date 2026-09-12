"""
AI Image Tiling & Sliding-Window Reassembly
Member 3: AI / Land Vision Engine
Workspace: ai/
Branch: feature/ai-integration

Splits large orthomosaics into manageable inference chips (e.g. 512x512)
with overlap, and merges the tile predictions back into full-scale masks.
Eliminates duplicate edge slices and boundary seams in overlap zones.
"""

from typing import List, Tuple, Generator
import numpy as np


class ImageTiler:
    """
    Handles sliding-window chip extraction and seamless mask reconstruction.
    Ensures complete boundary coverage without yielding duplicate edge tiles.
    """
    def __init__(self, tile_size: int = 512, overlap: int = 64):
        if overlap >= tile_size:
            raise ValueError(f"overlap ({overlap}) must be strictly less than tile_size ({tile_size})")
        self.tile_size = tile_size
        self.overlap = overlap
        self.step = tile_size - overlap

    def _compute_1d_slices(self, length: int) -> List[Tuple[int, int]]:
        """
        Computes unique non-redundant [start, end) 1D window intervals ensuring
        100% pixel coverage up to length, without duplicate slices at edges.
        """
        if length <= self.tile_size:
            return [(0, length)]

        starts = list(range(0, length - self.tile_size + 1, self.step))
        # If the last regular step doesn't reach the boundary, add clamped terminal window
        if starts[-1] + self.tile_size < length:
            starts.append(length - self.tile_size)

        unique_starts = sorted(set(starts))
        return [(s, min(s + self.tile_size, length)) for s in unique_starts]

    def generate_tiles(self, image: np.ndarray) -> Generator[Tuple[int, int, int, int, np.ndarray], None, None]:
        """
        Yields (y_start, x_start, height, width, chip_array) for every window position.
        Guarantees that every pixel is covered and no duplicate coordinate windows are emitted.
        """
        h, w = image.shape[:2]
        y_slices = self._compute_1d_slices(h)
        x_slices = self._compute_1d_slices(w)

        for y_start, y_end in y_slices:
            for x_start, x_end in x_slices:
                chip = image[y_start:y_end, x_start:x_end]
                yield y_start, x_start, y_end - y_start, x_end - x_start, chip

    def assemble_mask(
        self,
        full_shape: Tuple[int, int],
        predicted_tiles: List[Tuple[int, int, np.ndarray]]
    ) -> np.ndarray:
        """
        Reconstructs the full-size mask from individual predicted chips.
        Uses center-prioritized distance weighting in overlap zones to prevent
        boundary artifacts from overriding central predictions.
        """
        h, w = full_shape[:2]
        full_mask = np.zeros((h, w), dtype=np.uint8)
        dist_to_center = np.full((h, w), fill_value=np.inf, dtype=np.float32)

        for y_start, x_start, chip_mask in predicted_tiles:
            ch, cw = chip_mask.shape[:2]
            # Compute distance to chip center: central pixels have lowest distance
            cy, cx = (ch - 1) / 2.0, (cw - 1) / 2.0
            y_coords, x_coords = np.ogrid[:ch, :cw]
            tile_dist = (y_coords - cy) ** 2 + (x_coords - cx) ** 2

            sub_dist = dist_to_center[y_start:y_start + ch, x_start:x_start + cw]
            closer = tile_dist < sub_dist

            sub_mask = full_mask[y_start:y_start + ch, x_start:x_start + cw]
            sub_mask[closer] = chip_mask[closer]
            sub_dist[closer] = tile_dist[closer]

        return full_mask

