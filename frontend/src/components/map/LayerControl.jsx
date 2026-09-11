import React from 'react';

export default function LayerControl({
  layers,
  onToggleLayer
}) {
  return (
    <div className="map-controls-overlay">
      <div className="map-controls-title">Map Layers</div>
      <label className="map-control-item">
        <input
          type="checkbox"
          checked={layers.satellite}
          onChange={() => onToggleLayer('satellite')}
        />
        <span>Satellite Basemap</span>
      </label>

      <label className="map-control-item">
        <input
          type="checkbox"
          checked={layers.orthomosaic}
          onChange={() => onToggleLayer('orthomosaic')}
        />
        <span>Stitched Orthomosaic</span>
      </label>

      <label className="map-control-item">
        <input
          type="checkbox"
          checked={layers.parcels}
          onChange={() => onToggleLayer('parcels')}
        />
        <span>AI Parcel Polygons</span>
      </label>

      <label className="map-control-item">
        <input
          type="checkbox"
          checked={layers.heatmap}
          onChange={() => onToggleLayer('heatmap')}
        />
        <span>VARI Vegetation Heatmap</span>
      </label>
    </div>
  );
}
