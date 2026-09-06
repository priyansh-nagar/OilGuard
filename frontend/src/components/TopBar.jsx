import { useEffect, useState, useMemo } from 'react';

const TopBar = ({ selectedVessel, playbackProgress }) => {
  const [utcTime, setUtcTime] = useState('');
  const [coordinates, setCoordinates] = useState({ lat: 18.95, lon: 71.85 }); // Default map center

  // Default map center (Arabian Sea)
  const DEFAULT_COORDINATES = { lat: 18.95, lon: 71.85 };

  // Prototype vessel starting positions
  const prototypeStartPositions = {
    'PROTOTYPE-01': { lat: 19.1, lon: 71.9 },
    'PROTOTYPE-02': { lat: 18.8, lon: 72.1 },
    'PROTOTYPE-03': { lat: 19.3, lon: 71.5 }
  };

  // Prototype vessel trajectories (same as App.jsx)
  const prototypeTrajectories = {
    'PROTOTYPE-01': [[71.9, 19.1], [72.0, 19.15], [72.1, 19.2]],
    'PROTOTYPE-02': [[72.1, 18.8], [72.0, 18.75], [71.95, 18.7]],
    'PROTOTYPE-03': [[71.5, 19.3], [71.6, 19.25], [71.7, 19.2]]
  };

  // Calculate interpolated coordinates from trajectory based on progress
  const getInterpolatedPosition = (trajectory, progress) => {
    if (!trajectory || trajectory.length < 2) return null;

    const progressRatio = Math.min(progress / 100, 1);
    const pointIndex = progressRatio * (trajectory.length - 1);
    const lowerIndex = Math.floor(pointIndex);
    const upperIndex = Math.min(lowerIndex + 1, trajectory.length - 1);
    const segmentProgress = pointIndex - lowerIndex;

    const lowerPoint = trajectory[lowerIndex]; // [lon, lat]
    const upperPoint = trajectory[upperIndex]; // [lon, lat]

    const interpolatedLon = lowerPoint[0] + (upperPoint[0] - lowerPoint[0]) * segmentProgress;
    const interpolatedLat = lowerPoint[1] + (upperPoint[1] - lowerPoint[1]) * segmentProgress;

    return { lat: interpolatedLat, lon: interpolatedLon };
  };

  // Derive current coordinates from selected vessel and playback progress
  const currentCoordinates = useMemo(() => {
    if (!selectedVessel) {
      return DEFAULT_COORDINATES;
    }

    // If it's a prototype vessel with trajectory and we're playing/stopped mid-playback
    if (selectedVessel.prototype && selectedVessel.trajectory && selectedVessel.trajectory.length >= 2) {
      const interpolated = getInterpolatedPosition(selectedVessel.trajectory, playbackProgress);
      if (interpolated) return interpolated;
    }

    // Otherwise use vessel's current/static coordinates
    if (selectedVessel.coordinates) {
      return { lat: selectedVessel.coordinates.lat, lon: selectedVessel.coordinates.lon };
    }

    // Fallback to starting position for prototype vessels
    if (selectedVessel.prototype && prototypeStartPositions[selectedVessel.name]) {
      return prototypeStartPositions[selectedVessel.name];
    }

    return DEFAULT_COORDINATES;
  }, [selectedVessel, playbackProgress]);

  useEffect(() => {
    setCoordinates(currentCoordinates);
  }, [currentCoordinates]);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toISOString().slice(11, 19) + 'Z'); // HH:MM:SSZ format
    };

    // Update time every second
    const interval = setInterval(updateTime, 1000);
    updateTime(); // Initial call

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="top-bar">
      <div className="top-bar-content">
        <div className="branding">
          <span className="label">OILGUARD</span>
          <span className="separator">//</span>
          <span className="label">MARITIME INTELLIGENCE</span>
        </div>

        <div className="status-items">
          <div className="status-item">
            <span className="status-label">SYSTEM</span>
            <span className="status-value">ONLINE</span>
          </div>
          <div className="status-item">
            <span className="status-label">ML INFERENCE</span>
            <span className="status-value">LIVE</span>
          </div>
          <div className="status-item">
            <span className="status-label">UTC</span>
            <span className="status-value">{utcTime}</span>
          </div>
          <div className="status-item coordinates">
            <span className="status-label">POS</span>
            <span className="status-value">
              {coordinates.lat.toFixed(3)}°N, {Math.abs(coordinates.lon).toFixed(3)}°{' '}
              {coordinates.lon >= 0 ? 'E' : 'W'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;