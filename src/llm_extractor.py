"""
Turn free-text music requests into user_prefs metadata using an LLM.

The output dict uses the same keys score_song() understands, so it can be
passed straight into recommend_songs().
"""

import json
from typing import Dict, List, Optional, Tuple

try:
    from src.recommender import recommend_songs
except ImportError:
    from recommender import recommend_songs

MODEL = "claude-sonnet-5-5"

# Numeric features the LLM may set, with the range each is clamped to
NUMERIC_RANGES = {
    "energy": (0.0, 1.0),
    "valence": (0.0, 1.0),
    "danceability": (0.0, 1.0),
    "acousticness": (0.0, 1.0),
    "tempo_bpm": (40.0, 220.0),
}


def build_system_prompt(songs: List[Dict]) -> str:
    """Build the instructions, listing the genres and moods that exist in the catalog."""
    genres = sorted({s["genre"] for s in songs})
    moods = sorted({s["mood"] for s in songs})
    return f"""You convert music requests into metadata for a song recommender.
Return ONLY a JSON object, no prose, with these optional keys:
  "genre": one of {genres}
  "mood": one of {moods}
  "energy": number 0-1 (calm -> intense)
  "valence": number 0-1 (sad -> happy)
  "danceability": number 0-1
  "acousticness": number 0-1 (electronic -> acoustic; "no vocals"/"studying" usually leans acoustic)
  "tempo_bpm": number in BPM
Omit any key the request doesn't imply. Pick the closest allowed genre/mood or omit it.
If the request is not about music, return {{"error": "off_topic"}}."""


def parse_json(text: str) -> Dict:
    """Pull the JSON object out of the model reply, tolerating code fences or extra prose."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise ValueError(f"No JSON object in model reply: {text!r}")
    return json.loads(text[start : end + 1])


def validate(raw: Dict, songs: List[Dict]) -> Dict:
    """Keep only known keys, clamp numbers to valid ranges, and drop genres/moods not in the catalog."""
    if "error" in raw:
        return {"error": str(raw["error"])}

    prefs = {}
    for key, (lo, hi) in NUMERIC_RANGES.items():
        value = raw.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue  # missing or malformed -> leave unconstrained
        prefs[key] = min(max(float(value), lo), hi)

    for key in ("genre", "mood"):
        allowed = {s[key] for s in songs}
        value = raw.get(key)
        if isinstance(value, str) and value.strip().lower() in allowed:
            prefs[key] = value.strip().lower()

    return prefs


def get_client(client: Optional[object] = None) -> object:
    """Return the given client, or a real Anthropic client (reads ANTHROPIC_API_KEY from env)."""
    if client is not None:
        return client
    import anthropic

    return anthropic.Anthropic()


def ask(client: object, system: str, user_text: str) -> str:
    """Send one message to the model and return its text reply."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": user_text}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def extract_preferences(user_text: str, songs: List[Dict], client: Optional[object] = None,
                        feedback: Optional[str] = None) -> Dict:
    """Ask the LLM for metadata matching user_text and return validated user_prefs.

    feedback, if given, describes why a previous attempt fell short so the model can revise.
    """
    client = get_client(client)
    prompt = user_text if feedback is None else f"{user_text}\n\n{feedback}"
    text = ask(client, build_system_prompt(songs), prompt)
    try:
        raw = parse_json(text)
    except (ValueError, json.JSONDecodeError):
        return {"error": "unparseable"}
    return validate(raw, songs)


# ---------- Agentic: check the results and retry ----------

# Points each preference key can earn in score_song()
MAX_POINTS = {"genre": 3.0, "mood": 2.0, "energy": 2.0, "danceability": 1.0,
              "valence": 1.0, "acousticness": 1.0, "tempo_bpm": 0.5}


def match_quality(user_prefs: Dict, top_score: float) -> float:
    """Return top_score as a fraction (0-1) of the best score these prefs could earn."""
    best = sum(MAX_POINTS[key] for key in user_prefs if key in MAX_POINTS)
    return top_score / best if best else 0.0


def recommend_with_retry(user_text: str, songs: List[Dict], client: Optional[object] = None,
                         min_quality: float = 0.6, max_attempts: int = 2) -> Tuple[Dict, List[str]]:
    """Extract prefs, check how well the best song matches, and let the LLM revise if it's weak.

    Returns (user_prefs, log) where log describes each attempt.
    """
    client = get_client(client)
    log = []
    feedback = None
    for attempt in range(1, max_attempts + 1):
        prefs = extract_preferences(user_text, songs, client, feedback)
        if "error" in prefs:
            return prefs, log
        top_song, top_score, _ = recommend_songs(prefs, songs, k=1)[0]
        quality = match_quality(prefs, top_score)
        log.append(f"attempt {attempt}: {prefs} -> best '{top_song['title']}' ({quality:.0%} match)")
        if quality >= min_quality:
            break
        feedback = (f"Your previous metadata {json.dumps(prefs)} matched the catalog poorly "
                    f"(best song only a {quality:.0%} match). Revise it: relax or drop the "
                    "constraints least important to the request.")
    return prefs, log


# ---------- RAG: explain picks using the retrieved song data ----------

EXPLAIN_SYSTEM = """You explain music recommendations to a listener.
You are given their request and the songs that were retrieved for it, with their real data.
Write 2-4 short sentences explaining why these songs fit. Only mention songs, artists and
facts from the provided data; never invent songs or details."""


def explain_picks(user_text: str, recommendations: List[Tuple[Dict, float, str]],
                  client: Optional[object] = None) -> str:
    """Ask the LLM to explain the top picks, grounded in the retrieved song rows."""
    client = get_client(client)
    fields = ("title", "artist", "genre", "mood", "energy", "tempo_bpm",
              "valence", "danceability", "acousticness")
    retrieved = [{**{f: song[f] for f in fields}, "score": round(score, 2)}
                 for song, score, _ in recommendations]
    prompt = f"Request: {user_text}\n\nRetrieved songs:\n{json.dumps(retrieved, indent=2)}"
    return ask(client, EXPLAIN_SYSTEM, prompt).strip()
