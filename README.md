# Dynamic AI Interactive Storytelling Engine — Week 4 Prototype

This is the Week 4 deliverable: a working **text-only core loop** —
pick a universe, read a generated scene, pick a choice, get the next
scene — backed by a real database and a real LLM integration point.

Media generation (art, voice, procedural music) is intentionally **not**
included yet; that's Weeks 6–8 per the project plan. This week proves
the foundation works end to end.

---

## 1. Development environment setup

1. **Install VS Code** — https://code.visualstudio.com
   Recommended extensions: Python (Microsoft), ES7+ React snippets.

2. **Install Python 3.10+** — https://python.org/downloads
   Check it worked: `python3 --version`

3. **Install Node.js 18+ (includes npm)** — https://nodejs.org
   Check it worked: `node --version` and `npm --version`

4. **Install Git** — https://git-scm.com/downloads
   Check it worked: `git --version`

5. **Connect this project to GitHub:**
   ```bash
   cd storytelling-engine
   git init
   git add .
   git commit -m "Week 4: prototype core loop, database, and API integration"
   ```
   Then on GitHub: create a new empty repository (no README/license),
   copy the URL it gives you, and run:
   ```bash
   git remote add origin <your-repo-url>
   git branch -M main
   git push -u origin main
   ```

---

## 2. Running the backend (core loop + database)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # optional — see note below
uvicorn main:app --reload
```

Backend now runs at **http://127.0.0.1:8000**. Visit
`http://127.0.0.1:8000/docs` for an interactive API tester (built into
FastAPI automatically) — great for demoing the API live in your viva.

**About the LLM integration:** `llm.py` calls the Groq API. If you add
a free key from https://console.groq.com/keys into `.env`, real AI
text gets generated. If you leave `.env` empty, the app automatically
runs in **mock mode** — it still exercises the full loop and database
with pre-written sample scenes, so the prototype works even without
a key. This is worth explicitly mentioning in your viva: it shows you
designed the integration to fail gracefully instead of crashing.

---

## 3. Running the frontend (basic prototype UI)

In a **second terminal**:
```bash
cd frontend
npm install
npm run dev
```
Opens at **http://127.0.0.1:5173**. Pick a universe, read the scene,
click a choice, watch the next scene load — that's the core loop.

---

## 4. Proving the database/API integration works

With the backend running, in a third terminal:

```bash
# See the two universes available
curl http://127.0.0.1:8000/api/universes

# Start a story (creates a row in the database)
curl -X POST http://127.0.0.1:8000/api/start \
  -H "Content-Type: application/json" \
  -d '{"universe":"cyberpunk"}'
# copy the "session_id" from the response, then:

# Make a choice (appends to that same database row)
curl -X POST http://127.0.0.1:8000/api/choice \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<paste-id-here>","choice":"Accept the contract immediately"}'

# Reload the session straight from the database — proves it persisted
curl http://127.0.0.1:8000/api/session/<paste-id-here>

# List every session ever saved (debug endpoint)
curl http://127.0.0.1:8000/api/sessions
```

You can also just close and reopen `backend/story_engine.db` in a
SQLite viewer (e.g. the "SQLite Viewer" VS Code extension) to show
the saved rows visually during your viva.

---

## Project structure

```
storytelling-engine/
├── backend/
│   ├── main.py          # FastAPI routes — the core loop
│   ├── llm.py            # Groq API integration + mock fallback
│   ├── db.py              # SQLite database layer
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main UI — universe select + story screen
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## What's next (Weeks 5–8, per the project plan)

- Week 5: polish the frontend UI / state management
- Week 6: wire in edge-tts voice narration + typewriter animation sync
- Week 7: wire in SDXL Turbo image generation, run it in parallel with the LLM call
- Week 8: build the Tone.js procedural background music engine
