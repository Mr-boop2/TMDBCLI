https://roadmap.sh/projects/tmdb-cli


### // Basic Blueprinted Implementation 
In this project, you will build a simple command line interface (CLI) to fetch data from 
The Movie Database (TMDB) and display it in the terminal. 
This project will help you practice your programming skills, 
including working with APIs, handling JSON data, and building a simple CLI application.

Requirements
The application should run from the command line, and be able to pull and show the popular,
top-rated, upcoming and now playing movies from the TMDB API.
The user should be able to specify the type of movies they want to see by passing a 
command line argument to the CLI tool.

Here is how the CLI tool usage should look like:

tmdb-app --type "playing"
tmdb-app --type "popular"
tmdb-app --type "top"
tmdb-app --type "upcoming"
You can look at the API documentation to understand how to fetch the data for each type of movie.

Now Playing Movies
Popular Movies
Top Rated Movies
Upcoming Movies
There are some considerations to keep in mind:

Handle errors gracefully, such as API failures or network issues.
Use a programming language of your choice to build this project.
Make sure to include a README file with instructions on how to run the application
and any other relevant information


### // Project Ideas 

   Add an LLM to provide recommendations based on your user preferences. 
   Add a watched movies list. If the movie has already been watched it will be tagged when displayed to the console. 
   Add a user preferences tab that will take use of the custom api search. 
   ### // AI Movie Search Based on current desires. 
      Enter User and verify it within the database. The database will have two tables. 1 Table will host the user and their preference file. The second table will host the users previously watched movies. 
      Entry Point: "Enter username: " 
      Second Prompt: "What type of movie are you looking for today?" 
         Gemini AI will look at previously watched movies -> query keywords using TMDB AI -> Make a suggestion of now playing movies. 
      Third Prompt: 
         *Display 5 Choices* 
         "Which movie would you like?" 
            Chooses 1 movie -> stores it in the watched movies database
            Does not choose a movie -> Generates five more movies with similar keywords. 

#### Project Tree 

```
TMDB Cli
├─ .venv
├─ pyproject.toml
├─ README.md
├─ testFile.txt
├─ tmdb_cli
│  ├─ cli.py
│  ├─ formatter.py
│  ├─ M_API.py
│  └─ __pycache__
│     ├─ cli.cpython-312.pyc
│     ├─ formatter.cpython-312.pyc
│     └─ M_API.cpython-312.pyc
└─ tmdb_cli.egg-info
   ├─ dependency_links.txt
   ├─ entry_points.txt
   ├─ PKG-INFO
   ├─ requires.txt
   ├─ SOURCES.txt
   └─ top_level.txt

```