import json
import requests

def query_sparql(endpoint, query):
    """Execute a SPARQL query and return the results as a list of dictionaries."""
    headers = {'Accept': 'application/json'}
    response = requests.get(endpoint, params={'query': query}, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    data = response.json()
    variables = data.get('head', {}).get('vars', [])
    return [
        {var: binding[var]['value'] for var in variables if var in binding}
        for binding in data.get('results', {}).get('bindings', [])
    ]

def fetch_movies(endpoint):
    """Fetch a list of movies from the SPARQL endpoint."""
    movie_query = """
SELECT DISTINCT ?id ?title ?origin ?producer ?abstract WHERE {
    ?id a schema:Movie .
    ?id dbp:name ?title .
    FILTER(LANG(?title)="en")
    ?id dbp:country ?origin .
    FILTER(LANG(?origin)="en")
    ?id dbo:producer/dbp:name ?producer .
    FILTER(LANG(?producer)="en")
    ?id dbo:abstract ?abstract .
    FILTER(LANG(?abstract)="en")
} ORDER BY RAND() LIMIT 100
"""
    return query_sparql(endpoint, movie_query)

def fetch_starring(endpoint, movie_id):
    """Fetch a list of actors starring in a given movie."""
    query = f"""
SELECT ?starring WHERE {{
    <{movie_id}> dbo:starring ?starring .
}} LIMIT 5
"""
    results = query_sparql(endpoint, query)
    return [result["starring"] for result in results if "starring" in result]

def fetch_actor_details(endpoint, actor_id):
    """Fetch details for a given actor."""
    query = f"""
SELECT ?name ?birthDate ?origin WHERE {{
    <{actor_id}> dbp:name ?name .
    FILTER(LANG(?name)="en")
    <{actor_id}> dbo:birthDate ?birthDate .
    <{actor_id}> dbp:birthPlace ?origin .
}}
"""
    results = query_sparql(endpoint, query)
    if results:
        actor = results[0]
        actor["id"] = actor_id
        return actor
    return None

def main():
    endpoint = "https://dbpedia.org/sparql"
    movies = fetch_movies(endpoint)
    
    # Build the dataset with movies and a dict for actors.
    dataset = {
        "actors": {},
        "movies": movies,
    }
    
    for movie in movies:
        movie_id = movie.get("id")
        print("Processing movie:", movie_id)
        starring = fetch_starring(endpoint, movie_id)
        movie["starring"] = starring
        
        for actor_id in starring:
            if actor_id not in dataset["actors"]:
                print("Fetching actor:", actor_id)
                actor = fetch_actor_details(endpoint, actor_id)
                if actor:
                    dataset["actors"][actor_id] = actor
    
    # Save the dataset to a JSON file.
    with open("dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
