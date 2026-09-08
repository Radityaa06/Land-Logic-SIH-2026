import React, { useState } from 'react';

/**
 * UploadZone Component
 * Drag-and-drop batch upload for drone flight imagery
 */
export default function UploadZone({ onUploadSelected, isUploading }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedCount, setSelectedCount] = useState(0);

  const handleFiles = (e) => {
    const files = Array.from(e.target.files || []);
    setSelectedCount(files.length);
    if (onUploadSelected) onUploadSelected(files);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const files = Array.from(e.dataTransfer.files || []);
        setSelectedCount(files.length);
        if (onUploadSelected) onUploadSelected(files);
      }}
      style={{
        border: `2px dashed ${dragOver ? '#38bdf8' : '#475569'}`,
        borderRadius: '12px',
        padding: '36px 20px',
        textAlign: 'center',
        background: dragOver ? 'rgba(56, 189, 248, 0.05)' : '#1e293b',
        transition: 'all 0.2s ease',
        cursor: 'pointer'
      }}
    >
      <input
        type="file"
        multiple
        accept="image/jpeg,image/png,image/tiff"
        id="drone-file-input"
        style={{ display: 'none' }}
        onChange={handleFiles}
      />
      <label htmlFor="drone-file-input" style={{ cursor: 'pointer' }}>
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>🚁</div>
        <h3 style={{ margin: '0 0 4px', color: '#f1f5f9', fontSize: '16px' }}>
          Drop Drone Flight Images Here
        </h3>
        <p style={{ margin: '0 0 12px', color: '#94a3b8', fontSize: '13px' }}>
          Supports JPG, PNG, DNG with EXIF GPS tags
        </p>
        <div style={{
          display: 'inline-block',
          background: '#0284c7',
          color: '#ffffff',
          padding: '8px 16px',
          borderRadius: '6px',
          fontSize: '13px',
          fontWeight: 500
        }}>
          {isUploading ? 'Uploading Imagery...' : selectedCount > 0 ? `${selectedCount} Images Selected` : 'Select Flight Batch'}
        </div>
      </label>
    </div>
  );
}
