import React from 'react';

/**
 * MetricsPanel Component
 * Summarizes survey area, NDVI health, and land parcels
 */
export default function MetricsPanel({ metrics }) {
  const data = metrics || {
    totalAreaHa: 14.8,
    vegetationPct: 76.4,
    meanNdvi: 0.71,
    parcelsIdentified: 9
  };

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
      gap: '12px'
    }}>
      <div style={{ background: '#1e293b', padding: '14px', borderRadius: '10px', border: '1px solid #334155' }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Survey Area</div>
        <div style={{ color: '#f8fafc', fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>
          {data.totalAreaHa} <span style={{ fontSize: '13px', fontWeight: 400, color: '#64748b' }}>ha</span>
        </div>
      </div>

      <div style={{ background: '#1e293b', padding: '14px', borderRadius: '10px', border: '1px solid #334155' }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Vegetation Cover</div>
        <div style={{ color: '#22c55e', fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>
          {data.vegetationPct}%
        </div>
      </div>

      <div style={{ background: '#1e293b', padding: '14px', borderRadius: '10px', border: '1px solid #334155' }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Mean NDVI</div>
        <div style={{ color: '#38bdf8', fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>
          {data.meanNdvi}
        </div>
      </div>

      <div style={{ background: '#1e293b', padding: '14px', borderRadius: '10px', border: '1px solid #334155' }}>
        <div style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'uppercase' }}>Parcels Detected</div>
        <div style={{ color: '#e2e8f0', fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>
          {data.parcelsIdentified}
        </div>
      </div>
    </div>
  );
}
