import json, requests, os
import datetime, time
from uri_label_dates_dbpedia import query_dbpedia, endpoint
from game_info_dbpedia import is_list_empty

def check_missing_games(uris_filename, out_filename, out_series_filename, out_devs_filename, out_eng_filename, out_genre_filename, out_pub_filename, out_plat_filename):
    fout = open(out_filename, "r", encoding='utf-8')    
    out_games = json.load(fout)
    fout.close()
    all_uris_curr = [entry["uri"] for entry in out_games["games"]]
    
    
    furis = open(uris_filename, "r", encoding='utf-8')
    all_uris_missing = []
    for k in json.load(furis)["games"].keys():
        if k not in all_uris_curr:
            all_uris_missing.append(k)
    furis.close()
    all_uris_curr.clear()
    
    if len(all_uris_missing) > 0:
        print(f"detected {len(all_uris_missing)} missing URIs in final dataset. Fetching the remaining info...")
        fser = open(out_series_filename, "a", encoding='utf-8')
        fdevs = open(out_devs_filename, "a", encoding='utf-8')
        feng = open(out_eng_filename, "a", encoding='utf-8')
        fgen = open(out_genre_filename, "a", encoding='utf-8')
        fpub = open(out_pub_filename, "a", encoding='utf-8')
        fplat = open(out_plat_filename, "a", encoding='utf-8')
        
        i = 0
        while i < len(all_uris_missing):
            values = "".join(f"<{uri}>\n" for uri in all_uris_missing[i : (i+50 if i+50 < len(all_uris_missing) else len(all_uris_missing))])
            query_info_1 = f"""
            SELECT ?game (GROUP_CONCAT(DISTINCT ?ser; separator="; ") as ?series) (GROUP_CONCAT(DISTINCT ?ser2; separator="; ") as ?series2)
                (GROUP_CONCAT(DISTINCT ?dev; separator="; ") as ?devs) (GROUP_CONCAT(DISTINCT ?dev2; separator="; ") as ?devs2) 
                (GROUP_CONCAT(DISTINCT ?eng; separator="; ") as ?engine) (GROUP_CONCAT(DISTINCT ?eng2; separator="; ") as ?engine2) 
                (GROUP_CONCAT(DISTINCT ?gen; separator="; ") as ?genre) (GROUP_CONCAT(DISTINCT ?gen2; separator="; ") as ?genre2)
                (GROUP_CONCAT(DISTINCT ?pub; separator="; ") as ?publisher) (GROUP_CONCAT(DISTINCT ?pub2; separator="; ") as ?publisher2)
                (GROUP_CONCAT(DISTINCT ?mc; separator="; ") as ?metacritic)
                (GROUP_CONCAT(DISTINCT ?abs; separator="; ") as ?abstract) WHERE {{
                VALUES ?game {{ {values} }}
                ?game a dbo:VideoGame.
                OPTIONAL{{?game dbo:series ?ser .}}
                OPTIONAL{{?game dbp:series ?ser2 .}}
                OPTIONAL{{?game dbo:developer ?dev .}}
                OPTIONAL{{?game dbp:developer ?dev2 .}}
                OPTIONAL{{?game dbo:gameEngine ?eng .}}
                OPTIONAL{{?game dbp:engine ?eng2 .}}
                OPTIONAL{{?game dbo:genre ?gen .}}
                OPTIONAL{{?game dbp:genre ?gen2 .}}
                OPTIONAL{{?game dbo:publisher ?pub .}}
                OPTIONAL{{?game dbp:publisher ?pub2 .}}
                OPTIONAL{{?game dbp:mc ?mc .}}
                OPTIONAL{{?game dbo:abstract ?abs .}}
                # tirei o filter do abstract de ingles pq os jogos missing não têm
            }} GROUP BY ?game
            """
            query_info_2 = f"""
            SELECT ?game (GROUP_CONCAT(DISTINCT ?plat; separator="; ") as ?platforms) (GROUP_CONCAT(DISTINCT ?plat2; separator="; ") as ?platforms2) 
            (GROUP_CONCAT(DISTINCT ?plat3; separator="; ") as ?platforms3) WHERE {{
                VALUES ?game {{ {values} }}
                ?game a dbo:VideoGame.
                OPTIONAL{{?game dbo:computingPlatform ?plat .}}
                OPTIONAL{{?game dbp:platforms ?plat2 .}}
                OPTIONAL{{?game dbp:platform ?plat3 .}}
            }} GROUP BY ?game
            """
            print(query_info_1)
            responses = query_dbpedia(endpoint, query_info_1)["results"]["bindings"]
            responses2 = query_dbpedia(endpoint, query_info_2)["results"]["bindings"]
            print(responses)
            responses.sort(key=lambda x: x["game"]["value"])
            responses2.sort(key=lambda x: x["game"]["value"])
            print(i)
            for j in range(0, len(responses)):
                print(j)
                response = {
                    "uri": responses[j]["game"]["value"],
                    "series": list(set(responses[j]["series"]["value"].split("; "))),
                    "series2": list(set(responses[j]["series2"]["value"].split("; "))),
                    "devs": list(set(responses[j]["devs"]["value"].split("; "))),
                    "devs2": list(set(responses[j]["devs2"]["value"].split("; "))),
                    "engine": list(set(responses[j]["engine"]["value"].split("; "))),
                    "engine2": list(set(responses[j]["engine2"]["value"].split("; "))),
                    "genre": list(set(responses[j]["genre"]["value"].split("; "))),
                    "genre2": list(set(responses[j]["genre2"]["value"].split("; "))),
                    "publisher": list(set(responses[j]["publisher"]["value"].split("; "))),
                    "publisher2": list(set(responses[j]["publisher2"]["value"].split("; "))),
                    "metacritic": list(set(responses[j]["metacritic"]["value"].split("; "))),
                    "platforms": list(set(responses2[j]["platforms"]["value"].split("; "))),
                    "platforms2": list(set(responses2[j]["platforms2"]["value"].split("; "))),
                    "platforms3": list(set(responses2[j]["platforms3"]["value"].split("; "))),
                    "abstract": list(set(responses[j]["abstract"]["value"].split("; ")))
                }
                
                if not is_list_empty(response["series"]):
                    fser.write(json.dumps({"series": response["series"]}, ensure_ascii=False) + "\n")
                    response.pop("series2", None)
                elif not is_list_empty(response["series2"]):
                    fser.write(json.dumps({"series": response["series2"]}, ensure_ascii=False) + "\n")
                    response["series"] = response["series2"]
                    response.pop("series2", None)
                else:
                    fser.write(json.dumps({"series": []}, ensure_ascii=False) + "\n")
                    response.pop("series2", None)
                    
                if not is_list_empty(response["devs"]):
                    fdevs.write(json.dumps({"devs": response["devs"]}, ensure_ascii=False) + "\n")
                    response.pop("devs2", None)
                elif not is_list_empty(response["devs2"]):
                    fdevs.write(json.dumps({"devs": response["devs2"]}, ensure_ascii=False) + "\n")
                    response["devs"] = response["devs2"]
                    response.pop("devs2", None)
                else:
                    fdevs.write(json.dumps({"devs": []}, ensure_ascii=False) + "\n")
                    response.pop("devs2", None)
                    
                if not is_list_empty(response["engine"]):
                    feng.write(json.dumps({"engine": response["engine"]}, ensure_ascii=False) + "\n")
                    response.pop("engine2", None)
                elif not is_list_empty(response["engine2"]):
                    feng.write(json.dumps({"engine": response["engine2"]}, ensure_ascii=False) + "\n")
                    response["engine"] = response["engine2"]
                    response.pop("engine2", None)
                else:
                    feng.write(json.dumps({"engine": []}, ensure_ascii=False) + "\n")
                    response.pop("engine2", None)
                
                if not is_list_empty(response["genre"]):
                    fgen.write(json.dumps({"genre": response["genre"]}, ensure_ascii=False) + "\n")
                    response.pop("genre2", None)
                elif not is_list_empty(response["genre2"]):
                    fgen.write(json.dumps({"genre": response["genre2"]}, ensure_ascii=False) + "\n")
                    response["genre"] = response["genre2"]
                    response.pop("genre2", None)
                else:
                    fgen.write(json.dumps({"genre": []}, ensure_ascii=False) + "\n")
                    response.pop("genre2", None)
                    
                if not is_list_empty(response["publisher"]):
                    fpub.write(json.dumps({"publisher": response["publisher"]}, ensure_ascii=False) + "\n")
                    response.pop("publisher2", None)
                elif not is_list_empty(response["publisher2"]):
                    fpub.write(json.dumps({"publisher": response["publisher2"]}, ensure_ascii=False) + "\n")
                    response["publisher"] = response["publisher2"]
                    response.pop("publisher2", None)
                else:
                    fpub.write(json.dumps({"publisher": []}, ensure_ascii=False) + "\n")
                    response.pop("publisher2", None)
                    
                if not is_list_empty(response["platforms"]):
                    fplat.write(json.dumps({"platforms": response["platforms"]}, ensure_ascii=False) + "\n")
                    response.pop("platforms2", None)
                    response.pop("platforms3", None)
                elif not is_list_empty(response["platforms2"]):
                    fplat.write(json.dumps({"platforms": response["platforms2"]}, ensure_ascii=False) + "\n")
                    response["platforms"] = response["platforms2"]
                    response.pop("platforms2", None)
                    response.pop("platforms3", None)
                elif not is_list_empty(response["platforms3"]):
                    fplat.write(json.dumps({"platforms": response["platforms3"]}, ensure_ascii=False) + "\n")
                    response["platforms"] = response["platforms3"]
                    response.pop("platforms2", None)
                    response.pop("platforms3", None)
                else:
                    fplat.write(json.dumps({"platforms": []}, ensure_ascii=False) + "\n")
                    response.pop("platforms2", None)
                    response.pop("platforms3", None)
                    
                out_games["games"].append(response)
                
            print("waiting 5 seconds before next GET...")
            time.sleep(5)
            i += 50 
        
        os.remove(out_filename)
        with open(out_filename, "w", encoding='utf-8') as fout:
            json.dump(out_games, fout, ensure_ascii=False)
        
        fser.close()
        fdevs.close()
        feng.close()
        fgen.close()
        fpub.close()
        fplat.close()
        
        ####################################################################################
        a = len(out_games["games"])
        with open(uris_filename, "r", encoding='utf-8') as fNaux:
            b = len(list(json.load(fNaux)["games"].keys()))

        if b - a > 0:
            print(f"there are still {b-a} missing URIs. Run me again to complete please.")
        else:
            print("missing URIs fetching complete.")
        ####################################################################################
        
    else:
        print("no missing URIs detected.")
    


def main():
    if "final_datasets_dbpedia" not in os.listdir():
        os.mkdir("final_datasets_dbpedia")
    if "game_info_dbpedia" not in os.listdir():
        os.mkdir("game_info_dbpedia")
        
    check_missing_games("uri_label_dates_dbpedia/games_uris_dbpedia.json", "final_datasets_dbpedia/games_dbpedia.json", "game_info_dbpedia/seriesURIsOUT.txt", 
                   "game_info_dbpedia/devsURIsOUT.txt", "game_info_dbpedia/engineURIsOUT.txt", "game_info_dbpedia/genreURIsOUT.txt", 
                   "game_info_dbpedia/publisherURIsOUT.txt", "game_info_dbpedia/platformsURIsOUT.txt")
    
    

if __name__ == "__main__":
    main()