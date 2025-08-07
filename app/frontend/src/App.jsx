import { useEffect, useState } from "react";
import { warmup, scoreTexts, scoreYouTube } from "./api";

export default function App() {
  const [text, setText] = useState("");
  const [yt, setYt] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { warmup(); }, []);

  const onScoreText = async () => {
    setLoading(true);
    try {
      const texts = text.split("\n").map(s => s.trim()).filter(Boolean);
      setResult(await scoreTexts(texts));
    } finally {
      setLoading(false);
    }
  };

  const onScoreYT = async () => {
    setLoading(true);
    try {
      setResult(await scoreYouTube(yt, 300));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{maxWidth: 800, margin: "40px auto", fontFamily: "system-ui, sans-serif"}}>
      <h2>Toxicity Scorer</h2>

      <section>
        <h3>Paste comments</h3>
        <textarea
          rows={6}
          value={text}
          onChange={e => setText(e.target.value)}
          style={{width:"100%"}}
          placeholder="One comment per line"
        />
        <button onClick={onScoreText} disabled={loading}>Score Texts</button>
      </section>

      <section style={{marginTop: 24}}>
        <h3>YouTube link</h3>
        <input
          value={yt}
          onChange={e => setYt(e.target.value)}
          style={{width:"100%"}}
          placeholder="https://www.youtube.com/watch?v=..."
        />
        <button onClick={onScoreYT} disabled={loading}>Fetch & Score Comments</button>
      </section>

      {loading && <p>Scoring...</p>}

      {result && (
        <section style={{marginTop: 24}}>
          <h3>Aggregate</h3>
          <pre>{JSON.stringify(result.aggregate, null, 2)}</pre>
          <h3>Per Comment</h3>
          <pre style={{maxHeight: 400, overflow: "auto"}}>
            {JSON.stringify(result.scores, null, 2)}
          </pre>
        </section>
      )}
    </div>
  );
} 