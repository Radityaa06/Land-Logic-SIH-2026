/**
 * Land Logic DRONE-MAPPING-AI — Frontend API Client
 * Member 1: Frontend & UI/UX
 * Connects Member 1's UI to Member 2's FastAPI Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const ROOT_URL = import.meta.env.VITE_ROOT_URL || 'http://localhost:8000';

export const api = {
  /**
   * Unified Pipeline Ingestion Endpoint:
   * Sends drone frames directly through Member 2's central orchestrator
   * (OpenCV -> AI -> GIS -> Backend -> Frontend)
   */
  async predictDirect(files = [], projectId = null) {
    const formData = new FormData();
    if (projectId) {
      formData.append('project_id', projectId);
    }
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    const res = await fetch(`${ROOT_URL}/predict`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      throw new Error(`Pipeline failed with status ${res.status}`);
    }
    return res.json();
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
