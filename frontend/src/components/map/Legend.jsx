import React from 'react';

export const CLASS_COLORS = {
  agricultural_land: '#22c55e',   // Green
  barren_soil: '#f59e0b',         // Amber / Soil
  forests: '#15803d',             // Dark Forest Green
  water_bodies: '#0ea5e9',        // Cyan / Blue
  man_made_structures: '#ec4899', // Magenta / Pink
  unclassified: '#94a3b8'
};

export const CLASS_LABELS = {
  agricultural_land: 'Agricultural Land',
  barren_soil: 'Barren Soil',
  forests: 'Forest Canopy',
  water_bodies: 'Water Bodies',
  man_made_structures: 'Structures & Roads',
  unclassified: 'Unclassified'
};

export const CROP_HEALTH_COLORS = {
  healthy: '#22c55e',   // Emerald Green
  moderate: '#facc15',  // Amber / Moderate
  stressed: '#ef4444',  // Rose / Stressed
  not_applicable: '#64748b'
};

export const CROP_HEALTH_LABELS = {
  healthy: 'Healthy (VARI ≥ 0.20)',
  moderate: 'Moderate (0.05–0.20)',
  stressed: 'Stressed (VARI < 0.05)'
};

export default function Legend() {
  return (
    <div className="map-legend-overlay">
      <div className="map-legend-title">Land Classification</div>
      {Object.entries(CLASS_LABELS).filter(([k]) => k !== 'unclassified').map(([clsKey, label]) => (
        <div key={clsKey} className="map-legend-row">
          <span
            className="map-legend-color"
            style={{ backgroundColor: CLASS_COLORS[clsKey] || '#94a3b8' }}
          />
          <span>{label}</span>
        </div>
      ))}

      <div className="map-legend-title" style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid #334155' }}>
        Crop Health & Stress (VARI)
      </div>
      {Object.entries(CROP_HEALTH_LABELS).map(([healthKey, label]) => (
        <div key={healthKey} className="map-legend-row">
          <span
            className="map-legend-color"
            style={{
              backgroundColor: CROP_HEALTH_COLORS[healthKey],
              borderRadius: '50%'
            }}
          />
          <span>{label}</span>
        </div>
      ))}
    </div>
  );
}
