"""
Tests that call the real Claude API.

They are skipped unless ANTHROPIC_API_KEY is set. Each run makes ~10 API calls
(a fraction of a cent). Run only these with:  python -m pytest tests/test_llm_live.py -v
"""

import os

import pytest

from src.llm_extractor import (
    explain_picks, extract_preferences, get_client, match_quality, recommend_with_retry,
)
from src.recommender import load_songs, recommend_songs

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"
)

SONGS = load_songs("data/songs.csv")


@pytest.fixture(scope="module")
def client():
    return get_client()


def test_study_request_gives_low_energy(client):
    prefs = extract_preferences("calm music for studying, no vocals", SONGS, client)
    assert "error" not in prefs
    assert prefs.get("energy", 0) <= 0.5


def test_gym_request_gives_high_energy(client):
    prefs = extract_preferences("hype songs for lifting weights at the gym", SONGS, client)
    assert "error" not in prefs
    assert prefs.get("energy", 0) >= 0.7


def test_off_topic_request_is_rejected(client):
    prefs = extract_preferences("what's the capital of France?", SONGS, client)
    assert prefs == {"error": "off_topic"}


def test_retry_pipeline_finds_a_good_match(client):
    prefs, log = recommend_with_retry("happy upbeat pop", SONGS, client)
    assert "error" not in prefs
    assert 1 <= len(log) <= 2
    top_score = recommend_songs(prefs, SONGS, k=1)[0][1]
    assert match_quality(prefs, top_score) >= 0.6


def test_explanation_mentions_a_retrieved_song(client):
    recs = recommend_songs({"genre": "lofi", "mood": "chill"}, SONGS, k=3)
    explanation = explain_picks("chill lofi to relax", recs, client)
    assert any(song["title"] in explanation for song, _, _ in recs)


def test_same_request_is_mostly_consistent(client):
    # The real LLM can vary slightly, so require most of the top 5 to overlap
    runs = []
    for _ in range(3):
        prefs = extract_preferences("sad acoustic songs for a rainy day", SONGS, client)
        runs.append({song["id"] for song, _, _ in recommend_songs(prefs, SONGS, k=5)})
    assert len(runs[0] & runs[1] & runs[2]) >= 3
