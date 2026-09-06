const VesselInvestigationPanel = ({
  vessel,
  isSelected,
  onClose,
  isPlaying,
  currentTime,
  duration,
  progress,
  onPlayPause,
  onStop,
  formatTime
}) => {
  if (!vessel || !isSelected) {
    return null;
  }

  const associationScore = vessel?.attribution_score || 0;
  const spatialScore = vessel?.spatial_consistency || 0;
  const temporalScore = vessel?.temporal_consistency || 0;
  const trajectoryScore = vessel?.trajectory_consistency || 0;

  // Calculate deterministic distance and direction from vessel position to spill
  // Spill center is at 18.95, 71.85 (from demo data)
  const SPILL_LAT = 18.95;
  const SPILL_LON = 71.85;
  const vesselLat = vessel?.coordinates?.lat || SPILL_LAT;
  const vesselLon = vessel?.coordinates?.lon || SPILL_LON;

  // Haversine distance in km
  const R = 6371.0;
  const dLat = (vesselLat - SPILL_LAT) * Math.PI / 180;
  const dLon = (vesselLon - SPILL_LON) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(SPILL_LAT * Math.PI / 180) * Math.cos(vesselLat * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  const distanceKm = 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  // Bearing from spill to vessel
  const y = Math.sin(dLon) * Math.cos(vesselLat * Math.PI / 180);
  const x = Math.cos(SPILL_LAT * Math.PI / 180) * Math.sin(vesselLat * Math.PI / 180) -
    Math.sin(SPILL_LAT * Math.PI / 180) * Math.cos(vesselLat * Math.PI / 180) * Math.cos(dLon);
  const bearingDeg = (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const direction = directions[Math.round(bearingDeg / 45) % 8];

  return (
    <div className={`vessel-investigation-panel ${isSelected ? 'open' : ''}`}>
      <div className="panel-header">
        <h2>
          <span>⊙</span>
          VESSEL INVESTIGATION
        </h2>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="panel-content">
        <div className="vessel-info">
          <div className="info-row">
            <span className="label">VESSEL ID</span>
            <span className="value">{vessel.vessel_id}</span>
          </div>
          <div className="info-row">
            <span className="label">VESSEL NAME</span>
            <span className="value">{vessel.name}</span>
          </div>
          <div className="info-row">
            <span className="label">AIS TIMESTAMP</span>
            <span className="value">{vessel.timestamp}</span>
          </div>
          <div className="info-row">
            <span className="label">PROXIMITY</span>
            <span className="value">{distanceKm.toFixed(1)} km {direction}</span>
          </div>
        </div>

        <div className="assessment-section">
          <h3>⚠ SPILL ASSOCIATION</h3>
          <div className="association-score-display">
            <div className="score-bar-wrapper">
              <div className="score-bar">
                <div className="score-fill" style={{ width: `${associationScore * 100}%` }}></div>
              </div>
              <span className="score-value">{(associationScore * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        <div className="assessment-section">
          <h3>PROXIMITY</h3>
          <div className="score-bar-wrapper">
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${spatialScore * 100}%` }}></div>
            </div>
            <span className="score-label">SPATIAL CONSISTENCY</span>
            <span className="score-value">{(spatialScore * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="assessment-section">
          <h3>TEMPORAL CORRELATION</h3>
          <div className="score-bar-wrapper">
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${temporalScore * 100}%` }}></div>
            </div>
            <span className="score-label">TEMPORAL CONSISTENCY</span>
            <span className="score-value">{(temporalScore * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="assessment-section">
          <h3>TRAJECTORY</h3>
          <div className="score-bar-wrapper">
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${trajectoryScore * 100}%` }}></div>
            </div>
            <span className="score-label">TRAJECTORY CONSISTENCY</span>
            <span className="score-value">{(trajectoryScore * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="assessment-conclusion">
          <div className="conclusion-header">
            {associationScore >= 0.6 ? 'HIGHER POTENTIAL ASSOCIATION' :
             associationScore >= 0.3 ? 'MODERATE POTENTIAL ASSOCIATION' :
             'LOWER POTENTIAL ASSOCIATION'}
          </div>
        </div>

        <div className="disclaimer">
          ⓘ Attribution score is investigative ranking based on demonstrative correlation factors. NOT proof of causation or legal guilt. Vessel positions and trajectories are prototype data.
        </div>
      </div>

      {/* Playback footer for prototype vessels */}
      {vessel.prototype && (
        <div className="panel-footer">
          <div className="playback-header">
            <span className="playback-title">VESSEL TRAJECTORY PLAYBACK</span>
          </div>

          <div className="playback-controls">
            <button className="playback-btn" onClick={onPlayPause}>
              {isPlaying ? '❚❚' : '▶'}
            </button>
            <button className="playback-btn" onClick={onStop}>
              ◼
            </button>
          </div>

          <div className="playback-timeline">
            <div className="timeline-bar">
              <div className="timeline-progress" style={{ width: `${progress}%` }} />
              <div className="timeline-handle" />
            </div>
            <div className="timeline-display">
              <span className="time-current">{formatTime(currentTime)}</span>
              <span className="time-divider"> / </span>
              <span className="time-duration">{formatTime(duration)}</span>
            </div>
          </div>

          <div className="playback-disclaimer">
            <span className="disclaimer-text">PROTOTYPE VISUALIZATION DATA</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default VesselInvestigationPanel;