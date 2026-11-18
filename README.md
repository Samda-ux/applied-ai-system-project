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
