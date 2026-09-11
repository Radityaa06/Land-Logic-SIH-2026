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
    </div>
  );
}
