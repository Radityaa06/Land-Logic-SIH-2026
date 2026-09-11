import React from 'react';

export default function RasterLayer({ imageUrl, opacity = 0.85 }) {
  if (!imageUrl) return null;

  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      pointerEvents: 'none',
      opacity: opacity,
      zIndex: 400,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <img
        src={imageUrl}
        alt="Orthomosaic Overlay"
        style={{
          maxWidth: '90%',
          maxHeight: '90%',
          objectFit: 'contain',
          border: '1px solid rgba(56, 189, 248, 0.4)',
          borderRadius: '8px',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.6)'
        }}
      />
    </div>
  );
}
