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

## Design Decisions

- **The code decides what the LLM extracts** The LLM only turns text into preferences; the ranking is done by a deterministic scoring function. Less "creative" than letting the LLM pick songs, but results are repeatable and explainable based on the current limited data set.
- **Validate what the LLM returns.** Clamping numbers and dropping unknown genres protects the scorer from bad output. Trade-off: if the LLM picks a genre we don't have, that preference is lost instead of mapped to something similar.
- **Retry at most twice.** The self-check catches weak matches without making the program slow or expensive. Trade-off: some requests just can't be matched well by an 18-song catalog, and retrying won't fix that.
- **Explanations use only retrieved data (RAG).** The explanation prompt contains the real song rows and tells the LLM not to invent details.
- **Fake clients in tests.** LLM tests use a fake client with canned replies, so they run for free, offline, and always give the same result.

## Testing Summary

- **11 automated tests, all passing** (`python -m pytest`):
  - JSON parsing handles code fences and extra text from the LLM.
  - The validator clamps out-of-range numbers and drops unknown values.
  - Off-topic and unparseable replies return an error instead of crashing.
  - Consistency: the same request run 5 times gives the same top 5.
  - The retry loop runs again only when the first match is weak.
  - The explanation prompt contains the real retrieved songs.
  -
  - **Not covered:** the tests don't call the real LLM, so they can't measure how good its extractions are.
