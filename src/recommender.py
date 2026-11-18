import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        """Convert a UserProfile into the user_prefs dict score_song() expects."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the k songs that score highest for this user."""
        prefs = self._prefs(user)
        return sorted(self.songs, key=lambda s: score_song(prefs, asdict(s))[0], reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return the scoring reasons for one song as a single string."""
        score, reasons = score_song(self._prefs(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts, converting numeric columns to int/float."""
    print(f"Loading songs from {csv_path}...")
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (score, list of reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += 3.0
        reasons.append(f"genre match: {song['genre']} (+3.0)")

    if song["mood"] == user_prefs.get("mood"):
        score += 2.0
        reasons.append(f"mood match: {song['mood']} (+2.0)")

    if "energy" in user_prefs:
        energy_points = 2 * (1 - abs(user_prefs["energy"] - song["energy"]))
        score += energy_points
        reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{energy_points:.2f})")

    if "danceability" in user_prefs:
        dance_points = 1.0 * (1 - abs(user_prefs["danceability"] - song["danceability"]))
        score += dance_points
        reasons.append(f"danceability {song['danceability']:.2f} vs target {user_prefs['danceability']:.2f} (+{dance_points:.2f})")

    for feature in ("valence", "acousticness"):
        if feature in user_prefs:
            points = 1.0 * (1 - abs(user_prefs[feature] - song[feature]))
            score += points
            reasons.append(f"{feature} {song[feature]:.2f} vs target {user_prefs[feature]:.2f} (+{points:.2f})")

    if "tempo_bpm" in user_prefs:
        # Tempo is in BPM, so scale the gap: 100+ BPM apart earns nothing
        tempo_gap = min(abs(user_prefs["tempo_bpm"] - song["tempo_bpm"]) / 100, 1.0)
        tempo_points = 0.5 * (1 - tempo_gap)
        score += tempo_points
        reasons.append(f"tempo {song['tempo_bpm']:.0f} vs target {user_prefs['tempo_bpm']:.0f} BPM (+{tempo_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, rank by score, and return the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
