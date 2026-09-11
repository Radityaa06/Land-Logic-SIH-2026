/**
 * Land Logic DRONE-MAPPING-AI — Frontend API Client
 * Member 1: Frontend & UI/UX
 * Connects Member 1's UI to Member 2's FastAPI Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const ROOT_URL = import.meta.env.VITE_ROOT_URL || 'http://localhost:8000';

/**
 * Checks whether an error was triggered by request cancellation or timeout.
 */
export function isAbortError(err) {
  return Boolean(err && (err.name === 'AbortError' || err.code === 20 || err.message === 'Request timed out'));
}

export const api = {
  /**
   * Unified Pipeline Ingestion Endpoint:
   * Sends drone frames directly through Member 2's central orchestrator
   * (OpenCV -> AI -> GIS -> Backend -> Frontend)
   */
  async predictDirect(files = [], projectId = null, signal = null, timeoutMs = 30000) {
    const controller = new AbortController();
    let timerId = null;

    if (timeoutMs && timeoutMs > 0) {
      timerId = setTimeout(() => {
        controller.abort(new Error('Request timed out'));
      }, timeoutMs);
    }

    if (signal) {
      if (signal.aborted) {
        controller.abort(signal.reason);
      } else {
        signal.addEventListener('abort', () => controller.abort(signal.reason), { once: true });
      }
    }

    const formData = new FormData();
    if (projectId) {
      formData.append('project_id', projectId);
    }
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await fetch(`${ROOT_URL}/predict`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      if (!res.ok) {
        let errorMessage = 'Upload failed — please try again';
        try {
          const errData = await res.json();
          if (errData && (errData.detail || errData.message)) {
            const rawMsg = errData.detail || errData.message;
            errorMessage = typeof rawMsg === 'object' ? JSON.stringify(rawMsg) : String(rawMsg);
          }
        } catch {
          // Body not parseable as JSON; keep generic fallback
        }
        throw new Error(errorMessage);
      }

      return await res.json();
    } finally {
      if (timerId) {
        clearTimeout(timerId);
      }
    }
  },

  /**
   * Create a new mapping project
   */
  async createProject(name, description) {
    const res = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    });
    return res.json();
  },

  /**
   * Upload drone images for a given project
   */
  async uploadImages(projectId, files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/upload`, {
      method: 'POST',
      body: formData,
    });
    return res.json();
  },

  /**
   * Trigger processing pipeline (OpenCV Stitching, AI, and GIS)
   */
  async startPipeline(projectId) {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/pipeline/stitch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ blend_mode: 'MULTIBAND' }),
    });
    return res.json();
  },

  /**
   * Fetch GeoJSON layer data
   */
  async getGeoJsonLayer(projectId) {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/layers/parcels.geojson`);
    return res.json();
  },
};
