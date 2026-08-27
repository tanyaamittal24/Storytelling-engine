"""
llm.py — Narrative generation layer (API integration piece).

Calls the Groq API (Llama 3) to generate the next story scene as
structured JSON: narrative text, 2-3 branching choices, and a mood tag.

If no GROQ_API_KEY is set, falls back to MOCK MODE so the rest of the
app (UI, database, session loop) can still be built, run, and tested
without needing an API key yet — useful for this week's prototype demo.
"""

import os
import json
import random
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a narrative engine for an interactive graphic novel.
Given the story universe and the conversation history so far, write the NEXT
short scene (60-100 words), then provide exactly 3 branching choices, and a
one-word mood tag (choose from: tense, mysterious, triumphant, calm, eerie, hopeful).

Respond ONLY with valid JSON in this exact shape, no extra text:
{
  "text": "...",
  "choices": ["...", "...", "..."],
  "mood": "..."
}"""

# ---------------------------------------------------------------------
# MOCK MODE — used automatically when no API key is configured
# ---------------------------------------------------------------------
_MOCK_SCENES = {
    "cyberpunk": [
        {
            "text": "Rain streaks down the corp-tower windows as your neural rig pings: an anonymous contract, "
                    "paying triple rate, asking you to break into Aegis Biotech's vault tonight.",
            "choices": ["Accept the contract immediately", "Dig into who's really behind it", "Ignore it and log off"],
            "mood": "tense",
        },
        {
            "text": "The vault door hisses open. Cold blue light spills across rain-slicked chrome, and "
                    "somewhere below, a security drone's rotors spin up.",
            "choices": ["Step inside the vault", "Disable the drone first", "Signal your crew to hold position"],
            "mood": "tense",
        },
    ],
    "dark-fantasy": [
        {
            "text": "The ruined chapel groans as you push the door open. Dust hangs thick in the moonlight, "
                    "and something ancient stirs beneath the cracked stone altar.",
            "choices": ["Approach the altar", "Search the side chambers", "Leave before it wakes"],
            "mood": "eerie",
        },
    ],
    "sci-fi-survival": [
        {
            "text": "The ship's hull groans against the derelict station's docking clamp. Emergency lights "
                    "flicker red, and your oxygen readout just dropped below 40%.",
            "choices": ["Force the airlock open", "Reroute power to life support first", "Check for other survivors"],
            "mood": "tense",
        },
    ],
}


def _mock_generate(universe: str, turn_index: int) -> dict:
    scenes = _MOCK_SCENES.get(universe, _MOCK_SCENES["cyberpunk"])
    scene = scenes[turn_index % len(scenes)]
    return scene


# ---------------------------------------------------------------------
# Real Groq API call
# ---------------------------------------------------------------------
def _groq_generate(universe: str, history: list) -> dict:
    messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nStory universe: {universe}"}]
    for turn in history:
        role = "assistant" if turn["role"] == "scene" else "user"
        messages.append({"role": role, "content": turn["content"]})
    if not history:
        messages.append({"role": "user", "content": "Begin the story."})

    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.9,
            "response_format": {"type": "json_object"},
        },
        timeout=20,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def generate_scene(universe: str, history: list) -> dict:
    """
    Public entry point used by main.py.
    Returns: {"text": str, "choices": [str, str, str], "mood": str}
    """
    if GROQ_API_KEY:
        try:
            return _groq_generate(universe, history)
        except Exception as e:
            # Fail soft to mock mode rather than crashing the demo mid-viva
            print(f"[llm.py] Groq call failed, falling back to mock: {e}")

    turn_index = len(history) // 2
    return _mock_generate(universe, turn_index)
