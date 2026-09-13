# AI & Land Vision Engine — Land Logic DRONE-MAPPING-AI

🤖 **Owner**: Member 3  
🌿 **Assigned Branch**: `feature/ai-integration`  
🛠️ **Tech Stack**: NumPy, Pillow, SciPy (connected components), PyTorch / ONNX interface  
📁 **Workspace**: `ai/`

---

## 🎯 Scope & Capabilities

1. **Land-Use Classification**: Identifies and segments 5 project-defined canonical categories:
   - `agricultural_land` (class_id: 1)
   - `barren_soil` (class_id: 2)
   - `forests` (class_id: 3)
   - `water_bodies` (class_id: 4)
   - `man_made_structures` (class_id: 5)
2. **Spectral Vegetative Index (VARI)**: Evaluates canopy vitality using the Visible Atmospherically Resistant Index (`(G - R) / (G + R - B)`).
3. **Sliding-Window Tiling & Reassembly**: Splits orthomosaics into overlapping chips (default 512x512) and reassembles masks using center-prioritized distance weighting to prevent edge boundary artifacts.
4. **Connected-Component Parcel Discovery**: Separates distinct fields into individual parcels using 8-connectivity labeling (`scipy.ndimage.label`), eliminating multi-field bounding box clustering.
5. **Cached Model Singleton**: Loads model weights once at startup/import (`get_segmentation_model()`) and caches the instance across requests.

---

## 📋 Input / Output Integration Contract

This contract is strictly maintained for **Member 2 (Backend Orchestrator)** and **Member 5 (GIS Georeferencing)**.

### Primary Entrypoint

```python
from ai.inference import run_inference, DEFAULT_CONFIDENCE_THRESHOLD

result = run_inference(
    image_path: str,
    output_dir: str,
    tile_size: int = 512,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD, # 0.50
    checkpoint_path: Optional[str] = None
)
```

### Input Parameters

| Parameter | Type | Default | Description & Validation |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *required* | Path to decodable RGB orthomosaic (PNG/JPG). Must exist and be $\ge 16 \times 16$ px. Raises `FileNotFoundError` if missing or `ValueError` if corrupt/invalid. |
| `output_dir` | `str` | *required* | Directory where `segmentation_mask.png` is saved. Created automatically if not present. |
| `tile_size` | `int` | `512` | Square dimension of sliding-window inference chips. |
| `confidence_threshold` | `float` | `0.50` | Minimum confidence score to retain a parcel in `predictions`. |
| `checkpoint_path` | `Optional[str]` | `None` | Path to weights file (.pt/.onnx). If `None`, uses calibrated spectral engine. |

### Output Dictionary Schema

```python
{
    "status": "SUCCESS",                      # str: execution status
    "mask_path": "/path/to/segmentation_mask.png", # str: saved grayscale mask artifact
    "mean_vari": 0.186,                       # float: average VARI across whole image [-1.0, 1.0]
    "classes_supported": [                    # List[str]: canonical project classes
        "agricultural_land",
        "barren_soil",
        "forests",
        "water_bodies",
        "man_made_structures"
    ],
    "predictions": [                          # List[Dict[str, Any]]: detected parcel records
        {
            "parcel_id": "parcel_01",         # str: sequential parcel identifier
            "class": "agricultural_land",     # str: class label (matches classes_supported)
            "class_id": 1,                    # int: canonical integer ID (1..5)
            "confidence": 0.95,               # float: detection confidence [0.0, 1.0]
            "pixel_bbox": [40, 43, 299, 279], # List[int]: [min_x, min_y, max_x, max_y]
            "pixel_area": 56200,              # int: area in pixels of connected component
            "mean_vari": 0.742,               # float: mean VARI within parcel [-1.0, 1.0]
            "crop_health": "healthy"          # str: 'healthy', 'moderate', 'stressed', or 'not_applicable'
        }
    ],
    "raster_shape": [640, 640]                # List[int]: [height, width] of input orthomosaic
}
```

### Downstream Consumer Mapping

- **Member 2 (`backend/app/services/pipeline.py`)**:
  - `ai_results["predictions"]`: iterated to extract distinct detected classes (`{p["class"] for p in ai_results.get("predictions", [])}`) and aggregate `crop_health_summary`.
  - `ai_results["mean_vari"]`: included in pipeline response summary.
  - `ai_results["mask_path"]`: mapped to artifacts response payload.
- **Member 5 (`gis/geojson.py`)**:
  - `ai_results["predictions"]`: passed directly as `parcels` into `generate_parcels_geojson()`.
  - Reads `p["pixel_bbox"]` for polygon ring bounds, `p["parcel_id"]`, `p["class"]`, `p["confidence"]`, `p["mean_vari"]`, `p["pixel_area"]`, and `p["crop_health"]`.

---

## 🌿 Spectral Indices & Crop Health Classification (VARI)

- **VARI (`compute_vari_index`) is REAL**: Calculated per-pixel using `(Green - Red) / (Green + Red - Blue)` from the 3 visible RGB channels. Includes numerical stabilization (`epsilon = 1e-5`) to eliminate zero-division and sign-inversion spikes in deep shadows and water bodies.
- **Crop Health & Stress Classification (`classify_crop_health`)**:
  - Evaluates vegetation vitality for `agricultural_land` and `forests`:
    - **`healthy`**: $\text{VARI} \ge 0.20$ (dense, vigorous canopy with strong chlorophyll reflectance)
    - **`moderate`**: $0.05 \le \text{VARI} < 0.20$ (adequate canopy, mild moisture stress, or early-stage growth)
    - **`stressed`**: $\text{VARI} < 0.05$ (sparse canopy, chlorosis, moisture deficit, or crop damage)
  - Non-vegetative categories (`barren_soil`, `water_bodies`, `man_made_structures`) return **`not_applicable`**.
- **NDVI is NOT computed**: True NDVI requires Near-Infrared (NIR) imagery ($[NIR - Red] / [NIR + Red]$). Because drone inputs are standard 3-channel RGB imagery, NDVI cannot be calculated without multispectral hardware. VARI is the standard RGB proxy.

---

## ⚙️ Configuration & Thresholds

- **Crop Health Thresholds**: `VARI_HEALTHY_THRESHOLD = 0.20`, `VARI_MODERATE_THRESHOLD = 0.05`.
- **Active Confidence Threshold**: `DEFAULT_CONFIDENCE_THRESHOLD = 0.50`. Discards small isolated speckles and boundary noise below 50% confidence.
- **Minimum Parcel Area**: `min_area_pixels = 100`. Connected components smaller than 100 pixels are excluded from parcel predictions to suppress tile seam artifacts.
- **Model Caching**: Cached in `_MODEL_CACHE` within `ai/model.py`. New instances are only allocated if a different checkpoint path or device is specified, or if `force_reload=True`.

---

## 📂 Directory Structure

```text
ai/
├── model.py              # Land segmentation classes and model loading interface
├── inference.py          # Top-level inference runner coordinating tiling, model & postprocess
├── tiling.py             # Sliding-window chip generation and mask reconstruction
├── postprocess.py        # VARI index computation & parcel contour discovery
├── scripts/
│   └── predict_cli.py    # Standalone CLI entrypoint with argument parsing
├── tests/
│   └── test_ai.py        # Unit test suite for AI components
├── models/               # Model checkpoints directory (.gitkeep)
├── requirements.txt      # AI dependencies
└── README.md
```

---

## 📊 Performance & Benchmark Status

- **Model Execution**: Operating on the calibrated spectral segmentation engine when checkpoints are not loaded.
- **Real Trained Classifier**: Not yet built, requires labeled dataset — currently using RGB-heuristic fallback, disclosed above.
- **Inference Speed & Accuracy (mIoU)**: **Not yet benchmarked** on full flight datasets. Benchmarking will be performed once dedicated test flight orthomosaics are cataloged.

---

## 🧪 Testing

```bash
# Run the AI unit test suite (12 tests)
python -m unittest ai/tests/test_ai.py -v

# Run backend cross-module pipeline tests
python -m unittest backend/tests/test_backend.py -v

# Run CLI entrypoint test
python ai/scripts/predict_cli.py
```


