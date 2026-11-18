from types import SimpleNamespace

from src.llm_extractor import (
    explain_picks, extract_preferences, parse_json, recommend_with_retry, validate,
)
from src.recommender import load_songs, recommend_songs

SONGS = load_songs("data/songs.csv")


class FakeClient:
    """Stands in for anthropic.Anthropic and returns a canned reply."""

    def __init__(self, reply: str):
        self.messages = SimpleNamespace(create=lambda **kwargs: SimpleNamespace(
            content=[SimpleNamespace(type="text", text=reply)]
        ))


def test_parse_json_handles_fences_and_prose():
    assert parse_json('Sure!\n```json\n{"mood": "chill"}\n```') == {"mood": "chill"}


def test_validate_clamps_and_drops_unknowns():
    raw = {"energy": 1.7, "tempo_bpm": "fast", "genre": "K-Pop", "mood": "Chill", "foo": 1}
    assert validate(raw, SONGS) == {"energy": 1.0, "mood": "chill"}


def test_off_topic_passes_through():
    client = FakeClient('{"error": "off_topic"}')
    assert extract_preferences("what's the weather?", SONGS, client) == {"error": "off_topic"}


def test_unparseable_reply_returns_error():
    assert extract_preferences("x", SONGS, FakeClient("no json here")) == {"error": "unparseable"}


def test_extracted_prefs_drive_recommendations():
    client = FakeClient('{"genre": "lofi", "mood": "focused", "energy": 0.3, "acousticness": 0.8}')
    prefs = extract_preferences("something mellow for studying, no vocals", SONGS, client)
    top_song = recommend_songs(prefs, SONGS, k=1)[0][0]
    assert top_song["genre"] == "lofi"


class SequenceClient:
    """Fake client that returns a different canned reply on each call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.prompts = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.prompts.append(kwargs["messages"][0]["content"])
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.replies.pop(0))])


def test_same_request_gives_consistent_results():
    reply = '{"genre": "pop", "mood": "happy", "energy": 0.8}'
    runs = []
    for _ in range(5):
        prefs = extract_preferences("upbeat pop", SONGS, FakeClient(reply))
        runs.append([song["id"] for song, _, _ in recommend_songs(prefs, SONGS, k=5)])
    assert all(run == runs[0] for run in runs)


def test_retry_revises_weak_match():
    # First guess is impossible to satisfy well; the revision is a good match
    client = SequenceClient([
        '{"genre": "lofi", "mood": "intense", "energy": 1.0, "danceability": 1.0}',
        '{"genre": "lofi", "mood": "chill", "energy": 0.4}',
    ])
    prefs, log = recommend_with_retry("chill lofi", SONGS, client)
    assert len(log) == 2
    assert prefs["mood"] == "chill"
    assert "matched the catalog poorly" in client.prompts[1]


def test_no_retry_when_first_match_is_good():
    client = SequenceClient(['{"genre": "pop", "mood": "happy", "energy": 0.8}'])
    prefs, log = recommend_with_retry("happy pop", SONGS, client)
    assert len(log) == 1


def test_explanation_prompt_contains_retrieved_songs():
    client = SequenceClient(["These fit because..."])
    recs = recommend_songs({"genre": "pop"}, SONGS, k=3)
    assert explain_picks("pop please", recs, client) == "These fit because..."
    for song, _, _ in recs:
        assert song["title"] in client.prompts[0]
