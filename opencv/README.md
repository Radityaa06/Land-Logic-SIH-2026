# OpenCV & Orthomosaic Stitching — Land Logic DRONE-MAPPING-AI

👁️ **Owner**: Member 4  
🌿 **Assigned Branch**: `feature/opencv`  
🛠️ **Tech Stack**: OpenCV (`cv2`), NumPy, Pillow, Scikit-image, imutils  
📁 **Workspace**: `opencv/`

---

## 🎯 Scope & Responsibilities
1. **Input Robustness & Auditing**: Validates all incoming flight frames, catches corrupted/empty files, checks blur (Laplacian variance) and brightness boundaries.
2. **Preprocessing & EXIF Orientation**: Normalizes orientation across drone gimbal shifts (`correct_exif_orientation`) and balances flight strip illumination using CLAHE on the L-channel in LAB color space (`balance_exposure`).
3. **Global Orthomosaic Stitching**: Orchestrates registration and composite generation (`DroneStitcher` in `opencv/stitching.py`) delegating to `cv2.Stitcher_create(cv2.Stitcher_SCANS)`.

> [!NOTE]
> **Standalone Modules (`features.py`, `matching.py`, `blending.py`)**:
> `DroneStitcher.stitch_image_list()` delegates feature extraction, pairwise matching, homography estimation, and seam blending entirely to `cv2.Stitcher`'s internal C++ implementation. The modules `opencv/features.py` (SIFT/ORB detection), `opencv/matching.py` (k-NN matching, Lowe's ratio test, RANSAC homography), and `opencv/blending.py` (feather and multiband seam smoothing) are standalone, independently unit-tested components that are **not** wired into the default `stitch_image_list()` execution path. They are maintained for standalone utilities, debugging registration failures frame-pair-by-pair, and future manual pipeline customization (see *Architecture Roadmap* below).

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
- **C++ Crash Protection**: Raw `cv2.error` assertions thrown by `stitcher.stitch()` on pathological inputs are caught and re-raised as `RuntimeError("Orthomosaic stitching crashed inside OpenCV: ...")`, ensuring clean, readable error reporting instead of unhandled stack traces.
- **EXIF Normalization**: Every image automatically has its EXIF orientation tag corrected before feature detection.
- **Feature Detector Alignment**: `DroneStitcher` explicitly sets its features finder to **SIFT** (`cv2.SIFT_create()`), matching `StitchRequest.feature_detector = "SIFT"` in `backend/app/models/schemas.py`.

---

## ⏱️ Real Performance Profiling Benchmarks

Benchmarked on genuine photographic aerial drone frames from `shared/sample_images/` ($960 \times 640$ px per frame, genuine forward overlap and agricultural surface texture):

| Pipeline Stage | Total Duration | Per-Frame / Pair Metric | Observations |
| :--- | :--- | :--- | :--- |
| **Preprocessing** (EXIF transpose + CLAHE LAB) | `246.6 ms` | `82.2 ms / frame` | Normalized exposure & standardized orientations |
| **SIFT Feature Extraction** | `181.5 ms` | `60.5 ms / frame` | **2,000 keypoints / frame** with scale-space octaves |
| **Feature Matching** (k-NN + Lowe's + RANSAC) | `12.2 ms` | `12.2 ms / pair` | **594 good matches**, **553 RANSAC inliers** |
| **End-to-End Stitching** (Registration + Blending) | `690.2 ms` | **0.69 s** for 3-frame strip | Robust planar homography alignment & multiband blend |
| **Output Orthomosaic Composite** | Shape: `(677, 1599, 3)` | Data type: `uint8` (BGR) | Non-degenerate, seamless composite with full texture |

---

## 🔍 Known Limitations & Architecture Roadmap (Item 4)

1. **OpenCV Python Bindings for Feature Finder**:
   - In standard OpenCV 4.x / 5.x Python bindings, `cv2.Stitcher.setFeaturesFinder` is not exposed in the C++ Python wrapper.
   - `StitchRequest.feature_detector` is fully wired from the FastAPI schema through `execute_pipeline()` into `DroneStitcher(detector_type=...)` to stop the API from silently ignoring user parameters. However, calling `setFeaturesFinder` is safely guarded in a `try/except` block and will not alter `cv2.Stitcher`'s internal C++ defaults.
2. **Path to Genuine Per-Request Feature Detector Switching**:
   - To make `detector_type="ORB"` or custom feature detectors functionally effective at runtime, `DroneStitcher`'s registration path must be rebuilt using OpenCV's low-level `cv2.detail_*` API:
     - `cv2.detail_computeImageFeatures2` (or `FeatureExtractor` from `opencv/features.py`)
     - `cv2.detail_BestOf2NearestMatcher` (or `FeatureMatcher` from `opencv/matching.py`)
     - `cv2.detail_HomographyBasedEstimator`
     - `cv2.detail_BundleAdjusterRay`
     - `cv2.detail_MultiBandBlender`
   - Rebuilding on `cv2.detail_*` would also make `opencv/features.py` and `opencv/matching.py` directly load-bearing in the production path instead of standalone modules.
   - **Guideline**: *Do not implement this rewrite speculatively — confirm with the team first as it represents a significant architectural overhaul of the registration engine.*

---

## 📌 Recommendations for Member 2 (Backend Orchestrator)

### Item 5: Concurrency Cap Re-Check & Tuning
- The original synthetic benchmarks (~5.0s) reflected degenerate corner cases on flat images. With real photographic images, 3 frames ($960 \times 640$) stitch in **~0.69 seconds**.
- However, full production drone missions typically ingest batches of 20–60 full-resolution (4K / 12MP–24MP) flight frames. In that regime:
  - Memory consumption scales with image dimensions and pyramid blend bands (~300MB–800MB peak RSS per worker).
  - Multi-threaded SIFT and bundle adjustment saturate CPU cores via OpenMP.
- **Tuned Recommendation**: Member 2 should maintain the concurrency ceiling:
  $$\text{Concurrency Cap} = \max\left(1, \left\lfloor \frac{\text{CPU Cores}}{2} \right\rfloor\right)$$
  - Standard 4-core worker: limit to **2 concurrent jobs**.
  - 8-core worker: limit to **3–4 concurrent jobs**.
  - Any additional concurrent requests should return `503 Service Unavailable` with `Server busy, try again in a moment` via `pipeline_concurrency_guard`.

### Item 6: Diagnostic SSE Progress Events
- When image stitching fails with `ERR_NEED_MORE_IMGS` (OpenCV status code 1), the API currently returns a generic `500 Internal Server Error` with `Pipeline failed at stage 'stitching'`.
- **Recommended Enhancement**:
  - In `opencv/stitching.py` or `opencv/matching.py`, count the pairwise extracted keypoints and surviving Lowe's ratio matches prior to alignment.
  - Surface these diagnostic metrics in the SSE event payload emitted to the frontend:
    ```json
    {
      "stage": "stitching",
      "status": "error",
      "message": "OpenCV stitching failed: Insufficient overlap between frame_02 and frame_03 (found 2000 keypoints each, but only 4 matching features — flight overlap is below recommended 60-70%)."
    }
    ```
  - This provides drone operators with actionable flight guidance rather than an opaque server error.

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
