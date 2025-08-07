const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function warmup() {
  await fetch(`${BASE}/health`);
}

export async function scoreTexts(texts) {
  const res = await fetch(`${BASE}/api/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texts })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function scoreYouTube(url, max_comments = 300) {
  const res = await fetch(`${BASE}/api/youtube/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, max_comments })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
} 