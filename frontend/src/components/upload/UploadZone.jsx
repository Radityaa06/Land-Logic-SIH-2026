import React, { useState } from 'react';

/**
 * UploadZone Component
 * Member 1: Frontend & UI/UX
 * Workspace: frontend/src/components/upload/
 * Branch: feature/react-frontend
 *
 * Drag-and-drop batch upload for drone flight imagery with file preview & validation.
 */
export default function UploadZone({ onUploadSelected, isUploading, selectedFiles = [] }) {
  const [dragOver, setDragOver] = useState(false);
  const [localFiles, setLocalFiles] = useState(selectedFiles);

  const handleFiles = (e) => {
    const files = Array.from(e.target.files || []);
    setLocalFiles(files);
    if (onUploadSelected) onUploadSelected(files);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files || []);
    setLocalFiles(files);
    if (onUploadSelected) onUploadSelected(files);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragOver ? '#38bdf8' : '#334155'}`,
          borderRadius: '12px',
          padding: '32px 20px',
          textAlign: 'center',
          background: dragOver ? 'rgba(56, 189, 248, 0.06)' : '#0f172a',
          transition: 'all 0.2s ease',
          cursor: 'pointer'
        }}
      >
        <input
          type="file"
          multiple
          accept="image/jpeg,image/png,image/tiff,.dng"
          id="drone-file-input"
          style={{ display: 'none' }}
          onChange={handleFiles}
        />
        <label htmlFor="drone-file-input" style={{ cursor: 'pointer' }}>
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>🚁</div>
          <h3 style={{ margin: '0 0 4px', color: '#f8fafc', fontSize: '15px', fontWeight: 600 }}>
            Drop Drone Flight Imagery Here
          </h3>
          <p style={{ margin: '0 0 14px', color: '#94a3b8', fontSize: '12px' }}>
            Supports JPG, PNG, TIFF, DNG with EXIF GPS telemetry
          </p>
          <div style={{
            display: 'inline-block',
            background: isUploading ? '#0284c7' : '#2563eb',
            color: '#ffffff',
            padding: '8px 18px',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: 500,
            boxShadow: '0 2px 8px rgba(37, 99, 235, 0.3)'
          }}>
            {isUploading ? 'Uploading & Processing...' : localFiles.length > 0 ? `${localFiles.length} Images Selected` : 'Select Flight Batch'}
          </div>
        </label>
      </div>

      {/* File Preview Chips */}
      {localFiles.length > 0 && (
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '6px',
          maxHeight: '110px',
          overflowY: 'auto',
          background: '#090d16',
          padding: '8px',
          borderRadius: '8px',
          border: '1px solid #1e293b'
        }}>
          {localFiles.slice(0, 8).map((file, idx) => (
            <div key={idx} style={{
              background: '#1e293b',
              color: '#e2e8f0',
              padding: '4px 10px',
              borderRadius: '4px',
              fontSize: '11px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>📷</span>
              <span style={{ maxWidth: '120px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {file.name}
              </span>
              <span style={{ color: '#64748b' }}>({Math.round(file.size / 1024)} KB)</span>
            </div>
          ))}
          {localFiles.length > 8 && (
            <div style={{ color: '#38bdf8', fontSize: '11px', alignSelf: 'center', padding: '0 6px' }}>
              +{localFiles.length - 8} more files
            </div>
          )}
        </div>
      )}
    </div>
  );
}
