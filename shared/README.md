# Shared Data & Sample Artifacts — Land Logic DRONE-MAPPING-AI

This directory contains shared sample assets, test aerial frames, and intermediate outputs used across the team during the 36-hour sprint.

---

## 📂 Subdirectories

- **`sample_images/`**: Contains 3–5 sample overlapping drone aerial photos (with GPS EXIF metadata). Used to test stitching (Member 4), EXIF parsing (Member 5), and frontend drag-and-drop (Member 1).
- **`sample_outputs/`**: Contains reference outputs (e.g. `stitched_ortho.png`, `segmentation_mask.png`, `parcels.geojson`) so each member can develop independently without waiting for upstream pipeline completion.

---

## ⚠️ Data Size Rules
- Do NOT commit image files > 5MB into Git.
- Keep total folder size in Git under 15MB.
- For full-resolution flight datasets (gigabytes), store them on Google Drive / S3 and link the download URL in team chat.
