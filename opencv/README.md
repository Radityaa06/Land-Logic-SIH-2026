# OpenCV & Orthomosaic Stitching — Land Logic DRONE-MAPPING-AI

👁️ **Owner**: Member 4  
🌿 **Assigned Branch**: `feature/opencv`  
🛠️ **Tech Stack**: OpenCV (`cv2`), NumPy, Pillow, Scikit-image, imutils  
📁 **Workspace**: `opencv/`

---

## 🎯 Scope & Responsibilities
1. **Input Robustness & Auditing**: Validates all incoming flight frames, catches corrupted/empty files, checks blur (Laplacian variance) and brightness boundaries.
2. **Preprocessing & EXIF Orientation**: Normalizes orientation across drone gimbal shifts (`correct_exif_orientation`) and balances flight strip illumination using CLAHE on the L-channel in LAB color space (`balance_exposure`).
3. **Feature Extraction**: Extracts scale-invariant local keypoints and descriptors using **SIFT** (default per `StitchRequest`) with ORB fallback (`opencv/features.py`).
4. **Feature Matching & Homography**: Pairwise k-NN matching (Lowe's ratio threshold = 0.75) and RANSAC homography matrix estimation (`opencv/matching.py`).
5. **Seamline Blending**: Multi-band blending and feather smoothing to remove seams between overlapping flight strips (`opencv/blending.py`).
6. **Global Orthomosaic Stitching**: Orchestrates registration and composite generation (`DroneStitcher` in `opencv/stitching.py`).

---

## 📋 Inter-Member Data Contract (Members 2 & 3)

Downstream modules (**Member 2: Backend Orchestrator** and **Member 3: AI Land Vision**) rely on the following exact data specification:

| Parameter | Specification | Downstream Impact |
| :--- | :--- | :--- |
| **Output File** | `stitched_orthomosaic.png` | Saved to `backend/outputs/{project_id}/stitched_orthomosaic.png` |
| **Tensor Shape** | `(H, W, 3)` | 3-channel 2D spatial raster where $H = \text{height}$, $W = \text{width}$ |
| **Data Type** | `numpy.uint8` | Integer pixel intensities in range $[0, 255]$ |
| **Channel Ordering** | **BGR** | Standard OpenCV format. **Member 3 must convert to RGB** via `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` prior to feeding into PyTorch/YOLOv8 or calculating VARI `(G - R) / (G + R - B)`. |
| **Coordinate Space** | Pixel $(X, Y)$ | Top-left origin $(0, 0)$ to $(W, H)$, consumed by Member 5 for affine georeferencing and vectorization. |

---

## 🛡️ Input Robustness & Error Guarantees

The stitching pipeline implements strict, catchable exception semantics for Member 2's `PipelineStageError("stitching", detail)`:

- **Minimum Image Set ($\ge 2$ frames)**: Passing 0 or 1 image raises `ValueError("Stitching requires at least 2 image frames...")`. Silent mock generation has been completely removed.
- **Corrupted / Unreadable Files**: If an image cannot be decoded or is corrupted, `load_and_preprocess_image()` raises a descriptive `ValueError("Failed to decode image '<path>'...")` identifying the offending file.
- **Alignment Failures**: If visual overlap is insufficient ($< 60\%$) or bundle adjustment fails, `cv2.Stitcher` returns an error code that is translated into an actionable `RuntimeError`:
  - `ERR_NEED_MORE_IMGS` (1): Insufficient feature overlap between flight frames.
  - `ERR_HOMOGRAPHY_EST_FAIL` (2): RANSAC could not find a geometrically consistent affine transformation.
  - `ERR_CAMERA_PARAMS_ADJUST_FAIL` (3): Camera bundle adjustment optimization failed.
- **EXIF Normalization**: Every image automatically has its EXIF orientation tag corrected before feature detection.
- **Feature Detector Alignment**: `DroneStitcher` explicitly sets its features finder to **SIFT** (`cv2.SIFT_create()`), matching `StitchRequest.feature_detector = "SIFT"` in `backend/app/models/schemas.py`.

---

## ⏱️ Real Performance Profiling Benchmarks

Benchmarked on a representative multi-frame flight batch from `shared/sample_images/` ($640 \times 448$ px per frame, 70% forward overlap):

| Pipeline Stage | Total Duration | Per-Frame / Pair Metric |
| :--- | :--- | :--- |
| **Preprocessing** (EXIF transpose + CLAHE LAB) | `212.5 ms` | `70.8 ms / frame` |
| **SIFT Feature Extraction** | `94.1 ms` | `31.4 ms / frame` (avg. 15–30 keypoints) |
| **Feature Matching** (k-NN + Lowe's test) | `0.20 ms` | `0.20 ms / frame pair` |
| **End-to-End Stitching** (Registration + Blending) | `4.98 s` | ~5.0 seconds for 3-frame strip |
| **Output Image Specification** | Shape: `(640, 541, 3)` | Data type: `uint8` (BGR) |

### 🔒 Recommendation for Member 2's Concurrency Cap
- OpenCV SIFT feature extraction, matching, and bundle adjustment are CPU-intensive operations that utilize multi-threaded OpenMP / TBB primitives.
- Given an average pipeline latency of **~5 seconds per 3-frame flight batch**, Member 2 should configure the concurrency ceiling to:
  $$\text{Concurrency Cap} = \max(1, \lfloor \text{CPU Cores} / 2 \rfloor)$$
- For standard 4–8 core instances, **2 to 3 concurrent stitching workers** is the safe maximum to prevent CPU starvation, memory spikes, and watchdog timeouts on `POST /predict`.

---

## 📂 Directory Structure
```text
opencv/
├── preprocess.py              # EXIF orientation, CLAHE balance & quality audit
├── features.py                # SIFT & ORB feature extractor
├── matching.py                # k-NN matcher with Lowe's ratio test & RANSAC homography
├── blending.py                # Feather blending & seam smoothing
├── stitching.py               # DroneStitcher orchestration engine
├── scripts/
│   └── stitch_cli.py          # Standalone CLI entrypoint for drone stitching
├── tests/
│   └── test_opencv.py         # Unit test suite for OpenCV routines
├── preprocessing/
│   └── color_correction.py    # Backward-compatibility wrapper
├── requirements.txt           # OpenCV dependencies
└── README.md                  # Module specification & benchmarks
```

---

## 🚀 Execution & Testing

```bash
# Run unit tests
python -m unittest opencv/tests/test_opencv.py

# Run standalone stitcher CLI
python opencv/scripts/stitch_cli.py --input shared/sample_images --output shared/sample_outputs/stitched_ortho.png
```
