function ScoreBar({ label, value }) {
  return (
    <div className="score-row">
      <span>{label}</span>
      <div className="bar">
        <div className="bar-fill" style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
      <strong>{value.toFixed(2)}</strong>
    </div>
  );
}

export default function CandidateCard({ vessel, rank }) {
  return (
    <article className="candidate-card">
      <header>
        <span className="rank">#{rank}</span>
        <div>
          <h3>{vessel.name}</h3>
          <p className="mono">{vessel.vessel_id}</p>
        </div>
        <div className="score-pill" title="Demo ranking only — not legal guilt">
          {vessel.attribution_score.toFixed(2)}
        </div>
      </header>
      <p className="meta">
        AIS position (simulated): {vessel.coordinates.lat}, {vessel.coordinates.lon}
        <br />
        AIS timestamp (simulated): {vessel.timestamp}
      </p>
      <ScoreBar label="Spatial consistency" value={vessel.spatial_consistency} />
      <ScoreBar label="Temporal consistency" value={vessel.temporal_consistency} />
      <ScoreBar label="Simplified drift consistency" value={vessel.drift_consistency} />
      <p className="explanation">{vessel.explanation}</p>
    </article>
  );
}
