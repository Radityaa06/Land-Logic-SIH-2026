import React from 'react';

/**
 * MetricsPanel Component
 * Member 1: Frontend & UI/UX
 * Workspace: frontend/src/components/results/
 * Branch: feature/react-frontend
 *
 * Summarizes survey area, NDVI health, parcel count, and coordinate space indicators.
 */
export default function MetricsPanel({ metrics }) {
  const data = metrics || {
    totalAreaHa: 14.8,
    vegetationPct: 76.4,
    meanNdvi: 0.71,
    parcelsIdentified: 4,
    coordinateSpace: 'pixel'
  };

  const healthSummary = data.cropHealthSummary || data.crop_health_summary || {
    healthy: 3,
    moderate: 1,
    stressed: 0
  };

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
      gap: '12px'
    }}>
      <div style={{
        background: '#0f172a',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid #1e293b',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Estimated Area
        </div>
        <div style={{ color: '#f8fafc', fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>
          {data.totalAreaHa || 12.5} <span style={{ fontSize: '13px', fontWeight: 400, color: '#64748b' }}>ha</span>
        </div>
      </div>

      <div style={{
        background: '#0f172a',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid #1e293b',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Vegetation Cover
        </div>
        <div style={{ color: '#22c55e', fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>
          {data.vegetationPct || 78}%
        </div>
      </div>

      <div style={{
        background: '#0f172a',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid #1e293b',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Mean VARI / NDVI
        </div>
        <div style={{ color: '#38bdf8', fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>
          {data.meanNdvi || data.mean_vari || 0.72}
        </div>
      </div>

      <div style={{
        background: '#0f172a',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid #1e293b',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Parcels Detected
        </div>
        <div style={{ color: '#f8fafc', fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>
          {data.parcelsIdentified || data.detected_parcels || 4}
        </div>
      </div>

      <div style={{
        background: '#0f172a',
        padding: '16px',
        borderRadius: '10px',
        border: '1px solid #1e293b',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Crop Health (VARI)
        </div>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginTop: '8px', flexWrap: 'wrap' }}>
          <span
            title="Healthy Parcels (VARI ≥ 0.20)"
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#4ade80',
              background: 'rgba(34, 197, 94, 0.15)',
              padding: '3px 7px',
              borderRadius: '4px',
              border: '1px solid rgba(34, 197, 94, 0.3)'
            }}
          >
            🟢 {healthSummary.healthy ?? 0}
          </span>
          <span
            title="Moderate Parcels (0.05 ≤ VARI < 0.20)"
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#facc15',
              background: 'rgba(250, 204, 21, 0.15)',
              padding: '3px 7px',
              borderRadius: '4px',
              border: '1px solid rgba(250, 204, 21, 0.3)'
            }}
          >
            🟡 {healthSummary.moderate ?? 0}
          </span>
          <span
            title="Stressed Parcels (VARI < 0.05)"
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#f87171',
              background: 'rgba(239, 68, 68, 0.15)',
              padding: '3px 7px',
              borderRadius: '4px',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}
          >
            🔴 {healthSummary.stressed ?? 0}
          </span>
        </div>
      </div>
    </div>
  );
}
