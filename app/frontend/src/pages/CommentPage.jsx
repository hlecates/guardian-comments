import { useState } from "react";
import { scoreTexts } from "../api";
import ScoreCard from "../components/ScoreCard.jsx";

export default function CommentPage() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const onScore = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const texts = text.split("\n").map(s => s.trim()).filter(Boolean);
      if (texts.length === 0) {
        setError("Please enter at least one comment.");
        return;
      }
      const res = await scoreTexts(texts);
      const items = res.scores.map((scores, idx) => ({ text: texts[idx] ?? "", scores }));
      setResult({ aggregate: res.aggregate, items });
    } catch (e) {
      setError(e?.message || "Failed to score comments");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <h2 className="panel-title">Score a Comment</h2>
      <p className="panel-subtitle">Paste one or more comments (one per line) and get a toxicity score for each.</p>

      <textarea
        className="input-textarea"
        rows={8}
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="One comment per line"
      />

      <div className="actions">
        <button className="btn" onClick={onScore} disabled={loading}>{loading ? "Scoring..." : "Score"}</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="results">
          <div className="aggregate">
            <h3>Aggregate</h3>
            <div className="metric">
              <span className="metric-label">Mean toxicity</span>
              <span className="metric-value">{(result.aggregate?.mean_toxicity ?? 0).toFixed(3)}</span>
            </div>
          </div>

          <div className="items">
            {result.items.map((item, idx) => (
              <ScoreCard key={idx} text={item.text} scores={item.scores} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
} 