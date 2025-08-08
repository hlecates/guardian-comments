import { useEffect } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { warmup } from "./api";
import CommentPage from "./pages/CommentPage.jsx";
import YoutubePage from "./pages/YoutubePage.jsx";

export default function App() {
  const location = useLocation();

  useEffect(() => { warmup(); }, []);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">Toxicity Scorer</h1>
        <nav className="app-nav">
          <Link className={location.pathname === "/comment" ? "nav-link active" : "nav-link"} to="/comment">Comment</Link>
          <Link className={location.pathname === "/youtube" ? "nav-link active" : "nav-link"} to="/youtube">YouTube</Link>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/comment" element={<CommentPage />} />
          <Route path="/youtube" element={<YoutubePage />} />
          <Route path="/" element={<Navigate to="/comment" replace />} />
          <Route path="*" element={<Navigate to="/comment" replace />} />
        </Routes>
      </main>
    </div>
  );
} 