## Original Project

- ai110-module3show-musicrecommendersimulation-starter. Uses a pre defined algorithm to sort a dataset of music along with it's metadata into specific categories that might align with user prefererences. It was relatively accurate in keeping track of songs across multiple genres.

## Title and Summary

**AI Music Recommender**

- My project uses the previously created music recommendation generator and creates a scoring for a person based on user responses where certain metadata is extracted using an LLM. It allows users to get song recommendations for them based on a scoring category created by their preferences.
- Why it matters: The LLM translates the request, and a transparent scoring system picks the songs, so every recommendation comes with reasons you can check.

## Architecture Overview

- User types a request and an LLM extract numbered preferences including genre, mood, energy, tempo etc.
- The code validates the scores and makes sure their correct and drops unknown genres and moods.
- Uses the scoring formula in songs.csv and matches the user score with the best matches for the top 3 songs. The LLM retrieves further information regarding the songs and writes a grounded explanation with top 5 songs and all other songs.

- **LLM extractor**: turns the user's text into a preferences dict. The prompt lists only the genres and moods that exist in the catalog.
- **Validator**: the LLM's output is never trusted directly. Numbers are clamped to valid ranges and unknown genres/moods are dropped.
- **Scorer**: Points for genre match (+3), mood match (+2), and closeness on energy, danceability, valence, acousticness and tempo.
- **Agentic retry**: If the best song is a weak match, the LLM is asked to revise its preferences (max 2 attempts).
- **RAG explanation**: the top songs' real data is retrieved from the catalog and given to the LLM, which explains the picks using only that data.

## Setup Instructions

1. Install Python 3.10+.
2. Open a terminal in the project folder and install the dependencies:
   ```
   pip install anthropic pytest
   ```
3. **Normal mode** (built-in test profiles, no API key needed):
   ```
   python src/main.py
   ```
4. **LLM mode** (type your own request): set your Anthropic API key, then run with `--llm`.
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-..."   # PowerShell; on Mac/Linux: export ANTHROPIC_API_KEY=...
   python src/main.py --llm
   ```
5. Run the tests:
   ```
   python -m pytest
   ```

## Sample Interactions

### 1. LLM mode (`--llm`)

Input: `a nice happy upbeat song`

```text
> python src/main.py --llm
Loading songs from data/songs.csv...
Loaded songs: 68

Describe what you want to listen to: a nice happy upbeat song
[attempt 1: {'energy': 0.7, 'valence': 0.85, 'danceability': 0.7, 'mood': 'happy'} -> best 'Bebop Sprint' (98% match)]

Why these picks: All three songs are tagged as happy with fairly high energy (0.70 to 0.74) and bright valence (0.78 to 0.86), which matches your request for something upbeat. "Golden Hour Drive" by Neon Echo has the sunniest feel of the group at 0.86 valence, and "Sweet Summer Synth" by Indigo Parade is the most danceable at 0.79, with a steady 122 BPM. If you want something more lively and acoustic, "Bebop Sprint" by Quincy Hale Trio is a fast jazz pick at 176 BPM.

============================================================
LLM: A NICE HAPPY UPBEAT SONG
============================================================
Profile: {'energy': 0.7, 'valence': 0.85, 'danceability': 0.7, 'mood': 'happy'}

#1 Bebop Sprint (Quincy Hale Trio)
Score: 5.87
Reasons: - mood match: happy (+2.0) - energy 0.70 vs target 0.70 (+2.00) - danceability 0.64 vs target 0.70 (+0.94) - valence 0.78 vs target 0.85 (+0.93)

---

#2 Sweet Summer Synth (Indigo Parade)
Score: 5.86
Reasons: - mood match: happy (+2.0) - energy 0.72 vs target 0.70 (+1.96) - danceability 0.79 vs target 0.70 (+0.91) - valence 0.84 vs target 0.85 (+0.99)

---

#3 Golden Hour Drive (Neon Echo)
Score: 5.84
Reasons: - mood match: happy (+2.0) - energy 0.74 vs target 0.70 (+1.92) - danceability 0.77 vs target 0.70 (+0.93) - valence 0.86 vs target 0.85 (+0.99)

---

#4 Backroad Sunset (The Holloway Creek)
Score: 5.81
Reasons: - mood match: happy (+2.0) - energy 0.64 vs target 0.70 (+1.88) - danceability 0.66 vs target 0.70 (+0.96) - valence 0.82 vs target 0.85 (+0.97)

---

#5 Juke Joint Shuffle (Sadie Greer)
Score: 5.81
Reasons: - mood match: happy (+2.0) - energy 0.66 vs target 0.70 (+1.92) - danceability 0.70 vs target 0.70 (+1.00) - valence 0.74 vs target 0.85 (+0.89)

---

Showing #1-#5 of 10 (scroll up to see #1)
Show the next 4 options? (y/n): y

#6 Rooftop Lights (Indigo Parade)
Score: 5.72
Reasons: - mood match: happy (+2.0) - energy 0.76 vs target 0.70 (+1.88) - danceability 0.82 vs target 0.70 (+0.88) - valence 0.81 vs target 0.85 (+0.96)

---

#7 Sunday Skank (Sol Rasta Collective)
Score: 5.71
Reasons: - mood match: happy (+2.0) - energy 0.62 vs target 0.70 (+1.84) - danceability 0.82 vs target 0.70 (+0.88) - valence 0.86 vs target 0.85 (+0.99)

---

#8 Summer Garage (Fuzz Parade)
Score: 5.69
Reasons: - mood match: happy (+2.0) - energy 0.79 vs target 0.70 (+1.82) - danceability 0.62 vs target 0.70 (+0.92) - valence 0.80 vs target 0.85 (+0.95)

---

#9 Sunrise City (Neon Echo)
Score: 5.66
Reasons: - mood match: happy (+2.0) - energy 0.82 vs target 0.70 (+1.76) - danceability 0.79 vs target 0.70 (+0.91) - valence 0.84 vs target 0.85 (+0.99)

---

Showing #1-#9 of 10 (scroll up to see #1)
Show the next 1 options? (y/n): y

#10 Block Party (Kilo Verse)
Score: 5.59
Reasons: - mood match: happy (+2.0) - energy 0.80 vs target 0.70 (+1.80) - danceability 0.88 vs target 0.70 (+0.82) - valence 0.82 vs target 0.85 (+0.97)

---

No more recommendations.
```

### 2. LLM mode: study request (RAG + confidence check)

Input: `something to focus on while studying late at night`. The first attempt is a 93% match, so no retry is needed. The explanation only cites songs and values from the retrieved rows.

```text
> python src/main.py --llm
Describe what you want to listen to: "something to focus on while studying late at night"
[attempt 1: {'energy': 0.25, 'valence': 0.4, 'danceability': 0.35, 'acousticness': 0.7, 'tempo_bpm': 75.0, 'genre': 'lofi', 'mood': 'focused'} -> best 'Rainy Window Notes' (93% match)]

Why these picks: These three lofi tracks suit a late-night study session because they're all low-energy (0.33 to 0.40) and slow (74 to 80 BPM), so they won't pull your attention away from your work. "Rainy Window Notes" by Paper Lanterns and "Focus Flow" by LoRoom are both tagged with a focused mood and have a warm, acoustic feel, which is why they ranked highest. "Late Bus Home" by Cloud Tenant is tagged moody rather than focused, but it has the same gentle tempo and lofi sound, making it a calmer, slightly more reflective choice for the later hours.

============================================================
LLM: "SOMETHING TO FOCUS ON WHILE STUDYING LATE AT NIGHT"
============================================================
Profile: {'energy': 0.25, 'valence': 0.4, 'danceability': 0.35, 'acousticness': 0.7, 'tempo_bpm': 75.0, 'genre': 'lofi', 'mood': 'focused'}

#1 Rainy Window Notes (Paper Lanterns)
Score: 9.81
Reasons: - genre match: lofi (+3.0) - mood match: focused (+2.0) - energy 0.33 vs target 0.25 (+1.84) - danceability 0.57 vs target 0.35 (+0.78) - valence 0.52 vs target 0.40 (+0.88) - acousticness 0.88 vs target 0.70 (+0.82) - tempo 74 vs target 75 BPM (+0.49)

---

#2 Focus Flow (LoRoom)
Score: 9.65
Reasons: - genre match: lofi (+3.0) - mood match: focused (+2.0) - energy 0.40 vs target 0.25 (+1.70) - danceability 0.60 vs target 0.35 (+0.75) - valence 0.59 vs target 0.40 (+0.81) - acousticness 0.78 vs target 0.70 (+0.92) - tempo 80 vs target 75 BPM (+0.47)

---

#3 Late Bus Home (Cloud Tenant)
Score: 7.95
Reasons: - genre match: lofi (+3.0) - energy 0.38 vs target 0.25 (+1.74) - danceability 0.60 vs target 0.35 (+0.75) - valence 0.40 vs target 0.40 (+1.00) - acousticness 0.74 vs target 0.70 (+0.96) - tempo 76 vs target 75 BPM (+0.49)

---

#4 Sleepy Tape Deck (LoRoom)
Score: 7.88
Reasons: - genre match: lofi (+3.0) - energy 0.30 vs target 0.25 (+1.90) - danceability 0.55 vs target 0.35 (+0.80) - valence 0.58 vs target 0.40 (+0.82) - acousticness 0.82 vs target 0.70 (+0.88) - tempo 70 vs target 75 BPM (+0.47)

---

#5 Midnight Coding (LoRoom)
Score: 7.71
Reasons: - genre match: lofi (+3.0) - energy 0.42 vs target 0.25 (+1.66) - danceability 0.62 vs target 0.35 (+0.73) - valence 0.56 vs target 0.40 (+0.84) - acousticness 0.71 vs target 0.70 (+0.99) - tempo 78 vs target 75 BPM (+0.48)

---

Showing #1-#5 of 10 (scroll up to see #1)
Show the next 4 options? (y/n):
```

### 3. LLM mode: genre not in the catalog (k-pop)

The catalog has no k-pop, so the validator falls back to pop. The system still finds a strong pop/melancholy match (98%), and the explanation says honestly that none of the songs are k-pop.

```text
> python src/main.py --llm
Describe what you want to listen to: dreamy k-pop for a rainy day
  [attempt 1: {'energy': 0.4, 'valence': 0.4, 'danceability': 0.55, 'acousticness': 0.4, 'tempo_bpm': 95.0, 'genre': 'pop', 'mood': 'melancholy'} -> best 'Lonely Satellite' (98% match)]

Why these picks: None of these songs are tagged k-pop, so they're the closest pop matches rather than true k-pop picks. "Lonely Satellite" by Mira Kane is the best fit for a rainy day: it's melancholy, with low energy (0.45), a slow 92 BPM tempo, and a fairly acoustic feel. "Paper Hearts" by Lila Marsh has a softer romantic mood and moderate energy, which suits a gentle, wistful mood. "Golden Hour Drive" by Neon Echo is much brighter and happier (valence 0.86), so it's the least rainy option, but it offers an upbeat contrast.

============================================================
             LLM: DREAMY K-POP FOR A RAINY DAY
============================================================
Profile: {'energy': 0.4, 'valence': 0.4, 'danceability': 0.55, 'acousticness': 0.4, 'tempo_bpm': 95.0, 'genre': 'pop', 'mood': 'melancholy'}

#1  Lonely Satellite  (Mira Kane)
    Score: 10.27
    Reasons:
      - genre match: pop (+3.0)
      - mood match: melancholy (+2.0)
      - energy 0.45 vs target 0.40 (+1.90)
      - danceability 0.55 vs target 0.55 (+1.00)
      - valence 0.30 vs target 0.40 (+0.90)
      - acousticness 0.42 vs target 0.40 (+0.98)
      - tempo 92 vs target 95 BPM (+0.48)
------------------------------------------------------------

#2  Paper Hearts  (Lila Marsh)
    Score: 7.62
    Reasons:
      - genre match: pop (+3.0)
      - energy 0.58 vs target 0.40 (+1.64)
      - danceability 0.70 vs target 0.55 (+0.85)
      - valence 0.72 vs target 0.40 (+0.68)
      - acousticness 0.38 vs target 0.40 (+0.98)
      - tempo 102 vs target 95 BPM (+0.46)
------------------------------------------------------------

#3  Golden Hour Drive  (Neon Echo)
    Score: 6.88
    Reasons:
      - genre match: pop (+3.0)
      - energy 0.74 vs target 0.40 (+1.32)
      - danceability 0.77 vs target 0.55 (+0.78)
      - valence 0.86 vs target 0.40 (+0.54)
      - acousticness 0.24 vs target 0.40 (+0.84)
      - tempo 116 vs target 95 BPM (+0.40)
------------------------------------------------------------

#4  Sunrise City  (Neon Echo)
    Score: 6.65
    Reasons:
      - genre match: pop (+3.0)
      - energy 0.82 vs target 0.40 (+1.16)
      - danceability 0.79 vs target 0.55 (+0.76)
      - valence 0.84 vs target 0.40 (+0.56)
      - acousticness 0.18 vs target 0.40 (+0.78)
      - tempo 118 vs target 95 BPM (+0.39)
------------------------------------------------------------

#5  Weekend Anthem  (The Brightsides)
    Score: 6.53
    Reasons:
      - genre match: pop (+3.0)
      - energy 0.81 vs target 0.40 (+1.18)
      - danceability 0.83 vs target 0.55 (+0.72)
      - valence 0.89 vs target 0.40 (+0.51)
      - acousticness 0.15 vs target 0.40 (+0.75)
      - tempo 120 vs target 95 BPM (+0.38)
------------------------------------------------------------

Showing #1-#5 of 10 (scroll up to see #1)
Show the next 4 options? (y/n):
```

### 4. Guardrail: off-topic request

Input: `what's the capital of France?`. The LLM flags it as not a music request, and the program refuses instead of recommending songs.

```text
> python src/main.py --llm
Describe what you want to listen to: "what's the capital of France?"
Sorry, I couldn't turn that into a music request.
```

### 5. Normal mode (built-in profiles, no API key)

```text
> python src/main.py
Loading songs from data/songs.csv...
Loaded songs: 68

============================================================
                      HIGH-ENERGY POP
============================================================
Profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'tempo_bpm': 120, 'danceability': 0.8}

#1  Sunrise City  (Neon Echo)
    Score: 8.44
    Reasons:
      - genre match: pop (+3.0)
      - mood match: happy (+2.0)
      - energy 0.82 vs target 0.80 (+1.96)
      - danceability 0.79 vs target 0.80 (+0.99)
      - tempo 118 vs target 120 BPM (+0.49)
------------------------------------------------------------

#2  Golden Hour Drive  (Neon Echo)
    Score: 8.33
    Reasons:
      - genre match: pop (+3.0)
      - mood match: happy (+2.0)
      - energy 0.74 vs target 0.80 (+1.88)
      - danceability 0.77 vs target 0.80 (+0.97)
      - tempo 116 vs target 120 BPM (+0.48)
------------------------------------------------------------

#3  Weekend Anthem  (The Brightsides)
    Score: 6.45
    Reasons:
      - genre match: pop (+3.0)
      - energy 0.81 vs target 0.80 (+1.98)
      - danceability 0.83 vs target 0.80 (+0.97)
      - tempo 120 vs target 120 BPM (+0.50)
------------------------------------------------------------
...
```

## Reliability and Guardrail Results

### Offline test suite (no API key)

```text
> python -m pytest -v
collecting ... collected 17 items

tests/test_llm_extractor.py::test_parse_json_handles_fences_and_prose PASSED [  5%]
tests/test_llm_extractor.py::test_validate_clamps_and_drops_unknowns PASSED [ 11%]
tests/test_llm_extractor.py::test_off_topic_passes_through PASSED        [ 17%]
tests/test_llm_extractor.py::test_unparseable_reply_returns_error PASSED [ 23%]
tests/test_llm_extractor.py::test_extracted_prefs_drive_recommendations PASSED [ 29%]
tests/test_llm_extractor.py::test_same_request_gives_consistent_results PASSED [ 35%]
tests/test_llm_extractor.py::test_retry_revises_weak_match PASSED        [ 41%]
tests/test_llm_extractor.py::test_no_retry_when_first_match_is_good PASSED [ 47%]
tests/test_llm_extractor.py::test_explanation_prompt_contains_retrieved_songs PASSED [ 52%]
tests/test_llm_live.py::test_study_request_gives_low_energy SKIPPED      [ 58%]
tests/test_llm_live.py::test_gym_request_gives_high_energy SKIPPED (...) [ 64%]
tests/test_llm_live.py::test_off_topic_request_is_rejected SKIPPED (...) [ 70%]
tests/test_llm_live.py::test_retry_pipeline_finds_a_good_match SKIPPED   [ 76%]
tests/test_llm_live.py::test_explanation_mentions_a_retrieved_song SKIPPED [ 82%]
tests/test_llm_live.py::test_same_request_is_mostly_consistent SKIPPED   [ 88%]
tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score PASSED [ 94%]
tests/test_recommender.py::test_explain_recommendation_returns_non_empty_string
tests/test_llm_live.py::test_study_request_gives_low_energy PASSED [ 16%]
tests/test_llm_live.py::test_gym_request_gives_high_energy PASSED [ 33%]
tests/test_llm_live.py::test_off_topic_request_is_rejected PASSED [ 50%]
tests/test_llm_live.py::test_retry_pipeline_finds_a_good_match PASSED [ 66%]
tests/test_llm_live.py::test_explanation_mentions_a_retrieved_song PASSED [ 83%]
tests/test_llm_live.py::test_same_request_is_mostly_consistent PASSED [100%]

======================== 17 passed ========================
```

### Live LLM tests (real Claude API)

```text
> python -m pytest tests/test_llm_live.py -v
tests/test_llm_live.py::test_study_request_gives_low_energy PASSED [ 16%]
tests/test_llm_live.py::test_gym_request_gives_high_energy PASSED [ 33%]
tests/test_llm_live.py::test_off_topic_request_is_rejected PASSED [ 50%]
tests/test_llm_live.py::test_retry_pipeline_finds_a_good_match PASSED [ 66%]
tests/test_llm_live.py::test_explanation_mentions_a_retrieved_song PASSED [ 83%]
tests/test_llm_live.py::test_same_request_is_mostly_consistent PASSED [100%]
6 passed in 14.09s
```

These cover the off-topic guardrail, the agentic retry, RAG grounding and consistency against the real model. See [model_card.md](model_card.md).

### Guardrail: missing API key

```text
> python src/main.py --llm
Loading songs from data/songs.csv...
Loaded songs: 68

Describe what you want to listen to: play me something chill
Sorry, the AI service failed: "Could not resolve authentication method. Expected one of api_key, auth_token, or credentials to be set. Or for the `Authorization` header to be explicitly omitted"
```

### Guardrail: empty request

```text
> python src/main.py --llm
Loading songs from data/songs.csv...
Loaded songs: 68

Describe what you want to listen to:
```

The program exits cleanly without calling the LLM.

## Design Decisions

- **The code decides what the LLM extracts** The LLM only turns text into preferences; the ranking is done by a deterministic scoring function. Less "creative" than letting the LLM pick songs, but results are repeatable and explainable based on the current limited data set.
- **Validate what the LLM returns.** Clamping numbers and dropping unknown genres protects the scorer from bad output. Trade-off: if the LLM picks a genre we don't have, that preference is lost instead of mapped to something similar.
- **Retry at most twice.** The self-check catches weak matches without making the program slow or expensive. Trade-off: some requests just can't be matched well by a 68-song catalog, and retrying won't fix that.
- **Explanations use only retrieved data (RAG).** The explanation prompt contains the real song rows and tells the LLM not to invent details.

## Testing Summary

- 11 out of 11 automated tests pass.
- **Automated tests**: 11 tests covering JSON parsing, validation, error cases, consistency, the retry loop and the RAG prompt.
- **Confidence scoring:** every LLM request gets a match quality (best song's score / highest possible score). Below 60%, the system retries.
- **Error handling and logging:** each attempt is printed. API failures, off-topic and unparseable replies print a message instead of crashing.
- **Human evaluation:** I reviewed the results in the table below.

**Evaluation results** (68-song catalog):

| Test Input                           | Evaluation Criteria                   | Result                                                                             |
| ------------------------------------ | ------------------------------------- | ---------------------------------------------------------------------------------- |
| High-Energy Pop profile              | #1 is pop, happy, high energy         | Pass. Sunrise City, score 8.44                                                     |
| Chill Lofi profile                   | #1 is lofi, chill, low energy         | Pass. Midnight Coding, score 8.43                                                  |
| Deep Intense Rock profile            | #1 is rock, intense, high energy      | Pass. Highway Thunder, score 8.47                                                  |
| Sad but Hyped (sad mood, energy 0.9) | Balances conflicting preferences      | Partial. Rain on the Delta (6.59) matches genre and mood but has low energy (0.38) |
| Unknown Genre (k-pop, dreamy)        | No crash; falls back to closest songs | Pass. Golden Hour Drive, low score 3.40 shows a weak match                         |
| Out-of-Range Energy (1.5)            | No crash; still ranks sensibly        | Pass. Ashes in the Wire (metal, angry), score 7.38                                 |
| Empty profile                        | No crash                              | Partial. Runs, but every song scores 0.00, so the order is meaningless             |
| Empty text in `--llm` mode           | Exits gracefully                      | Pass                                                                               |
| `--llm` with no API key              | Error message, no crash               | Pass. Prints "Sorry, the AI service failed: ..."                                   |
| Same request 5 times (test)          | Identical top 5 each time             | Pass                                                                               |
| Weak first LLM guess (test)          | Retries with feedback                 | Pass. 2nd attempt revised mood to chill                                            |
