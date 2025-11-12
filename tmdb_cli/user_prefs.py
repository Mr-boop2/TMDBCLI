#tmdb_cli/user_prefs.py

import json 
from pathlib import Path
from tmdb_cli.fetchGenres import fetchMGenres
pathHome = Path.home() / "userPreferences"
pathFile = pathHome / "preferences.json"
# This will be the default path for the userPrefs file. 

'''
This will store the user preferences in a JSON file that is the path name. 
We can use the OS module to automatically set the path name. 
It will be in the userprefs folder 

'''
movieGenres = fetchMGenres() 
'''
Tasks: 
1 Check if there is a existing preferences file. 
    If not, create one and prompt the user to make their preferences. 
    If so, show the user their current preferences and ask if they would like to make adjustments. 
'''


''' --- Helper Functions --- '''
def check_dir(): 
    #Creates the userPreferences directory 
    pathHome.mkdir(parents=True, exist_ok=True)


def load_prefs(): 
    if pathFile.exists() == True: 
        try:
            with pathFile.open(encoding="utf-8") as fh:
                return set(json.load(fh))
        except (json.JSONDecodeError, TypeError):
            pass 
    return set()


def save_prefs(ids) -> None:
    """Write genre-IDs back to JSON (pretty-printed)."""
    check_dir()
    with pathFile.open("w", encoding="utf-8") as fh:
        json.dump(sorted(ids), fh, indent=2)


''' --- API Functions --- '''


def list_prefs():
    """Return saved genre names (human readable)."""
    return [movieGenres[i] for i in sorted(load_prefs())]

def add_prefs(*ids) -> None:
    """
    Add one or more genres (by ID **or** case-insensitive name). Silently ignores unknown entries.
    """
    current = load_prefs()
    for item in ids:
        if isinstance(item, int) and item in movieGenres:
            current.add(item)
        elif isinstance(item, str):
            # match on name (case-insensitive)
            for gid, name in movieGenres.items():
                if item.lower() == name.lower():
                    current.add(gid)
                    break
    save_prefs(current)


def remove_prefs(*ids_or_names) -> None:
    """Remove genres (same rules as add_prefs)."""
    current = load_prefs()
    for item in ids_or_names:
        if isinstance(item, int):
            current.discard(item)
        elif isinstance(item, str):
            for genre_id, name in movieGenres.items():
                if item.lower() == name.lower():
                    current.discard(genre_id)
                    break
    save_prefs(current)

def toggle_ids(ids_to_toggle: set[int]):
    """Add missing ids, remove ones that already exist, then save."""
    current = load_prefs()
    for genre_id in ids_to_toggle:
        if genre_id in current:
            current.remove(genre_id)   # ← DESELECT
        else:
            current.add(genre_id)      # ← SELECT
    save_prefs(current)

def store_user_prefs_interactive() -> None:
    """Interactive menu that lets the user toggle genre preferences."""
    current = load_prefs()

    print("\nToggle your preferred genres (comma-separated numbers):\n")
    for idx, (genre_id, name) in enumerate(movieGenres.items(), start=1):
        marker = "✓" if genre_id in current else " "
        print(f"{idx:>2}. [{marker}] {name}")

    raw_input = input("\nSelect / Deselect → ").strip()
    if not raw_input:
        print("No changes made.")
        return
    try:
        indices = {int(list_index) for list_index in raw_input.split(",")}
    except ValueError:
        print("❌  Please enter only numbers separated by commas.")
        return

    # Map menu numbers → genre_ids, ignoring out-of-range choices
    # THIS BUILDS THE MAP AND GETS THE ACTUAL IDS THAT MATCH THE TMDB GENRES not my generated indices 
    ids_to_toggle = {
        list(movieGenres.keys())[i - 1]
        # For each genre chosen in the list of indices [the number associated with each genre]
        for i in indices
            # If the index is within the range of the valid choices 
            if 1 <= i <= len(movieGenres)
    }
    if not ids_to_toggle:
        print("❌  No valid selections.")
        return

    toggle_ids(ids_to_toggle)

    print("\nUpdated preferences:")
    for name in list_prefs():
        print(f"  • {name}")