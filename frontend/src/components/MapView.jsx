import React from 'react';

/**
 * MapView Component
 * Renders satellite basemap with raster orthomosaic and GeoJSON vector overlays
 */
export default function MapView({ geojsonData, rasterOverlayUrl }) {
  return (
    <div style={{
      width: '100%',
      height: '600px',
      borderRadius: '12px',
      overflow: 'hidden',
      position: 'relative',
      background: '#0f172a',
      border: '1px solid #334155'
    }}>
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        zIndex: 10,
        background: 'rgba(15, 23, 42, 0.85)',
        backdropFilter: 'blur(8px)',
        padding: '10px 16px',
        borderRadius: '8px',
        color: '#f8fafc',
        fontSize: '13px',
        border: '1px solid #475569'
      }}>
        <div style={{ fontWeight: 600 }}>🛰️ Map Layer: Drone Aerial Composite</div>
        <div style={{ color: '#94a3b8', fontSize: '11px' }}>
          {geojsonData ? `${geojsonData.features?.length || 0} parcels detected` : 'No layer loaded'}
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        color: '#64748b',
        flexDirection: 'column',
        gap: '8px'
      }}>
        <div style={{ fontSize: '28px' }}>🗺️</div>
        <div>Leaflet / Mapbox Map Container Ready</div>
        <div style={{ fontSize: '12px', color: '#475569' }}>
          Connect map tiles or load GeoJSON vectors from Member 5
        </div>
      </div>
    </div>
  );
}
