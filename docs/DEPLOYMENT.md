# Deployment Guide — Land Logic DRONE-MAPPING-AI (SIH 2026)

This doc explains two things: (1) how the 6 modules actually connect to
each other, so any team member knows what's safe to change without
breaking someone else's work, and (2) exact step-by-step instructions to
deploy the whole thing on Render.

---

## Part 1 — How the pieces actually connect

**The key fact to understand:** the frontend never talks to `ai/`,
`opencv/`, or `gis/` directly. Those three folders are only ever called
from inside `backend/app/services/pipeline.py`. The frontend's entire
integration surface is one HTTP endpoint: `POST /predict`.

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (frontend/)                                        │
│  ┌────────────┐   POST /predict    ┌──────────────────────┐  │
│  │ UploadZone │ ─────────────────▶ │  (goes to backend)   │  │
│  └────────────┘   (multipart file) └──────────────────────┘  │
│  ┌────────────┐   receives geojson prop from Dashboard.jsx   │
│  │ LeafletMap │ ◀───────────────────────────────────────┐    │
│  └────────────┘                                          │    │
└────────────────────────────────────────────────────────┼────┘
                                                            │
                     (this is the ONLY connection point)   │
                                                            │
┌───────────────────────────────────────────────────────────────┐
│  BACKEND (backend/)                                            │
│  routes/predict.py  →  validates upload, checks API key         │
│         │                                                        │
│         ▼                                                        │
│  services/pipeline.py  →  the ONLY code that calls the other    │
│         │                  3 modules, in this exact order:      │
│         ├──▶ opencv/  (stitching.py)     — merges raw frames    │
│         ├──▶ ai/      (inference.py)     — detects land classes │
│         └──▶ gis/     (geojson.py)       — builds GeoJSON output│
│         │                                                        │
│         ▼                                                        │
│  single JSON response: { status, summary, geojson, ... }        │
│  sent back to the frontend                                      │
└───────────────────────────────────────────────────────────────┘
```

**What this means practically:**
- If you're on frontend, backend, ai, opencv, or gis — you can work
  entirely inside your own folder without needing to coordinate line-by-
  line with anyone else, AS LONG AS you don't change what your module
  sends/receives at its boundary (documented in each module's README.md
  and in `docs/API_CONTRACT.md` for the frontend↔backend boundary).
- If you DO need to change a boundary (e.g. add a new field to the
  GeoJSON output, or change what `/predict` returns), update
  `docs/API_CONTRACT.md` in the same commit — that file is the single
  source of truth every other module was built against.
- Leaflet/map work is entirely inside `frontend/src/components/map/` —
  there's no separate "connecting" step, it just receives data as a
  normal React prop.

---

## Part 2 — Deploying to Render, step by step

You'll create **two separate Render services**: one for the backend
(a Python web service) and one for the frontend (a static site).

### Step 1 — Push your latest code to GitHub
Render deploys directly from your GitHub repo, so make sure `main` (or
whichever branch you deploy from) has everything merged in.

### Step 2 — Deploy the backend
1. Go to the Render dashboard → **New** → **Web Service**.
2. Connect your GitHub account and select `Land-Logic-SIH-2026`.
3. Set **Root Directory** to `backend`.
4. Set **Runtime** to Python 3.
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --limit-concurrency 10
   ```
   (this exact command, including the concurrency limit, is already
   documented in `backend/README.md` — it protects the single Render
   worker from being overwhelmed if multiple judges hit the demo at once)
7. Under **Environment**, add these variables:
   - `API_KEY` → set this to a real secret string you choose (e.g. a
     random 32-character value) — this is what protects `/predict` from
     being hit by anyone who doesn't have your frontend
   - `ALLOWED_ORIGINS` → for now, set a placeholder like
     `http://localhost:5173` — you'll come back and update this in Step 4
8. Click **Create Web Service** and wait for the first deploy to finish.
9. Once deployed, copy the backend's URL (something like
   `https://land-logic-backend.onrender.com`) — you'll need it next.
10. Test it's alive by visiting `https://your-backend-url.onrender.com/health`
    in a browser — you should get a simple success response with no
    API key required (that route is intentionally left open).

### Step 3 — Deploy the frontend
1. Render dashboard → **New** → **Static Site**.
2. Select the same repo.
3. Set **Root Directory** to `frontend`.
4. **Build Command**: `npm run build`
5. **Publish Directory**: `dist`
6. Under **Environment**, add:
   - `VITE_API_BASE_URL` → `https://your-backend-url.onrender.com/api/v1`
   - `VITE_ROOT_URL` → `https://your-backend-url.onrender.com`
   (use the actual backend URL you copied in Step 2.9 — these are the
   exact variable names `frontend/src/services/api.js` already reads;
   if they're unset it silently falls back to `localhost:8000`, which
   is why this step is required, not optional)
7. Click **Create Static Site** and wait for the build to finish.
8. Copy the frontend's URL once it's live (e.g.
   `https://land-logic-frontend.onrender.com`).

### Step 4 — Connect them: update backend CORS
This is the step that's easy to forget, because it only becomes
necessary once both services exist.
1. Go back to your **backend** service in Render → **Environment**.
2. Update `ALLOWED_ORIGINS` to include your real frontend URL:
   ```
   ALLOWED_ORIGINS=https://land-logic-frontend.onrender.com,http://localhost:5173
   ```
3. Save — Render will automatically redeploy the backend with the new
   setting. CORS changes don't take effect until this redeploy finishes.

### Step 5 — Test the real, deployed, connected app
1. Open your frontend's live URL in a browser.
2. Upload a real sample image (something from `shared/sample_images/`
   works well for this).
3. Confirm it actually reaches your backend — check the backend's logs
   in the Render dashboard; you should see structured log lines with a
   request id, per-stage timing, and outcome (this is the logging system
   that was built in an earlier hardening round).
4. Confirm the results — summary panel and map — render correctly with
   real data, not an error state.

### Common things that go wrong at this stage
- **CORS error in the browser console** → you forgot Step 4, or the
  backend hasn't finished redeploying yet after you changed
  `ALLOWED_ORIGINS`.
- **Frontend shows a network/timeout error** → check `VITE_ROOT_URL` was
  actually set correctly in Step 3, and that the backend's `/health`
  route responds when you visit it directly.
- **401 Unauthorized on upload** → the frontend needs to send the same
  `API_KEY` value in its request headers as what's set on the backend —
  check `frontend/src/services/api.js` for how it attaches the key, and
  confirm both sides use the identical value.
- **Backend cold-start delay** → Render's free tier spins down services
  after inactivity; the first request after idle time can take 30-60
  seconds to wake up. This is a platform limitation, not a bug — worth
  knowing about before a live judge demo, so consider doing a warm-up
  request a few minutes before you present.

---

## Quick reference — which env vars live where

| Variable | Set on | Purpose |
|---|---|---|
| `API_KEY` | Backend | Shared secret protecting `/predict` |
| `ALLOWED_ORIGINS` | Backend | Which frontend URLs are allowed to call it (CORS) |
| `VITE_API_BASE_URL` | Frontend | Base URL for project/pipeline-polling endpoints |
| `VITE_ROOT_URL` | Frontend | Base URL for the main `/predict` endpoint |

See `backend/.env.example` for the full, authoritative list of every
variable the backend reads (concurrency limits, timeout settings, etc.)
