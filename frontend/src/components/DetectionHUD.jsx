import { useEffect, useState } from 'react';

const DetectionHUD = ({ spillResult, loading }) => {
  const [confidencePercent, setConfidencePercent] = useState(0);

  useEffect(() => {
    if (spillResult && spillResult.confidence !== undefined) {
      const targetConfidence = Math.round(spillResult.confidence * 100);
      let current = 0;
      const interval = setInterval(() => {
        current += 3;
        if (current >= targetConfidence) {
          current = targetConfidence;
          clearInterval(interval);
        }
        setConfidencePercent(current);
      }, 30);
      return () => clearInterval(interval);
    } else {
      setConfidencePercent(0);
    }
  }, [spillResult]);

  const isDetected = spillResult?.detected === true;
  const hasAnalysis = spillResult !== null;

  // Determine status text
  let statusText, statusClass;
  if (loading) {
    statusText = 'ANALYZING SAR SCENE';
    statusClass = 'awaiting';
  } else if (hasAnalysis) {
    statusText = isDetected ? 'OIL SPILL DETECTED' : 'NO OIL SPILL DETECTED';
    statusClass = isDetected ? 'detected' : 'clear';
  } else {
    statusText = 'AWAITING SAR SCENE';
    statusClass = 'awaiting';
  }

  return (
    <div className="detection-hud">
      <div className="hud-header">
        <span className="hud-title">DETECTION STATUS</span>
      </div>

      <div className={`hud-status ${statusClass}`}>
        {statusText}
      </div>

      {hasAnalysis && (
        <div className="hud-section">
          <div className="hud-row">
            <span className="hud-label">AI CONFIDENCE</span>
            <span className="hud-value">{confidencePercent}%</span>
          </div>
          <div className="hud-progress">
            <div
              className="hud-progress-bar"
              style={{ width: `${confidencePercent}%` }}
            />
            <div className="hud-threshold-marker" style={{ left: '52%' }} />
          </div>
          <div className="hud-row threshold-row">
            <span className="hud-label">THRESHOLD</span>
            <span className="hud-value">0.52</span>
          </div>
        </div>
      )}

      <div className="hud-section">
        <div className="hud-row">
          <span className="hud-label">MODEL</span>
          <span className="hud-value">SMALLCNN</span>
        </div>
        <div className="hud-row">
          <span className="hud-label">THRESHOLD</span>
          <span className="hud-value">0.52</span>
        </div>
      </div>

      {hasAnalysis && (
        <>
          <div className="hud-section">
            <div className="hud-row">
              <span className="hud-label">TIMESTAMP</span>
              <span className="hud-value">{new Date().toISOString().slice(0, 19).replace('T', ' ')}</span>
            </div>
          </div>

          <div className="hud-section">
            <div className="hud-row">
              <span className="hud-label">COORDINATES</span>
              <span className="hud-value prototype">PROTOTYPE</span>
            </div>
          </div>

          <div className="hud-section">
            <div className="hud-row">
              <span className="hud-label">AREA</span>
              <span className="hud-value prototype">PROTOTYPE</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DetectionHUD;