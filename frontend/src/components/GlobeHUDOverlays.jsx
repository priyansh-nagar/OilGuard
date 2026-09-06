import { useEffect } from 'react';

const GlobeHUDOverlays = ({ spillResult, vessels, selectedVessel }) => {
  // Count real API vessels (from analysis result)
  const realVesselCount = vessels ? vessels.length : 0;

  // Always include 3 hardcoded prototype vessels for mission visualization
  const prototypeVesselCount = 3;

  // Total vessel count (prototype vessels always present, plus real vessels after analysis)
  const vesselCount = prototypeVesselCount + realVesselCount;

  const detectionCount = spillResult?.detected === true ? 1 : 0;

  useEffect(() => {
    // Overlays update based on spillResult, vessels, selectedVessel
  }, [spillResult, vessels, selectedVessel]);

  return (
    <div className="globe-overlays">
      {/* Mission area indicator - top left */}
      <div className="mission-indicator">
        <div className="mission-label">MISSION AREA</div>
        <div className="mission-status">ACTIVE</div>
      </div>

      {/* Coordinate readouts - corners */}
      <div className="coord-readout coord-top-left">
        <span className="coord-label">LAT</span>
        <span className="coord-value">18.950° N</span>
      </div>
      <div className="coord-readout coord-top-right">
        <span className="coord-label">LON</span>
        <span className="coord-value">71.850° E</span>
      </div>
      <div className="coord-readout coord-bottom-left">
        <span className="coord-label">SAR FEED</span>
        <span className="coord-value">READY</span>
      </div>
      <div className="coord-readout coord-bottom-right">
        <span className="coord-label">TRACKS</span>
        <span className="coord-value">{vesselCount}</span>
      </div>

      {/* Detections indicator */}
      <div className="detections-indicator">
        <span className="detections-label">DETECTIONS</span>
        <span className="detections-value">{detectionCount}</span>
      </div>

      {/* Central targeting reticle */}
      <div className="target-reticle">
        <div className="reticle-center"></div>
        <div className="reticle-cross">
          <div className="reticle-h"></div>
          <div className="reticle-v"></div>
        </div>
        <div className="reticle-ring"></div>
        <div className="reticle-ring" style={{ animationDelay: '0.3s' }}></div>
      </div>

      {/* Subtle radar rings */}
      <div className="radar-rings">
        <div className="radar-ring"></div>
        <div className="radar-ring" style={{ animationDelay: '0.5s' }}></div>
        <div className="radar-ring" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Faint technical grid background */}
      <div className="technical-grid"></div>
    </div>
  );
};

export default GlobeHUDOverlays;