import React, { useState, useEffect, useRef } from 'react';
import './map.css';
import Legend, { CLASS_COLORS, CLASS_LABELS } from './Legend';
import LayerControl from './LayerControl';
import FeaturePopup from './FeaturePopup';
import RasterLayer from './RasterLayer';

/**
 * GeoParcelCanvas Component — custom SVG parcel visualization (not Leaflet)
 * Member 6: Leaflet / Interactive Map
 * Workspace: frontend/src/components/map/
 * Branch: feature/leaflet-map
 *
 * Renders custom SVG parcel boundaries and orthomosaic raster overlays.
 * Strictly respects 'coordinate_space' ('geographic' vs 'pixel') so non-georeferenced
 * drone imagery is visualized accurately without misleading world tiles.
 */
export default function LeafletMap({
  geojsonData,
  rasterOverlayUrl,
  selectedFeature,
  onSelectFeature
}) {
  const [layers, setLayers] = useState({
    satellite: true,
    orthomosaic: true,
    parcels: true,
    heatmap: false
  });
  const [activeFeature, setActiveFeature] = useState(null);
  const [geojsonError, setGeojsonError] = useState(null);

  const toggleLayer = (layerKey) => {
    setLayers((prev) => ({ ...prev, [layerKey]: !prev[layerKey] }));
  };

  const coordSpace = geojsonData?.coordinate_space || 'pixel';
  const features = geojsonData?.features || [];

  // Coordinate bounding box calculation for responsive canvas fitting
  const getBounds = () => {
    if (!features.length) return null;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    features.forEach((feat) => {
      const coords = feat.geometry?.coordinates?.[0] || [];
      coords.forEach(([x, y]) => {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      });
    });

    if (minX === Infinity) return null;
    return { minX, minY, maxX, maxY, width: maxX - minX || 1, height: maxY - minY || 1 };
  };

  const bounds = getBounds();

  return (
    <div className="map-wrapper" id="leaflet-map-container">
      {/* Top Left Status Badge */}
      <div className="map-badge-overlay">
        <div className="map-badge">
          <div className="map-badge-title">
            <span>🛰️</span>
            <span>Drone Geospatial Canvas</span>
          </div>
          <div className="map-badge-meta">
            {features.length > 0 ? `${features.length} parcels identified` : 'Ready for flight data'}
          </div>
          <span className={`coord-space-tag ${coordSpace === 'geographic' ? 'coord-space-geo' : 'coord-space-pixel'}`}>
            {coordSpace === 'geographic' ? '✓ Geographic (WGS84 GPS)' : '⚡ Pixel Space (Preserved Drone Coordinates)'}
          </span>
        </div>
      </div>

      {/* Layer Control on Top Right */}
      <LayerControl layers={layers} onToggleLayer={toggleLayer} />

      {/* Legend on Bottom Left */}
      <Legend />

      {/* Active Feature Inspector Popup */}
      <FeaturePopup
        feature={activeFeature || selectedFeature}
        onClose={() => setActiveFeature(null)}
      />

      {/* Stitched Orthomosaic Raster Layer */}
      {layers.orthomosaic && rasterOverlayUrl && (
        <RasterLayer imageUrl={rasterOverlayUrl} />
      )}

      {/* Interactive Vector Overlay */}
      {features.length === 0 ? (
        <div className="map-empty-state">
          <div className="map-empty-icon">🗺️</div>
          <h3 style={{ color: '#f1f5f9', margin: '0 0 6px 0', fontSize: '16px' }}>
            Awaiting Drone Imagery & Pipeline Outputs
          </h3>
          <p style={{ color: '#94a3b8', margin: 0, fontSize: '13px', maxWidth: '420px' }}>
            Upload flight images through Member 1's upload zone to trigger the backend pipeline
            and visualize classified land parcels here.
          </p>
        </div>
      ) : (
        <div className="map-container" style={{ position: 'relative', overflow: 'hidden' }}>
          {/* Base Grid / Basemap */}
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 1000 600"
            preserveAspectRatio="xMidYMid meet"
            style={{ display: 'block', background: '#090d16' }}
          >
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.04)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Draw GeoJSON Polygons */}
            {layers.parcels && bounds && features.map((feat, idx) => {
              const ring = feat.geometry?.coordinates?.[0] || [];
              if (ring.length < 3) return null;

              // Project coordinates to 1000x600 SVG viewBox
              const pointsStr = ring.map(([x, y]) => {
                const normX = (x - bounds.minX) / bounds.width;
                // Invert Y for geographic/canvas orientation
                const normY = coordSpace === 'geographic'
                  ? (bounds.maxY - y) / bounds.height
                  : (y - bounds.minY) / bounds.height;
                const svgX = 120 + normX * 760;
                const svgY = 70 + normY * 460;
                return `${svgX},${svgY}`;
              }).join(' ');

              const cls = feat.properties?.class || 'unclassified';
              const strokeColor = CLASS_COLORS[cls] || '#38bdf8';
              const fillColor = strokeColor + '40'; // 25% opacity
              const isSelected = activeFeature?.properties?.parcel_id === feat.properties?.parcel_id;

              return (
                <g key={feat.properties?.parcel_id || idx} style={{ cursor: 'pointer' }}>
                  <polygon
                    points={pointsStr}
                    fill={fillColor}
                    stroke={isSelected ? '#ffffff' : strokeColor}
                    strokeWidth={isSelected ? 3 : 1.5}
                    onClick={() => {
                      setActiveFeature(feat);
                      if (onSelectFeature) onSelectFeature(feat);
                    }}
                  />
                  {/* Parcel label */}
                  {ring[0] && (
                    <text
                      x={120 + ((ring[0][0] - bounds.minX) / bounds.width) * 760}
                      y={70 + ((coordSpace === 'geographic' ? bounds.maxY - ring[0][1] : ring[0][1] - bounds.minY) / bounds.height) * 460 - 8}
                      fill="#ffffff"
                      fontSize="10"
                      fontWeight="bold"
                      textAnchor="middle"
                      style={{ pointerEvents: 'none' }}
                    >
                      {feat.properties?.parcel_id || `P-${idx + 1}`}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        </div>
      )}
    </div>
  );
}
