# OpenCV & Orthomosaic Stitching — Land Logic DRONE-MAPPING-AI

👁️ **Owner**: Member 4  
🌿 **Assigned Branch**: `feature/opencv`  
🛠️ **Tech Stack**: OpenCV (cv2), NumPy, Scikit-image, imutils  
📁 **Workspace**: `opencv/`

---

## 🎯 Scope & Responsibilities
1. **Validation & Quality Auditing**: Checks input drone frames for blur (Laplacian variance), exposure, and contrast limits.
2. **Preprocessing**: Normalizes illumination differences using CLAHE (`opencv/preprocess.py`).
3. **Feature Extraction**: SIFT and ORB keypoint detection and local descriptor extraction (`opencv/features.py`).
4. **Feature Matching & Homography**: Robust pairwise matching with Lowe's ratio test and RANSAC homography matrix estimation (`opencv/matching.py`).
5. **Seamline Blending**: Smooths exposure discontinuities and flight shadow variations via feather and multi-band blending (`opencv/blending.py`).
6. **Global Orthomosaic Stitching**: Coordinates the multi-frame registration pipeline and outputs composite imagery (`opencv/stitching.py`).

---

## 📂 Directory Structure
```text
opencv/
├── preprocess.py         # CLAHE exposure balance & image quality audit
├── features.py           # SIFT & ORB feature detector and descriptors
├── matching.py           # k-NN matching & RANSAC homography estimation
├── blending.py           # Feather blending & seam smoothing
├── stitching.py          # DroneStitcher orchestration engine
├── scripts/
│   └── stitch_cli.py     # Standalone CLI entrypoint for drone stitching
├── tests/
│   └── test_opencv.py    # Unit test suite for OpenCV routines
├── preprocessing/
│   └── color_correction.py # Backward-compatibility wrapper
├── requirements.txt      # OpenCV dependencies
└── README.md
```

---

## 🚀 Execution & Testing

```bash
# Run unit tests
python3 -m unittest opencv/tests/test_opencv.py

# Run standalone stitcher CLI
python3 opencv/scripts/stitch_cli.py
```

