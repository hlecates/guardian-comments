export default function ScoreCard({ text, scores = {} }) {
  const toxic = typeof scores.toxic === "number" ? scores.toxic : 0;
  const percent = Math.round(toxic * 100);

  return (
    <div className="score-card">
      <div className="score-header">
        <div className="score-badge" data-level={levelFromPercent(percent)}>
          {percent}% toxic
        </div>
      </div>
      <div className="score-bar">
        <div className="score-bar-fill" style={{ width: `${percent}%` }} />
      </div>
      {text && <p className="score-text">{text}</p>}

      <div className="score-grid">
        {Object.entries(scores).map(([label, value]) => (
          <div key={label} className="score-item">
            <span className="score-label">{label}</span>
            <span className="score-value">{value.toFixed(3)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function levelFromPercent(p) {
  if (p >= 70) return "high";
  if (p >= 40) return "medium";
  return "low";
} 