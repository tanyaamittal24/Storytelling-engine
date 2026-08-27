"""
db.py — Database integration layer.

Uses SQLite (built into Python, zero setup) to persist story sessions.
This is the "Database/API integration" piece of the Week 4 prototype:
- Connects a database (SQLite here, easy to swap for Postgres/MongoDB later)
- Saves user session data (which universe, full choice history)
- Loads it back on every turn so the LLM has full context

Swapping to Postgres/MongoDB later only requires changing this file —
main.py never talks to SQLite directly, only through these functions.
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "story_engine.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the sessions table if it doesn't exist yet. Call once on startup."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            universe TEXT NOT NULL,
            history TEXT NOT NULL,       -- JSON list of {role, content} turns
            mood TEXT DEFAULT 'neutral',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_session(universe: str) -> str:
    """Insert a new session row and return its id."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO sessions (id, universe, history, mood, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, universe, json.dumps([]), "neutral", now, now),
    )
    conn.commit()
    conn.close()
    return session_id


def get_session(session_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row["id"],
        "universe": row["universe"],
        "history": json.loads(row["history"]),
        "mood": row["mood"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def append_turn(session_id: str, role: str, content: str, mood: str = None):
    """Add one turn (assistant scene or user choice) to a session's history."""
    session = get_session(session_id)
    if session is None:
        raise ValueError(f"No session found with id {session_id}")

    history = session["history"]
    history.append({"role": role, "content": content})

    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET history = ?, mood = COALESCE(?, mood), updated_at = ? WHERE id = ?",
        (json.dumps(history), mood, datetime.utcnow().isoformat(), session_id),
    )
    conn.commit()
    conn.close()


def list_sessions():
    """Utility used by the /api/sessions debug endpoint to prove data persists."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, universe, mood, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
