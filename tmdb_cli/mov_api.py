# tmdb_cli/mov_api.py
import json
import os
import time
from typing import List

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live

from tmdb_cli.formatter import printFormat

load_dotenv()

ENDPOINTS = {
    "playing":  "now_playing",
    "popular":  "popular",
    "upcoming": "upcoming",
    "top":      "top_rated",
}

API_KEY = os.getenv("API_Key")               # fail fast if missing
if not API_KEY:
    raise RuntimeError("API_Key not found in environment (.env)")

# ---------------------------------------------------------------------------
def movie_request(
        movie_type: str, 
        page: int = 1, 
        release_year: int | None = None,
        genre_ids: List[int] | None = None 
        ) -> tuple:
    """Return one page of movies for the given type; raise on HTTP errors.""" 
    if release_year is None: 
        url = (
            f"https://api.themoviedb.org/3/movie/{ENDPOINTS[movie_type]}"
            f"?language=en-US&page={page}"
        )
        headers = {"accept": "application/json", "Authorization": API_KEY}
    else: 
        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?include_adult=false&include_video=false"
            f"&language=en-US&page={page}"
            f"&primary_release_year={release_year}"
            f"&sort_by=popularity.desc")
        headers = {"accept": "application/json", "Authorization": API_KEY}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"TMDB request failed: {exc}") from exc
    except json.JSONDecodeError:
        raise RuntimeError("TMDB returned invalid JSON")

    return data["results"], data["total_pages"]

# ---------------------------------------------------------------------------
def A_Main(movie_type: str, release_year: int | None) -> None:        # entry point from click
    console        = Console()
    movie_cache    = []      # holds movies fetched so far
    cursor         = 0       # next unread movie index
    current_page   = 1
    total_pages    = None
    batch_size     = 5
    keep_going     = True

    def ensure_cache():
        nonlocal current_page, total_pages, movie_cache  # ??? Ask chatGPT 
        # fetch next page when cursor outruns cache
        if cursor >= len(movie_cache):
            if total_pages is not None and current_page > total_pages:
                return False  # no more movies anywhere
            movies, total = movie_request(movie_type, current_page, release_year)
            movie_cache.extend(movies)
            total_pages = total
            current_page += 1
        return True

    while keep_going:
        if not ensure_cache():
            console.print("[bold yellow]No more movies to show.[/]")
            break

        upper = min(cursor + batch_size, len(movie_cache))
        for mov in movie_cache[cursor:upper]:
            info = {
                "Title":        mov["title"],
                "release_date": mov["release_date"],
                "genres":       mov["genre_ids"],
                "score":        mov["vote_average"],
                "overview":     mov["overview"],
            }
            panel = printFormat(info)
            with Live(panel, console=console, refresh_per_second=4):
                time.sleep(0.25)

        cursor = upper
        if not ensure_cache():  # pre-fetch so we know if more are available
            break

        answer = input("View more? (Y/N): ").strip().lower()
        keep_going = answer == "y"
