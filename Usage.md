A command line interface (CLI) application that fetches and displays data from The Movie Database (TMDB) API. Users can specify the type of movies they want to view, including currently playing, popular, top-rated, and upcoming movies.

This project is part of the backend section of the [roadmap.sh](https://roadmap.sh/projects/tmdb-cli) website.

## Features
- Fetch and display movie data from TMDB API.
- Command line arguments to specify movie types:
  - `playing`
  - `popular`
  - `top`
  - `upcoming`

## Installation
> Recommended (no virtualenv needed): **pipx**

1. Install `pipx` (one-time):
   - **Windows (PowerShell)**:
     ```powershell
     py -m pip install --user pipx
     py -m pipx ensurepath
     ```
   - **macOS/Linux**:
     ```bash
     python3 -m pip install --user pipx
     pipx ensurepath
     ```
## Configuration
Before running the application, you need to set your TMDB API key as an environment variable. (This project uses the TMDB v4 bearer token.)
On Windows (PowerShell)
setx TMDB_API_KEY "Bearer YOUR_TMDB_V4_TOKEN"

## Usage
To run the application, use the following command:
tmdb-app fetch --type [movie_type]
Replace [movie_type] with one of the following options:
playing
popular
top
upcoming


2. Install this project:
   ```bash
   pipx install git+https://github.com/your-username/tmdb-cli-tool.git
