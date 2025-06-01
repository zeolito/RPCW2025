import json, requests, os
import datetime

def query_dbpedia(endpoint_url, sparql_query):
    # Set up the headers
    headers = {
        'Accept': 'application/json',  # You can change this based on the response format you need
    }
    
    # Make the GET request to the GraphDB endpoint
    response = requests.get(endpoint_url, params={'query': sparql_query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response from the GraphDB endpoint
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

endpoint = "https://dbpedia.org/sparql"

def get_uris_from_dbpedia(out_filename):
    query_number_games = """
    SELECT (COUNT(?game) as ?nGames) WHERE {
        ?game a dbo:VideoGame .
        FILTER EXISTS {
            ?game rdfs:label ?label .
            FILTER(LANG(?label) = "en")
        }
        FILTER EXISTS {
            {?game dbo:releaseDate ?rdd .}
             UNION
            {?game dbp:released ?rd .
            FILTER NOT EXISTS {
                ?game dbo:releaseDate ?r .
            }
            }
        }
    }
    """
    total_games = int(query_dbpedia(endpoint, query_number_games)["results"]["bindings"][0]["nGames"]["value"])
    print(total_games)
    
    curr_offset = 0
    out_dict = {"date": str(datetime.datetime.now()), "games": {}}
    aux_game_list = []
    while curr_offset < total_games:
        query_games_uri = f"""
        SELECT ?game ?label (GROUP_CONCAT(DISTINCT ?d; separator="; ") as ?dates) WHERE {{
            {{?game a dbo:VideoGame ;
                    rdfs:label ?label ;
                    dbo:releaseDate ?d .
            }}
            UNION
            {{?game a dbo:VideoGame ;
                    rdfs:label ?label ;
                    dbp:released ?d .
            FILTER NOT EXISTS {{
            ?game dbo:releaseDate ?rd .
            }}
            }}
            FILTER(LANG(?label) = "en")
        }}
        OFFSET {curr_offset}
        LIMIT 10000
        """
        aux_game_list += query_dbpedia(endpoint, query_games_uri)["results"]["bindings"]
        curr_offset += 10000
    
    
    for entry in aux_game_list:
        out_dict["games"][entry["game"]["value"]] = (entry["label"]["value"], entry["dates"]["value"])
    aux_game_list = []
    
    with open(out_filename, "w", encoding="utf-8") as f:
        json.dump(out_dict, f, ensure_ascii=False)
    print(len(list(out_dict["games"].keys())))
    
def main():
    if "uri_label_dates_dbpedia" not in os.listdir():
        os.mkdir("uri_label_dates_dbpedia")
    get_uris_from_dbpedia("uri_label_dates_dbpedia/games_uris_dbpedia.json")
    
    
if __name__ == "__main__":
    main()


