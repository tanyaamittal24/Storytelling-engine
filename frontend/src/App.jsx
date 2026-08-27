import { useEffect, useState } from "react";

// Change this if your backend runs on a different port
const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [universes, setUniverses] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [scene, setScene] = useState(null); // { text, choices, mood }
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch the list of universes once, on load
  useEffect(() => {
    fetch(`${API_BASE}/api/universes`)
      .then((res) => res.json())
      .then(setUniverses)
      .catch(() => setError("Could not reach the backend. Is it running on port 8000?"));
  }, []);

  async function startStory(universeId) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ universe: universeId }),
      });
      if (!res.ok) throw new Error("Failed to start story");
      const data = await res.json();
      setSessionId(data.session_id);
      setScene(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function pickChoice(choiceText) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/choice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, choice: choiceText }),
      });
      if (!res.ok) throw new Error("Failed to load next scene");
      const data = await res.json();
      setScene(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function restart() {
    setSessionId(null);
    setScene(null);
  }

  return (
    <div className="app">
      <header>
        <h1>Story Engine</h1>
        <p className="subtitle">Week 4 prototype — core text loop</p>
      </header>

      {error && <div className="error">{error}</div>}

      {!scene && (
        <div className="universe-select">
          <h2>Choose your universe</h2>
          <div className="universe-list">
            {universes.map((u) => (
              <button key={u.id} className="universe-card" onClick={() => startStory(u.id)} disabled={loading}>
                <strong>{u.name}</strong>
                <span>{u.blurb}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {scene && (
        <div className="story-screen">
          <div className="mood-tag">mood: {scene.mood}</div>
          <p className="scene-text">{scene.text}</p>

          <div className="choices">
            {scene.choices.map((choice, i) => (
              <button key={i} className="choice-btn" onClick={() => pickChoice(choice)} disabled={loading}>
                {choice}
              </button>
            ))}
          </div>

          <button className="restart-btn" onClick={restart}>
            ↺ Start a different story
          </button>
        </div>
      )}

      {loading && <div className="loading">Generating next scene…</div>}

      {sessionId && <div className="session-note">session id: {sessionId}</div>}
    </div>
  );
}
