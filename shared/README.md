# Shared Data & Sample Artifacts — Land Logic DRONE-MAPPING-AI

This directory contains shared sample assets, test aerial frames, and intermediate outputs used across the **6-member team** during the hackathon sprint.

---

## 👥 Inter-Member Asset Flow
- **Member 1 (Frontend)**: Reads sample data to test drag-and-drop batch upload.
- **Member 2 (Backend)**: Uses sample frames to benchmark end-to-end pipeline execution.
- **Member 3 (AI)**: Consumes `sample_outputs/stitched_ortho.png` to test 512x512 tiling and VARI calculations.
- **Member 4 (OpenCV)**: Feeds `sample_images/` into `DroneStitcher` to test SIFT matching and homography warping.
- **Member 5 (GIS)**: Reads image EXIF metadata and outputs reference GeoJSON.
- **Member 6 (Leaflet Map)**: Renders `sample_outputs/parcels.geojson` and overlay raster images.

---

## 📂 Subdirectories
- **`sample_images/`**: Contains sample overlapping drone aerial photos (with GPS EXIF metadata).
- **`sample_outputs/`**: Contains reference outputs (`stitched_ortho.png`, `segmentation_mask.png`, `parcels.geojson`) so each member can develop independently without waiting for upstream pipeline completion.

---

## ⚠️ Data Size Rules
- Do NOT commit image files > 5MB into Git.
- Keep total folder size in Git under 15MB.
- For full-resolution flight datasets (gigabytes), store them on cloud storage (Google Drive / S3) and link the download URL in team documentation.
