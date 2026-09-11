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
    </div>
  );
}
