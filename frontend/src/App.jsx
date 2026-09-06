import { useState, useEffect } from "react";
import { analyzeImage } from "./api.js";
import UploadPanel from "./components/UploadPanel.jsx";
import GlobeContainer from "./components/GlobeContainer.jsx";
import VesselInvestigationPanel from "./components/VesselInvestigationPanel.jsx";
import TopBar from "./components/TopBar.jsx";
import LeftSidebar from "./components/LeftSidebar.jsx";
import DetectionHUD from "./components/DetectionHUD.jsx";
import BottomTelemetryBar from "./components/BottomTelemetryBar.jsx";
import GlobeHUDOverlays from "./components/GlobeHUDOverlays.jsx";
import ArchiveModal from "./components/ArchiveModal.jsx";

export default function App() {
  const [result, setResult] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedVessel, setSelectedVessel] = useState(null);
  const [activeSidebarSection, setActiveSidebarSection] = useState('MISSION CONTROL');
  const [playbackProgress, setPlaybackProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(30); // 30 seconds for trajectory
  const [showArchiveModal, setShowArchiveModal] = useState(false);

  // Reset playback when vessel changes
  useEffect(() => {
    if (selectedVessel) {
      setPlaybackProgress(0);
      setIsPlaying(false);
      setCurrentTime(0);
    }
  }, [selectedVessel]);

  async function handleAnalyze(file) {
    setLoading(true);
    setError("");
    setResult(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(URL.createObjectURL(file));

    try {
      const data = await analyzeImage(file);
      setResult(data);
    } catch (err) {
      setError(err.message || "Could not reach the OilGuard API.");
    } finally {
      setLoading(false);
    }
  }

  const handleVesselSelect = (vessel) => {
    // Use trajectory from backend if available, otherwise fallback to prototype
    const vesselWithTrajectory = {
      ...vessel,
      trajectory: vessel.trajectory && vessel.trajectory.length > 0
        ? vessel.trajectory
        : vessel.prototype
          ? getPrototypeTrajectory(vessel.name)
          : undefined
    };

    setSelectedVessel(vesselWithTrajectory);
  };

  function getPrototypeTrajectory(vesselName) {
    // MapLibre format: [longitude, latitude]
    const trajectories = {
      'PROTOTYPE-01': [[71.9, 19.1], [72.0, 19.15], [72.1, 19.2]],
      'PROTOTYPE-02': [[72.1, 18.8], [72.0, 18.75], [71.95, 18.7]],
      'PROTOTYPE-03': [[71.5, 19.3], [71.6, 19.25], [71.7, 19.2]]
    };
    return trajectories[vesselName] || [];
  }

  const handleVesselClose = () => {
    setSelectedVessel(null);
  };

  const handleSectionChange = (section) => {
    setActiveSidebarSection(section);

    // Handle section-specific focus behaviors
    switch (section) {
      case 'ARCHIVE':
        setShowArchiveModal(true);
        break;
      case 'SAR IMAGERY':
        // Focus on upload panel
        document.querySelector('.sar-analysis-panel')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      case 'VESSEL TRACKING':
        // Focus on globe area
        document.querySelector('.globe-wrapper')?.focus();
        break;
      case 'DETECTIONS':
        // Focus on detection HUD
        document.querySelector('.detection-hud')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      case 'TELEMETRY':
        // Focus on telemetry bar
        document.querySelector('.bottom-telemetry-bar')?.scrollIntoView({ behavior: 'smooth', block: 'end' });
        break;
      case 'MISSION CONTROL':
      default:
        // Return to main view
        document.querySelector('.globe-wrapper')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleStop = () => {
    setIsPlaying(false);
    setPlaybackProgress(0);
    setCurrentTime(0);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Update playback progress based on time
  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setCurrentTime(prevTime => {
          const newTime = prevTime + 0.1; // 100ms increments
          if (newTime >= duration) {
            setIsPlaying(false);
            return duration;
          }
          return newTime;
        });
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isPlaying, duration]);

  // Sync playbackProgress with currentTime
  useEffect(() => {
    setPlaybackProgress((currentTime / duration) * 100);
  }, [currentTime, duration]);

  return (
    <div className="page">
      {/* Top Bar */}
      <TopBar
        selectedVessel={selectedVessel}
        playbackProgress={playbackProgress}
      />

      {/* Main Content Area */}
      <div className="main-content">
        {/* Left Sidebar */}
        <LeftSidebar
          onSectionChange={handleSectionChange}
          activeSidebarSection={activeSidebarSection}
        />

        {/* Globe Container with HUD Overlays */}
        <div className="globe-wrapper">
          <GlobeContainer
            spillResult={result?.spill || null}
            vessels={result?.candidates || []}
            onVesselSelect={handleVesselSelect}
            selectedVessel={selectedVessel}
            playbackProgress={playbackProgress}
          />
          <GlobeHUDOverlays
            spillResult={result?.spill || null}
            vessels={result?.candidates || []}
            selectedVessel={selectedVessel}
          />
        </div>

        {/* Right Detection HUD */}
        <DetectionHUD spillResult={result?.spill || null} loading={loading} />

        {/* Vessel Investigation Panel */}
        {selectedVessel && (
          <VesselInvestigationPanel
            vessel={selectedVessel}
            isSelected={true}
            onClose={handleVesselClose}
            isPlaying={isPlaying}
            currentTime={currentTime}
            duration={duration}
            progress={playbackProgress}
            onPlayPause={handlePlayPause}
            onStop={handleStop}
            formatTime={formatTime}
          />
        )}

        {/* Upload Panel */}
        <UploadPanel onResult={handleAnalyze} disabled={loading} />
      </div>

      {/* Bottom Telemetry Bar */}
      <BottomTelemetryBar result={result} loading={loading} />

      {/* Archive Modal */}
      <ArchiveModal
        isOpen={showArchiveModal}
        onClose={() => setShowArchiveModal(false)}
      />

      {/* Error Message */}
      {error && <p className="error">{error}</p>}
    </div>
  );
}