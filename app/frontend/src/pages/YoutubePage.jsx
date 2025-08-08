import { useState } from "react";
import { scoreYouTube } from "../api";
import ScoreCard from "../components/ScoreCard.jsx";

export default function YoutubePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const onScore = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (!url.trim()) {
        setError("Please paste a YouTube video URL.");
        return;
      }
      const res = await scoreYouTube(url, 300);
      // Prefer items if provided by backend; otherwise fall back to pairing if possible
      if (Array.isArray(res.items)) {
        setResult({ aggregate: res.aggregate, items: res.items });
      } else if (Array.isArray(res.scores) && Array.isArray(res.comments)) {
        const items = res.scores.map((scores, idx) => ({ text: res.comments[idx] ?? "", scores }));
        setResult({ aggregate: res.aggregate, items });
      } else {
        // Fallback: show scores only
        const items = (res.scores || []).map((scores) => ({ text: "", scores }));
        setResult({ aggregate: res.aggregate, items });
      }
    } catch (e) {
      setError(e?.message || "Failed to fetch and score YouTube comments");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <h2 className="panel-title">Score a YouTube Video</h2>
      <p className="panel-subtitle">Paste a YouTube link; we will fetch top comments and score each one.</p>

      <input
        className="input-text"
        value={url}
        onChange={e => setUrl(e.target.value)}
        placeholder="https://www.youtube.com/watch?v=..."
      />

      <div className="actions">
        <button className="btn" onClick={onScore} disabled={loading}>{loading ? "Fetching & scoring..." : "Fetch & Score"}</button>
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