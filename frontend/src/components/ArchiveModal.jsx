const ArchiveModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  // Demo archive entries
  const demoEntries = [
    {
      id: 'DEMO-001',
      date: '2026-08-25 14:23:00',
      area: 'Arabian Sea Sector 7A',
      result: 'DETECTED',
      confidence: '0.87',
      type: 'DEMONSTRATION DATA'
    },
    {
      id: 'DEMO-002',
      date: '2026-08-22 09:15:00',
      area: 'Arabian Sea Sector 4B',
      result: 'CLEAR',
      confidence: '0.23',
      type: 'DEMONSTRATION DATA'
    },
    {
      id: 'DEMO-003',
      date: '2026-08-18 18:45:00',
      area: 'Arabian Sea Sector 9C',
      result: 'DETECTED',
      confidence: '0.91',
      type: 'DEMONSTRATION DATA'
    }
  ];

  return (
    <div className="archive-overlay" onClick={onClose}>
      <div className="archive-modal" onClick={e => e.stopPropagation()}>
        <div className="archive-header">
          <h2>ARCHIVE</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="archive-notice">
          <span className="notice-icon">ℹ</span>
          <span className="notice-text">DEMONSTRATION DATA - Historical scenes are for display purposes only. No actual backend archive system is connected.</span>
        </div>

        <div className="archive-list">
          {demoEntries.map(entry => (
            <div key={entry.id} className={`archive-item ${entry.result === 'DETECTED' ? 'has-detection' : ''}`}>
              <div className="archive-item-header">
                <span className="archive-id">{entry.id}</span>
                <span className={`archive-result ${entry.result === 'DETECTED' ? 'detected' : 'clear'}`}>
                  {entry.result}
                </span>
              </div>
              <div className="archive-item-details">
                <div className="detail-row">
                  <span className="detail-label">DATE</span>
                  <span className="detail-value">{entry.date}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">AREA</span>
                  <span className="detail-value">{entry.area}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">CONFIDENCE</span>
                  <span className="detail-value">{entry.confidence}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">TYPE</span>
                  <span className="detail-value prototype">{entry.type}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="archive-footer">
          <button className="archive-close-btn" onClick={onClose}>CLOSE</button>
        </div>
      </div>
    </div>
  );
};

export default ArchiveModal;
