'''tmdb_cli/fetchGenres.py'''
import requests 
import os 
from dotenv import load_dotenv
from typing import List, Dict
load_dotenv() 

## Dynamically store the genres with an API call so that they dont need to be hardcoded 
## Put them in a dictionary 
def fetchMGenres() -> List[Dict[int, str]]: 
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    headers = {
        "accept": "application/json",
        "Authorization": os.getenv("API_Key")
    }
    response = requests.get(url, headers=headers)
    mGenreObj = response.json().get("genres", []) 
    return {g["id"]: g["name"] for g in mGenreObj}
    
GENRES = fetchMGenres() 