# Land Logic DRONE-MAPPING-AI — Git Workflow (6-Member Strategy)

This document outlines team Git conventions, 6-member branching strategies, commit messages, and review rules to maintain a clean codebase throughout the 36-hour sprint.

---

## 1. Branching Strategy

We follow a structured **Feature-Branch Workflow** centered around `main`:

```text
main (Production / Stable Demos)
 │
 ├── feature/react-frontend       (Member 1 — UI/UX & App Shell)
 ├── feature/fastapi-backend      (Member 2 — Backend & Pipeline Orchestrator)
 ├── feature/ai-integration       (Member 3 — AI & Land Vision Engine)
 ├── feature/opencv               (Member 4 — OpenCV Orthomosaic Stitching)
 ├── feature/gis-geojson          (Member 5 — GIS & Georeferencing)
 └── feature/leaflet-map          (Member 6 — Leaflet / Interactive Map)
```

---

## 2. Branch Ownership Matrix

| Member | Assigned Branch | Workspace | Scope |
| :--- | :--- | :--- | :--- |
| **Member 1** | `feature/react-frontend` | `frontend/` *(excl. `components/map/`)* | App shell, uploader, results, dashboard, and styles |
| **Member 2** | `feature/fastapi-backend` | `backend/` | FastAPI gateway, pipeline orchestrator, `/predict`, artifacts |
| **Member 3** | `feature/ai-integration` | `ai/` | Tiling, model inference, VARI index, land classification |
| **Member 4** | `feature/opencv` | `opencv/` | Image preprocessing, SIFT/ORB features, homography, stitching |
| **Member 5** | `feature/gis-geojson` | `gis/` | EXIF extraction, GSD, world files, RFC 7946 GeoJSON generator |
| **Member 6** | `feature/leaflet-map` | `frontend/src/components/map/` | Leaflet map, vector polygon styling, popups, legend, layers |

---

## 3. Contribution Rules

All 6 members must adhere to these rules:

1. **Pull Latest Main**: Always pull or rebase onto `origin/main` before beginning work.
2. **Work Only on Assigned Workspace & Branch**:
   - Member 1 works on `feature/react-frontend` and must NOT touch `frontend/src/components/map/`.
   - Member 6 works on `feature/leaflet-map` and touches ONLY `frontend/src/components/map/`.
   - Members 2, 3, 4, 5 work strictly within `backend/`, `ai/`, `opencv/`, and `gis/`.
3. **Commit Logical Changes**: Use conventional commit messages.
4. **Push Branch & Open PR**: Push to remote branch and open a Pull Request into `main`.
5. **Review Integration Conflicts**: Verify interface contracts before merging.
6. **Merge Only After Verification**: Ensure unit tests and frontend build pass prior to merging.

---

## 4. Commit Message Standards

We enforce [Conventional Commits](https://www.conventionalcommits.org/):

### Format
```text
<type>(<scope>): <short imperative summary>

[optional body explaining context]
```

### Allowed Types
- `feat`: A new feature or algorithm implementation
- `fix`: A bug fix in pipeline, routing, or math
- `docs`: Documentation updates
- `style`: Formatting or CSS styling
- `refactor`: Restructuring code without changing functionality
- `test`: Adding or running tests
- `chore`: Dependency or config updates

### Examples
- `feat(map): render classified land parcel polygons with class color ramp`
- `feat(backend): add unified POST /predict pipeline endpoint`
- `fix(gis): set coordinate_space to pixel when genuine GPS is absent`
- `feat(opencv): implement SIFT feature extraction with RANSAC homography`
- `feat(ai): compute VARI spectral vegetative index`

---

## 5. Large File Handling Protocol (CRITICAL)

> [!WARNING]
> **DO NOT COMMIT LARGE FILES TO GIT**:
> - Never commit model weights (`.pt`, `.onnx`, `.pth` > 50MB) to Git.
> - Never commit raw drone flight batches (`.tif`, `.dng`, `.jpg` folders > 100MB) to Git.
> - Use the `shared/sample_images/` directory with a maximum of 3–5 lightweight sample images (< 2MB each) for testing.
> - Store large training sets and model weights on cloud storage (Google Drive, S3, or Hugging Face Hub).
> - Never commit `.env` files, API keys, or private tokens.
