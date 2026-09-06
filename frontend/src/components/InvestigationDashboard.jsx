import SpillMap from "./SpillMap.jsx";
import CandidateCard from "./CandidateCard.jsx";

function formatPercent(value) {
  return `${Math.round(value * 100)}%`;
}

export default function InvestigationDashboard({ result, previewUrl }) {
  const { spill, candidates, source_image, data_mode, disclaimer } = result;

  return (
    <section className="dashboard">
      <div className="banner">{data_mode}</div>
      <p className="disclaimer">{disclaimer}</p>

      <div className="grid">
        <div className="panel">
          <h2>2. Simulated spill</h2>
          {previewUrl && (
            <img className="preview" src={previewUrl} alt="Uploaded scene" />
          )}
          <dl className="facts">
            <div>
              <dt>Source file</dt>
              <dd>
                {source_image.filename} ({source_image.size_bytes} bytes)
              </dd>
            </div>
            <div>
              <dt>Spill detected</dt>
              <dd>{spill.detected ? "Yes (simulated)" : "No"}</dd>
            </div>
            <div>
              <dt>Spill confidence</dt>
              <dd>{formatPercent(spill.confidence)} (demo)</dd>
            </div>
            <div>
              <dt>Spill center</dt>
              <dd>
                {spill.center.lat}, {spill.center.lon}
              </dd>
            </div>
            <div>
              <dt>Estimated area</dt>
              <dd>{spill.estimated_area_km2} km² (demo)</dd>
            </div>
            <div>
              <dt>Detection timestamp</dt>
              <dd>{spill.detection_timestamp}</dd>
            </div>
          </dl>
        </div>

        <div className="panel map-panel">
          <h2>3. Investigation map</h2>
          <SpillMap spill={spill} candidates={candidates} />
        </div>
      </div>

      <div className="panel">
        <h2>4. Candidate vessels (simulated AIS)</h2>
        <p className="muted">
          Attribution score is a simple weighted mix of spatial, temporal, and
          toy drift checks. It is a demo ranking — not legal guilt and not a
          calibrated probability.
        </p>
        <div className="candidates">
          {candidates.map((vessel, index) => (
            <CandidateCard
              key={vessel.vessel_id}
              vessel={vessel}
              rank={index + 1}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
