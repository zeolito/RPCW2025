# SPARQL Movie & Actor Data Fetcher

This script retrieves movie data and associated actor details from DBpedia's SPARQL endpoint and saves the results as a JSON file.

## Prerequisites
- Python 3.x
- Install dependencies using:
  ```bash
  pip install requests
  ```

## Overview
- **query_sparql:** Executes a SPARQL query and returns results as a list of dictionaries.
- **fetch_movies:** Retrieves a list of movies.
- **fetch_starring:** Retrieves a list of actors for a movie.
- **fetch_actor_details:** Retrieves details for a specific actor.
- **main:** Coordinates data fetching and writes the dataset to a JSON file.