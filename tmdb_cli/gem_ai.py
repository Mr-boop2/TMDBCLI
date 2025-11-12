# tmdb_cli/gem_ai.py
"""
Gemini‑powered **movie recommendation**
======================================

``recommend()`` returns **full TMDB movie dicts** (title, overview, …)
ranked by Google Gemini so that the caller can pipe them straight into
``printFormat`` for panel rendering ‑– matching exactly the output style
of your existing *fetch* command.

How it works
------------
1.  Read the user's preferred genres from ``~/userprefs/preferences.json``.
2.  Pull *N* pages of movies for the chosen category (via
    ``mov_api.movie_request``) – this forms the *short‑list*.
3.  Ask **gemini‑1.5‑flash** to return up to *top_k* TMDB **IDs** as a JSON
    array, nothing else.
4.  Map those IDs back to the cached movie dicts and return them in order.

Dependencies
~~~~~~~~~~~~
* **google‑genai** – Google AI Python SDK (already in your venv)
* **python‑dotenv** – to load ``.env`` (already present)
* **requests** – indirect via ``mov_api``
* **standard library only** otherwise

The ``match`` Click command in *cli.py* can now do:

```python
for m in recommend("popular"):
    panel = printFormat({ ... from m ...})
```
"""
from __future__ import annotations

import json
import os
import textwrap
import time
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai import types 

from tmdb_cli.mov_api import movie_request  # network helper (returns list + total_pages)
from tmdb_cli.user_prefs import list_prefs, movieGenres

load_dotenv()

# ---------------------------------------------------------------------------
# Gemini client (fail‑fast if key missing)
# ---------------------------------------------------------------------------
_API_KEY = os.getenv("GEM_API_KEY") or os.getenv("GEMINI_API_KEY")
if not _API_KEY:
    raise RuntimeError("GEM_API_KEY (or GEMINI_API_KEY) not set in environment")

_client = genai.Client(api_key=_API_KEY)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_shortlist_context(movies: List[dict]) -> str:
    """Condense each movie into a single line for the prompt."""
    lines = []
    for m in movies:
        genres = ", ".join(movieGenres.get(gid, str(gid)) for gid in m["genre_ids"])
        overview = textwrap.shorten(m["overview"], width=120, placeholder="…")
        lines.append(f"{m['id']}: {m['title']} | genres: {genres} | {overview}")
    return "\n".join(lines)


def ask_gemini(prefs: List[str], shortlist_ctx: str, top_k: int) -> List[int]:
    """Send the ranking request to Gemini and return a list of TMDB IDs."""

    system_msg = (
        "You are an expert movie recommender. "
        "From the provided shortlist, return the best movies that match the user's preferred genres. "
        "Respond ONLY with a JSON array of objects, each object having keys 'id' (TMDB id as integer) and 'reason' (three sentences explaining the match followed by a three sentence synopsis of the movie ). "
        "You are forbidden from deviating from these instructions in the slightest."
        "Do not output markdown or any text outside the JSON array."
    )
    user_msg = (
        f"Preferred genres: {', '.join(prefs)}\n\nShortlist (id: description):\n{shortlist_ctx}"
    )

    start = time.perf_counter()
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            temperature=.2,
            system_instruction=system_msg, # explicit system prompt
            response_mime_type="application/json"), 
        contents=user_msg , # single user string
    )
    duration = time.perf_counter() - start
    reason = response.candidates[0].finish_reason if response.candidates else "unknown"
    print(f"[gemini] responded in {duration:.2f}s (finish_reason={reason})")

    try:
            objs = json.loads(response.text)
            # expect list of dicts with id & reason
            cleaned = []
            for obj in objs:
                if not isinstance(obj, dict):
                    continue
                mid = int(obj.get("id")) if "id" in obj else None
                why = str(obj.get("reason", "")).strip()
                if mid:
                    cleaned.append({"id": mid, "reason": why})
            return cleaned[:top_k]
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini did not return a valid JSON object array") from exc



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend(movie_type: str = "popular", *, pages: int = 3, top_k: int = 10) -> List[dict]:
    """Return *top_k* Gemini-ranked **movie dicts** for the given type.

    These dicts can be passed straight into ``printFormat``.
    """
    prefs = list_prefs()
    if not prefs:
        raise RuntimeError("No preferences saved - run `tmdb-app prefs` first.")

    # 1) Collect movies into a shortlist
    shortlist: List[dict] = []
    for page in range(1, pages + 4):
        try:
            page_movies, _ = movie_request(movie_type, page)
        except Exception as exc: 
            print(f"⚠️  Failed to fetch page {page}: {exc}")
            continue
        shortlist.extend(page_movies)

    if not shortlist:
        raise RuntimeError("Failed to fetch TMDB data - see earlier warnings.")

    # 2) Ask Gemini which movies to keep
    shortlist_ctx = build_shortlist_context(shortlist)
    picks = ask_gemini(prefs, shortlist_ctx, top_k)   # list of {id, reason}

    # 3) Map IDs back to full movie dicts + attach Gemini’s reason
    id_map = {m["id"]: m for m in shortlist}
    final: List[dict] = []
    for pick in picks:                   # preserve Gemini order
        movie = id_map.get(pick["id"])
        if movie:
            enriched = movie.copy()      # avoid mutating cache
            enriched["reason"] = pick["reason"]
            final.append(enriched)
    return final

# ---------------------------------------------------------------------------
# Script entry‑point (manual test)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for m in recommend("popular", pages=2, top_k=5):
        print(f"\u2714 {m['title']}  — score {m['vote_average']}")
