import React from 'react';
import { CLASS_LABELS, CROP_HEALTH_COLORS } from './Legend';

export default function FeaturePopup({ feature, onClose }) {
  if (!feature) return null;
  const props = feature.properties || {};

  const getCropHealthBadge = (health) => {
    switch (health) {
      case 'healthy':
        return { label: '🟢 Healthy', color: CROP_HEALTH_COLORS.healthy, bg: 'rgba(34, 197, 94, 0.15)', border: 'rgba(34, 197, 94, 0.4)' };
      case 'moderate':
        return { label: '🟡 Moderate', color: CROP_HEALTH_COLORS.moderate, bg: 'rgba(250, 204, 21, 0.15)', border: 'rgba(250, 204, 21, 0.4)' };
      case 'stressed':
        return { label: '🔴 Stressed', color: CROP_HEALTH_COLORS.stressed, bg: 'rgba(239, 68, 68, 0.15)', border: 'rgba(239, 68, 68, 0.4)' };
      default:
        return null;
    }
  };

  const healthBadge = getCropHealthBadge(props.crop_health);

  return (
    <div className="custom-feature-popup" style={{
      position: 'absolute',
      bottom: '20px',
      right: '20px',
      zIndex: 1100,
      minWidth: '220px',
      background: 'rgba(15, 23, 42, 0.95)',
      border: '1px solid #38bdf8',
      borderRadius: '8px',
      padding: '12px',
      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: 0 }}>{props.parcel_id || 'Parcel Inspection'}</h4>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            fontSize: '14px',
            lineHeight: 1
          }}
        >
          ✕
        </button>
      </div>

      <div style={{ marginTop: '8px', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div>
          <span style={{ color: '#94a3b8' }}>Class: </span>
          <strong style={{ color: '#f8fafc' }}>
            {CLASS_LABELS[props.class] || props.class}
          </strong>
        </div>
        <div>
          <span style={{ color: '#94a3b8' }}>Confidence: </span>
          <strong style={{ color: '#38bdf8' }}>
            {props.confidence ? `${Math.round(props.confidence * 100)}%` : 'N/A'}
          </strong>
        </div>
        {props.mean_vari !== undefined && (
          <div>
            <span style={{ color: '#94a3b8' }}>Mean VARI: </span>
            <strong style={{ color: '#4ade80' }}>{props.mean_vari}</strong>
          </div>
        )}
        {healthBadge && (
          <div>
            <span style={{ color: '#94a3b8' }}>Crop Health: </span>
            <span style={{
              display: 'inline-block',
              padding: '2px 7px',
              borderRadius: '4px',
              fontSize: '11px',
              fontWeight: 600,
              backgroundColor: healthBadge.bg,
              color: healthBadge.color,
              border: `1px solid ${healthBadge.border}`
            }}>
              {healthBadge.label}
            </span>
          </div>
        )}
        <div>
          <span style={{ color: '#94a3b8' }}>Coordinate Space: </span>
          <span style={{
            color: props.coordinate_space === 'geographic' ? '#4ade80' : '#fde047',
            fontWeight: 600,
            textTransform: 'uppercase',
            fontSize: '11px'
          }}>
            {props.coordinate_space || 'pixel'}
          </span>
        </div>
      </div>
    </div>
  );
}
