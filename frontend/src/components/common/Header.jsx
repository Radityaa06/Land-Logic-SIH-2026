import React from 'react';

/**
 * Header Component
 * Member 1: Frontend & UI/UX
 * Workspace: frontend/src/components/common/
 * Branch: feature/react-frontend
 */
export default function Header({ projectId, isProcessing }) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 24px',
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid #1e293b',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '18px',
          boxShadow: '0 2px 10px rgba(37, 99, 235, 0.4)'
        }}>
          🛰️
        </div>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: 700,
            color: '#f8fafc',
            letterSpacing: '-0.3px'
          }}>
            Land Logic <span style={{ color: '#38bdf8', fontWeight: 500, fontSize: '13px' }}>SIH 2026</span>
          </h1>
          <p style={{ margin: 0, fontSize: '11px', color: '#94a3b8' }}>
            Drone-Based Autonomous Land Analysis & Geospatial Mapping
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Project Selector Badge */}
        <div style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '6px',
          padding: '6px 12px',
          fontSize: '12px',
          color: '#e2e8f0',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ color: '#94a3b8' }}>Session:</span>
          <span style={{ fontWeight: 600, color: '#38bdf8' }}>{projectId || 'Default Flight'}</span>
        </div>

        {/* Live Status Indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          padding: '6px 12px',
          borderRadius: '6px',
          background: isProcessing ? 'rgba(234, 179, 8, 0.15)' : 'rgba(34, 197, 94, 0.15)',
          color: isProcessing ? '#fde047' : '#4ade80',
          border: `1px solid ${isProcessing ? 'rgba(234, 179, 8, 0.3)' : 'rgba(34, 197, 94, 0.3)'}`
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isProcessing ? '#fde047' : '#4ade80',
            animation: isProcessing ? 'pulse 1.5s infinite' : 'none'
          }} />
          <span>{isProcessing ? 'Pipeline Processing...' : 'Ready for Ingestion'}</span>
        </div>
      </div>
    </header>
  );
}
