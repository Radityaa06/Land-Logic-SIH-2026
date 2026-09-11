import React from 'react';

/**
 * PipelineStatus Component
 * Member 1: Frontend & UI/UX
 * Workspace: frontend/src/components/common/
 * Branch: feature/react-frontend
 *
 * Visualizes execution stages across Members 4 (OpenCV), 3 (AI), and 5 (GIS).
 */
export default function PipelineStatus({ stage, progressPct, statusMessage }) {
  const stages = [
    { key: 'UPLOAD', label: '1. Ingestion', member: 'M1 & M2' },
    { key: 'OPENCV_STITCHING', label: '2. OpenCV Stitch', member: 'M4' },
    { key: 'AI_SEGMENTATION', label: '3. AI Land Vision', member: 'M3' },
    { key: 'GIS_GEOREFERENCING', label: '4. GIS Georef', member: 'M5' },
    { key: 'COMPLETE', label: '5. Map Visualizer', member: 'M6' },
  ];

  return (
    <div style={{
      background: '#0f172a',
      borderRadius: '10px',
      padding: '16px',
      border: '1px solid #1e293b'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '10px'
      }}>
        <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          6-Member Autonomous Pipeline Progress
        </div>
        <div style={{ fontSize: '12px', color: '#38bdf8', fontWeight: 600 }}>
          {progressPct || 0}%
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{
        height: '6px',
        background: '#1e293b',
        borderRadius: '3px',
        overflow: 'hidden',
        marginBottom: '14px'
      }}>
        <div style={{
          height: '100%',
          width: `${progressPct || 0}%`,
          background: 'linear-gradient(90deg, #38bdf8, #22c55e)',
          borderRadius: '3px',
          transition: 'width 0.4s ease'
        }} />
      </div>

      {/* Stages Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: '6px'
      }}>
        {stages.map((s, idx) => {
          const isCurrent = stage === s.key;
          return (
            <div key={s.key} style={{
              background: isCurrent ? 'rgba(56, 189, 248, 0.15)' : '#090d16',
              border: `1px solid ${isCurrent ? '#38bdf8' : '#1e293b'}`,
              borderRadius: '6px',
              padding: '6px 8px',
              textAlign: 'center'
            }}>
              <div style={{
                color: isCurrent ? '#38bdf8' : '#e2e8f0',
                fontSize: '11px',
                fontWeight: isCurrent ? 600 : 400
              }}>
                {s.label}
              </div>
              <div style={{ color: '#64748b', fontSize: '9px', marginTop: '2px' }}>
                {s.member}
              </div>
            </div>
          );
        })}
      </div>

      {statusMessage && (
        <div style={{ color: '#94a3b8', fontSize: '11px', marginTop: '10px', textAlign: 'center' }}>
          {statusMessage}
        </div>
      )}
    </div>
  );
}
