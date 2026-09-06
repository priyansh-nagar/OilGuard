import { useState, useRef } from "react";

export default function UploadPanel({ onResult, disabled }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  function handleFileChange(event) {
    const selectedFile = event.target.files[0] || null;
    setFile(selectedFile);

    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (file) {
      onResult(file);
    }
  }

  function handleUploadClick() {
    fileInputRef.current?.click();
  }

  function handleClear() {
    setFile(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  return (
    <form className="sar-analysis-panel" onSubmit={handleSubmit}>
      <div className="sar-header">
        <span className="sar-title">SAR SCENE ANALYSIS</span>
      </div>

      {!file ? (
        <>
          <div className="sar-prompt">
            <span className="sar-prompt-text">DROP / SELECT SAR IMAGE</span>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />

          <button
            type="button"
            className="sar-upload-btn"
            onClick={handleUploadClick}
          >
            + UPLOAD SCENE
          </button>

          <div className="sar-status">
            <span className="sar-status-label">STATUS</span>
            <span className="sar-status-value">READY</span>
          </div>
        </>
      ) : (
        <>
          {preview && (
            <div className="sar-preview">
              <img src={preview} alt="SAR Scene Preview" />
            </div>
          )}

          <div className="sar-filename">{file.name}</div>

          <div className="sar-action-buttons">
            <button
              type="submit"
              className="sar-analyze-btn"
              disabled={disabled}
            >
              {disabled ? 'ANALYZING…' : 'ANALYZE SAR SCENE'}
            </button>
            <button
              type="button"
              className="sar-clear-btn"
              onClick={handleClear}
              disabled={disabled}
            >
              CLEAR
            </button>
          </div>

          <div className="sar-status">
            <span className="sar-status-label">STATUS</span>
            <span className="sar-status-value">{disabled ? 'PROCESSING' : 'READY'}</span>
          </div>
        </>
      )}
    </form>
  );
}
