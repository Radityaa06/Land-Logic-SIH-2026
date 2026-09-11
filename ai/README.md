# AI & Land Vision Engine — Land Logic DRONE-MAPPING-AI

🤖 **Owner**: Member 3  
🌿 **Assigned Branch**: `feature/ai-integration`  
🛠️ **Tech Stack**: PyTorch, Ultralytics YOLOv8-Seg / UNet, NumPy, PIL, Scikit-learn  
📁 **Workspace**: `ai/`

---

## 🎯 Scope & Responsibilities
1. **Land-Use Classification**: Classifies orthomosaic tiles into the 5 project-defined categories:
   - `agricultural_land`
   - `barren_soil`
   - `forests`
   - `water_bodies`
   - `man_made_structures`
2. **Spectral Vegetative Index (VARI)**: Calculates the Visible Atmospherically Resistant Index (`(G - R) / (G + R - B)`) to evaluate crop health and canopy vitality.
3. **Sliding-Window Tiling & Reassembly**: Segments gigapixel orthomosaics into 512x512 inference windows with overlap and reconstructs seamless masks (`ai/tiling.py`).
4. **Structured Prediction Formatting**: Prepares parcel predictions (class, confidence, bounding boxes, mean VARI) for consumption by Member 5 (GIS).
5. **Clean Model Loading**: Standardized model wrapper interface in `ai/model.py` that operates cleanly with or without downloaded checkpoints.

---

## 📂 Directory Structure
```text
ai/
├── model.py              # Land segmentation classes and model loading interface
├── inference.py          # Top-level inference runner coordinating tiling, model & postprocess
├── tiling.py             # Sliding-window chip generation and mask reconstruction
├── postprocess.py        # VARI index computation & parcel contour discovery
├── tests/
│   └── test_ai.py        # Unit test suite for AI components
├── models/               # Model checkpoints (.gitkeep)
├── inference/
│   ├── predict.py        # Backward-compatibility wrapper
│   └── segmentation.py   # Backward-compatibility wrapper
├── requirements.txt      # AI dependencies
└── README.md
```

---

## 🚀 Execution & Testing

```bash
# Run unit tests
python3 -m unittest ai/tests/test_ai.py

# Run standalone inference
python3 -m ai.inference
```
