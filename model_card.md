## Test Output using LLM

- use this in terminal
  $env:ANTHROPIC_API_KEY = "paste-your-full-key-here"
  python -m pytest tests/test_llm_live.py -v

======================================================================================= test session starts ========================================================================================
collected 6 items

tests/test_llm_live.py::test_study_request_gives_low_energy PASSED [ 16%]
tests/test_llm_live.py::test_gym_request_gives_high_energy PASSED [ 33%]
tests/test_llm_live.py::test_off_topic_request_is_rejected PASSED [ 50%]
tests/test_llm_live.py::test_retry_pipeline_finds_a_good_match PASSED [ 66%]
tests/test_llm_live.py::test_explanation_mentions_a_retrieved_song PASSED [ 83%]
tests/test_llm_live.py::test_same_request_is_mostly_consistent PASSED [100%]

======================================================================================== 6 passed in 14.09s ========================================================================================

**Result:** 6 out of 6 live tests passed against the real Claude API (model `claude-sonnet-5-5`), plus 11 out of 11 offline tests.

## Testing Overview

- Tested the project through two seperate testing formats.
- One tested the non LLM parts of the project including each function.
- The other tested the LLM's output and made sure it worked correctly.
- Another tested a sample of an LLM output that can be run without an API key.

## Limitations

- **Small, made-up catalog.** 68 fictional songs. Many requests can only be matched loosely.
- **Exact genre matching.** "indie pop" earns no genre points for a "pop" request, even though they're related.
- **Unknown genres are dropped.** If the LLM picks a genre that isn't in the catalog, that preference is thrown away instead of mapped to something similar.
- **Conflicting requests.** "Sad but hyped" returns a sad, low-energy song, because genre and mood are worth more points than energy.
- **Empty requests.** With no preferences, every song scores 0 and the order is meaningless.
- **Hand-picked weights.** The point values (+3 genre, +2 mood, ...) are my choices, not learned from real listener data.
- **The LLM can vary.** The same request can give slightly different preferences on different runs. The live consistency test only requires 3 of the top 5 songs to match.
- **Needs a paid API key** for LLM mode and the live tests.

## AI Reflection

- **Could your AI be misused, and how would you prevent that?**
  It can't really be misused as the AI key required is user side and is not abused
- **What surprised you while testing your AI's reliability?**
  The amount of times I had to go back and re-prompt claude while manually inspecting the LLM's output and adjusting to make it more satisfactory towards the user and adding guardlines as many times the AI hallucinated.
- **Describe your collaboration with AI during this project.**
  It went quite well, AI worked very well as a tool to both help me code and understand better. There were quite a few suggestions I rejected, one of them being AI completely hallucinated a false diagram that was applicable in any way to my current codebase that I rejected. One suggested I accepted was it helping me make llm_extractor.py which allows for the main functionality of integrating the LLM.
