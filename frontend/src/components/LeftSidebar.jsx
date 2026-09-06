import { useState, useEffect } from 'react';

const LeftSidebar = ({ onSectionChange, activeSidebarSection }) => {
  const [activeSection, setActiveSection] = useState('MISSION CONTROL');

  const sections = [
    { id: 'MISSION CONTROL', label: 'MISSION CONTROL', icon: '⎈' },
    { id: 'SAR IMAGERY', label: 'SAR IMAGERY', icon: '📡' },
    { id: 'VESSEL TRACKING', label: 'VESSEL TRACKING', icon: '🚢' },
    { id: 'DETECTIONS', label: 'DETECTIONS', icon: '🎯' },
    { id: 'TELEMETRY', label: 'TELEMETRY', icon: '📊' },
    { id: 'ARCHIVE', label: 'ARCHIVE', icon: '📁' }
  ];

  // Sync with parent's active section
  useEffect(() => {
    if (activeSidebarSection) {
      setActiveSection(activeSidebarSection);
    }
  }, [activeSidebarSection]);

  const handleSectionClick = (sectionId) => {
    setActiveSection(sectionId);
    onSectionChange?.(sectionId);
  };

  return (
    <div className="left-sidebar">
      <div className="sidebar-content">
        {sections.map(section => (
          <div
            key={section.id}
            className={`${activeSection === section.id ? 'sidebar-item active' : 'sidebar-item'}`}
            onClick={() => handleSectionClick(section.id)}
            title={section.id}
          >
            <span className="sidebar-icon">{section.icon}</span>
            <span className="sidebar-label">{section.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LeftSidebar;