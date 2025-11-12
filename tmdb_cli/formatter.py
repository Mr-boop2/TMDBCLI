'''tmdb_cli/formatter.py'''

from rich.panel import Panel 
from rich.text import Text
import requests
import json 
import os 
from dotenv import load_dotenv

load_dotenv() 


def printFormat(movieInformation: dict): 
    currEmoji = "❔" 
    if (movieInformation["score"] < 3 ): 
        currEmoji = "☹️ " 
    elif (movieInformation["score"] < 6 and movieInformation["score"] >= 3 ):
        currEmoji = "😑 " 
    elif (movieInformation["score"] < 8 and movieInformation["score"] >= 6 ): 
        currEmoji = "👌 " 
    else: 
        currEmoji = "😍 "
    panelBody = ( Text(f"{movieInformation["Title"]}"
        f"\n\t{movieInformation["release_date"]}"
        f"\n\t{movieInformation["genres"]}"
        f"\n\t{currEmoji}{movieInformation["score"]*10:.1f}"
        f"\n\t{movieInformation['overview']}")
    )
    moviePanel = Panel(panelBody, padding=(1,5))
    return moviePanel 