import { useEffect } from 'react';

const VesselPlaybackControl = ({ vessel, isPlaying, currentTime, duration, progress, onPlayPause, onStop, formatTime }) => {

  return (
    <div className="vessel-playback-control">
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
  );
};

export default VesselPlaybackControl;