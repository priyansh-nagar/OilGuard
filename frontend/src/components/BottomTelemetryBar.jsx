import { useEffect, useState } from 'react';

const BottomTelemetryBar = ({ result, loading }) => {
  const [inferenceStatus, setInferenceStatus] = useState('READY');

  useEffect(() => {
    if (loading) {
      setInferenceStatus('PROCESSING');
    } else if (result) {
      setInferenceStatus('COMPLETE');
    } else {
      setInferenceStatus('READY');
    }
  }, [loading, result]);

  return (
    <div className="bottom-telemetry-bar">
      <div className="telemetry-content">
        <div className="telemetry-item">
          <span className="telemetry-label">MODEL</span>
          <span className="telemetry-value">SMALLCNN</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">THRESHOLD</span>
          <span className="telemetry-value">0.52</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">INFERENCE</span>
          <span className="telemetry-value">{inferenceStatus}</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">DATA SOURCE</span>
          <span className="telemetry-value prototype">
            {result ? 'UPLOADED SAR' : 'NONE'}
          </span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">SYSTEM</span>
          <span className="telemetry-value">ONLINE</span>
        </div>
      </div>
    </div>
  );
};

export default BottomTelemetryBar;