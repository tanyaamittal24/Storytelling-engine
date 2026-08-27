"""
main.py — FastAPI backend for the Dynamic AI Interactive Storytelling Engine.

Week 4 prototype scope (text-only core loop, per project plan):
  POST /api/start     -> create a session, generate the opening scene
  POST /api/choice     -> save the user's choice, generate the next scene
  GET  /api/session/{id} -> reload a session (proves data persists)
  GET  /api/sessions   -> list all saved sessions (debug/demo endpoint)
  GET  /api/universes  -> static list of selectable universes

Media generation (images, voice, procedural music) is intentionally NOT
included yet — that's Weeks 6-8 per the project plan. This prototype's
job is to prove the core loop + LLM integration + database work end to end.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import llm

app = FastAPI(title="Dynamic AI Interactive Storytelling Engine — API")

# Allow the local React dev server to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

UNIVERSES = [
    {"id": "cyberpunk", "name": "Cyberpunk", "blurb": "Neon cities, corporations, and back-alley hacks."},
    {"id": "dark-fantasy", "name": "Dark Fantasy", "blurb": "Ruins, forgotten magic, and things that wait in the dark."},
    {"id": "sci-fi-survival", "name": "Sci-Fi Survival", "blurb": "A derelict ship. An unknown planet. You, mostly alone."},
]


class StartRequest(BaseModel):
    universe: str


class ChoiceRequest(BaseModel):
    session_id: str
    choice: str


@app.get("/api/universes")
def get_universes():
    return UNIVERSES


@app.post("/api/start")
def start_story(req: StartRequest):
    if req.universe not in {u["id"] for u in UNIVERSES}:
        raise HTTPException(status_code=400, detail="Unknown universe")

    session_id = db.create_session(req.universe)
    scene = llm.generate_scene(req.universe, history=[])

    db.append_turn(session_id, role="scene", content=scene["text"], mood=scene["mood"])

    return {
        "session_id": session_id,
        "text": scene["text"],
        "choices": scene["choices"],
        "mood": scene["mood"],
    }


@app.post("/api/choice")
def make_choice(req: ChoiceRequest):
    session = db.get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    db.append_turn(req.session_id, role="choice", content=req.choice)

    session = db.get_session(req.session_id)  # reload with the new turn included
    scene = llm.generate_scene(session["universe"], history=session["history"])

    db.append_turn(req.session_id, role="scene", content=scene["text"], mood=scene["mood"])

    return {
        "session_id": req.session_id,
        "text": scene["text"],
        "choices": scene["choices"],
        "mood": scene["mood"],
    }


@app.get("/api/session/{session_id}")
def load_session(session_id: str):
    session = db.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/sessions")
def all_sessions():
    """Debug endpoint: proves data is actually being saved to the database."""
    return db.list_sessions()


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Story engine API is running"}
