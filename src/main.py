"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys

try:
    from src.recommender import load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs  # python src/main.py


# Standard taste profiles
PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.80,
        "tempo_bpm": 120,
        "danceability": 0.80,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "tempo_bpm": 76,
        "danceability": 0.60,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.90,
        "tempo_bpm": 150,
        "danceability": 0.60,
    },
}

# Adversarial / edge-case profiles meant to trick the scoring logic
EDGE_CASE_PROFILES = {
    # Conflicting: sad mood but very high energy (the only sad song is low energy)
    "Sad but Hyped": {
        "genre": "blues",
        "mood": "sad",
        "energy": 0.90,
        "tempo_bpm": 160,
        "danceability": 0.90,
    },
    # Genre and mood that don't exist in the catalog
    "Unknown Genre": {
        "genre": "k-pop",
        "mood": "dreamy",
        "energy": 0.70,
        "tempo_bpm": 115,
        "danceability": 0.75,
    },
    # Energy outside the 0-1 range
    "Out-of-Range Energy": {
        "genre": "metal",
        "mood": "angry",
        "energy": 1.50,
        "tempo_bpm": 170,
        "danceability": 0.50,
    },
    # No preferences at all
    "Empty Profile": {},
}


WIDTH = 60


def print_song(rank: int, song: dict, score: float, explanation: str) -> None:
    """Print one ranked song with its score and reasons."""
    print(f"\n#{rank}  {song['title']}  ({song.get('artist', 'Unknown')})")
    print(f"    Score: {score:.2f}")
    print("    Reasons:")
    for reason in explanation.split("; "):
        if reason:
            print(f"      - {reason}")
    print("-" * WIDTH)


def print_recommendations(name: str, user_prefs: dict, songs: list, max_songs: int = None) -> None:
    """Print the top 5 recommendations, then offer the next 4 until the user says no.

    max_songs caps how many songs can be shown in total (default: the whole catalog).
    """
    recommendations = recommend_songs(user_prefs, songs, k=max_songs or len(songs))

    print("\n" + "=" * WIDTH)
    print(f"{name.upper():^{WIDTH}}")
    print("=" * WIDTH)
    print(f"Profile: {user_prefs or '(empty)'}")

    shown = 0
    batch = 5
    while shown < len(recommendations):
        for rank in range(shown + 1, min(shown + batch, len(recommendations)) + 1):
            print_song(rank, *recommendations[rank - 1])
        shown += batch
        batch = 4
        if shown >= len(recommendations):
            print("\nNo more recommendations.")
            break
        print(f"\nShowing #1-#{shown} of {len(recommendations)} (scroll up to see #1)")
        remaining = min(4, len(recommendations) - shown)
        answer = input(f"Show the next {remaining} options? (y/n): ").strip().lower()
        if answer not in ("y", "yes"):
            break


def run_llm_mode(songs: list) -> None:
    """Ask for a free-text request, let the LLM turn it into metadata, then recommend."""
    try:
        from src.llm_extractor import explain_picks, get_client, recommend_with_retry
    except ImportError:
        from llm_extractor import explain_picks, get_client, recommend_with_retry

    user_text = input("\nDescribe what you want to listen to: ").strip()
    if not user_text:
        return
    try:
        client = get_client()
        user_prefs, log = recommend_with_retry(user_text, songs, client)
        for line in log:
            print(f"  [{line}]")
        if "error" in user_prefs:
            print("Sorry, I couldn't turn that into a music request.")
            return
        explanation = explain_picks(user_text, recommend_songs(user_prefs, songs, k=3), client)
    except Exception as e:  # missing key, network, API errors
        print(f"Sorry, the AI service failed: {e}")
        return
    print(f"\nWhy these picks: {explanation}")
    print_recommendations(f"LLM: {user_text}", user_prefs, songs, max_songs=10)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    if "--llm" in sys.argv:
        run_llm_mode(songs)
        return

    for name, user_prefs in {**PROFILES, **EDGE_CASE_PROFILES}.items():
        print_recommendations(name, user_prefs, songs)


if __name__ == "__main__":
    main()
