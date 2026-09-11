import React from 'react';
import { CLASS_LABELS } from './Legend';

export default function FeaturePopup({ feature, onClose }) {
  if (!feature) return null;
  const props = feature.properties || {};

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
