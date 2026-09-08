# AI & Computer Vision — Land Logic DRONE-MAPPING-AI

🤖 **Owner**: Member 3  
**Tech Stack**: PyTorch, Ultralytics YOLOv8-Seg / UNet, NumPy, OpenCV, Scikit-image

---

## 🎯 Scope & Responsibilities
1. **Land Use & Crop Segmentation**: Classifies orthomosaic tiles into distinct categories (crops, bare soil, forest canopy, water bodies, structures).
2. **Vegetation Health & NDVI**: Calculates spectral indices (VARI / NDVI) to detect crop water stress and canopy density.
3. **Sliding-Window Tiling**: Chunks ultra-large aerial mosaics into manageable 512x512 inference windows and reassembles predictions seamlessly without border seams.
4. **Boundary Extraction**: Emits vectorized field boundaries and parcel contours for consumption by Member 5 (GIS).

---

## 🚀 Quickstart

```bash
cd ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run inference test on a stitched aerial image
python inference/predict.py --input ../shared/sample_images/ --output ../shared/sample_outputs/
```

---

## 📂 Directory Layout
```text
ai/
├── models/               # Model weights & ONNX checkpoints (.gitkeep)
├── inference/
│   ├── predict.py        # Top-level inference entrypoint
│   └── segmentation.py   # Sliding window tiler & NDVI math
├── requirements.txt      # PyTorch & CV dependencies
└── README.md
```
