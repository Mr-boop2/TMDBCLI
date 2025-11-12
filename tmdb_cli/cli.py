#tmdb_cli/cli.py
import click 
from tmdb_cli.mov_api import ENDPOINTS 
from datetime import datetime 
from typing import * 
@click.group() 
def cli(): 
    pass 

#Fetch Command Entrance Point. Browsing Options 
@cli.command() 
@click.option("--type", "movie_type", type=click.Choice(list(ENDPOINTS)), 
              default="popular", show_default=True, help="Fetch the movies that you would like to see based on four categories")
@click.option("--year", "release_year",  type=click.IntRange(1900, datetime.now().year + 1), default=None, help="Fetch the movies released in the specified year!")
def fetch(movie_type: str, release_year: int | None): 
    from tmdb_cli.mov_api import A_Main
    click.echo(f"You chose {movie_type}")
    A_Main(movie_type, release_year)        

# Settign User preferences 
@cli.command("prefs") 
def prefs(): 
    from tmdb_cli.user_prefs import store_user_prefs_interactive
    store_user_prefs_interactive()
    
# Gemini Powered automatching. 
@cli.command("match", help="Gemini-powered movie recommendations")
@click.option(
    "--type", "movie_type",
    default="popular",
    type=click.Choice(list(ENDPOINTS)),  # playing, upcoming, …
    show_default=True,
    help="TMDB category to draw the shortlist from",
)

@click.option(
    "--top", "top_n",
    default=10, show_default=True,
    help="How many recommendations to display",
)
def match_cmd(movie_type: str, top_n: int) -> None:
    """Ask Gemini to rank the best movies for your saved preferences."""
    from tmdb_cli.gem_ai import recommend
    from tmdb_cli.formatter import printFormat
    from rich.console import Console
    from rich.live import Live
    import time
    from tmdb_cli.user_prefs import movieGenres

    console = Console()

    try:
        movies = recommend(movie_type, top_k=top_n)
    except RuntimeError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise click.Abort()

    for m in movies:
        panel = printFormat(
            {
                "Title":        m["title"],
                "release_date": m["release_date"],
                "genres":       m["genre_ids"],
                "score":        m["vote_average"],
                "overview":     m["overview"],
            }
        )
        # same animation wrapper you use in fetch()
        with Live(panel, console=console, refresh_per_second=4):
            time.sleep(0.25)
            genres = ", ".join(movieGenres.get(g, str(g)) for g in m["genre_ids"])
            console.print(f"[bold green]Why Gemini chose it:[/] {m['reason']}")
            console.print(f"[bold red]Genres:[/] {genres}\n")