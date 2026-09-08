# OpenCV & Orthomosaic Stitching — Land Logic DRONE-MAPPING-AI

👁️ **Owner**: Member 4  
**Tech Stack**: OpenCV (cv2), NumPy, Scikit-image, imutils

---

## 🎯 Scope & Responsibilities
1. **Feature Matching & Alignment**: SIFT / ORB keypoint extraction with RANSAC-based homography matrix estimation.
2. **Global Registration**: Aligns dozens of overlapping aerial photos into a continuous panoramic projection.
3. **Seamline Blending**: Eliminates exposure discontinuities and flight shadow variations via multi-band pyramid blending.
4. **Distortion Calibration**: Compensates for wide-angle drone lens curvature and vignetting.

---

## 🚀 Quickstart

```bash
cd opencv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run stitching pipeline on sample flight images
python stitching/stitcher.py --input ../shared/sample_images/ --output ../shared/sample_outputs/stitched_ortho.png
```

---

## 📂 Directory Layout
```text
opencv/
├── stitching/
│   └── stitcher.py       # SIFT feature matcher & homography warp
├── preprocessing/
│   └── color_correction.py # Histogram equalization & vignetting correction
├── requirements.txt      # OpenCV dependencies
└── README.md
```
