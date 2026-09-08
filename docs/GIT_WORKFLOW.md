# Land Logic DRONE-MAPPING-AI — Git Workflow & Contribution Guidelines

This document outlines team Git conventions, branching strategies, commit messages, and review rules to maintain a clean codebase throughout the 36-hour sprint.

---

## 1. Branching Strategy

We follow a structured **Feature-Branch Workflow** centered around `main` and `dev`:

```
  main (Production / Stable Demos)
   ▲
   │ [PR merge after end-to-end testing]
  dev (Sprint Integration Branch)
   ▲
   ├── feature/member-1-frontend-map
   ├── feature/member-2-backend-orchestrator
   ├── feature/member-3-ai-segmentation
   ├── feature/member-4-opencv-stitching
   └── feature/member-5-gis-georeferencing
```

### Branch Naming Conventions
- `feature/member-1-<feature-name>`: Member 1 Frontend features
- `feature/member-2-<feature-name>`: Member 2 Backend features
- `feature/member-3-<feature-name>`: Member 3 AI / ML models
- `feature/member-4-<feature-name>`: Member 4 OpenCV algorithms
- `feature/member-5-<feature-name>`: Member 5 GIS & Georeferencing
- `hotfix/<issue-name>`: Critical emergency fixes during dry runs

---

## 2. Commit Message Standards

We enforce [Conventional Commits](https://www.conventionalcommits.org/) to keep the git log clear and automated:

### Format
```
<type>(<scope>): <short imperative summary>

[optional body explaining context or trade-offs]

[optional footer referencing issue or task ID]
```

### Allowed Types
- `feat`: A new user-facing feature or algorithmic capability
- `fix`: A bug fix in pipeline, routing, or calculations
- `docs`: Documentation updates (API contracts, task board, README)
- `style`: Formatting, missing semicolons, styling tweaks (no code logic change)
- `refactor`: Code restructuring without changing functionality
- `test`: Adding or updating test cases
- `chore`: Dependency updates, build configurations, or git setup

### Examples
- `feat(opencv): implement SIFT feature detector with RANSAC homography`
- `fix(backend): fix multipart stream timeout on large image batches`
- `feat(frontend): add Mapbox vector polygon layer with NDVI color ramp`
- `docs(api): document GeoJSON parcel export schema`

---

## 3. Large File Handling Protocol (CRITICAL)

> [!WARNING]
> **DO NOT COMMIT LARGE FILES TO GIT**:
> - Never commit model weights (`.pt`, `.onnx`, `.pth` > 50MB) to Git.
> - Never commit raw drone image batches (`.tif`, `.tiff`, `.dng`, `.jpg` folders > 100MB) to Git.
> - Use the `shared/sample_images/` directory with a maximum of 3–5 lightweight sample images (< 2MB each) for testing.
> - Store large training sets and model weights on cloud storage (Google Drive, S3, or Hugging Face Hub) and pull via scripts.

---

## 4. Pull Request Checklist

Before merging into `dev` or `main`:
1. [ ] Branch is rebased onto the latest `dev`.
2. [ ] All lint and compilation checks pass (`npm run lint`, `flake8` / `black`).
3. [ ] No untracked cache files or `.env` files committed.
4. [ ] Tested locally with sample data in `shared/sample_images/`.
5. [ ] At least one other team member has reviewed the PR.
