import json

def generate_rdf():
    # Load JSON data
    with open("imdb_movies.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    base_url = "http://github.com/ruippgoncalves/rpcw2025/cinema/"
    rdf_lines = []

    # Process People
    for person_id, name in data.get('allPeople', {}).items():
        rdf_lines.append(f"""### {base_url}{person_id}
:{person_id} rdf:type owl:NamedIndividual ,
                        :Pessoa ;
           :name "{name}" .
""")

    # Process Countries, Languages, and Genres
    categories = [
        ("allCountries", ":Pais"),
        ("allLanguages", ":Lingua"),
        ("allGenres", ":Genero")
    ]
    for category, rdf_class in categories:
        for entity_id in data.get(category, []):
            rdf_lines.append(f"""### {base_url}{entity_id}
:{entity_id} rdf:type owl:NamedIndividual ,
                         {rdf_class} .
""")
    
    # Process Movies
    for movie in data.get('movies', []):
        movie_id = movie['id']
        genres = ','.join(f':{genre}' for genre in movie.get('genres', []))
        original_language_line = f":temLingua :{movie['originalLanguage']};" if movie.get('originalLanguage') else ""
        
        rdf_lines.append(f"""### {base_url}{movie_id}
:{movie_id} rdf:type owl:NamedIndividual ,
                   :Filme ;
          :temArgumento :Argumento{movie_id} ;
          :temGenero {genres} ;
          {original_language_line}
          :temPaisOrigem :{movie["originalCountry"]} ;
          :data "{movie["releaseYear"]}" ;
          :duracao {movie["duration"]} .
""")
    
    # Join all the parts and return the complete RDF output
    return "".join(rdf_lines)

if __name__ == "__main__":
    rdf_output = generate_rdf()
    print(rdf_output)
