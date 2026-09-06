export default function ScoreBar({ label, value }) {
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