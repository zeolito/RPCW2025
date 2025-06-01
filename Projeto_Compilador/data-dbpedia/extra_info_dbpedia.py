import json, requests
import datetime, time
from uri_label_dates_dbpedia import query_dbpedia, endpoint
from game_info_dbpedia import is_list_empty


def collect_URIs(URIs_txt, dict_key):
    all_URIs = []
    all_Names = []
    with open(URIs_txt, "r", encoding='utf-8') as fs:
        for line in fs.readlines():
            curr_series_list = json.loads(line.strip())[dict_key]
            for s in curr_series_list:
                if s.strip() != "":
                    if ("http://dbpedia.org/" in s) and (s not in all_URIs):
                        all_URIs.append(s)
                    elif ("http://dbpedia.org/" not in s) and (s not in all_Names):
                        all_Names.append(s)
    return (all_URIs, all_Names)

def get_series_info(series_URIs_txt, out_json_filename):
    out_dict = {}
    (all_series, all_series_Names) = collect_URIs(series_URIs_txt, "series")
    for sN in all_series_Names:
        out_dict[sN] = {
            "name": [sN],
            "abstract": [sN + " is a video game series."],
            "debutDate": []
        }
        
    i = 0
    while i < len(all_series):
        values = "".join(f"<{uri}>\n" for uri in all_series[i : (i+50 if i+50 < len(all_series) else len(all_series))])
        query_series = f"""
        SELECT ?series (GROUP_CONCAT(DISTINCT ?label; separator="; ") as ?labels) (GROUP_CONCAT(DISTINCT ?date; separator="; ") as ?dates) (GROUP_CONCAT(DISTINCT ?abs; separator="; ") as ?abstract) WHERE {{
            VALUES ?series {{ {values} }}
            ?series rdfs:label ?label .
            OPTIONAL{{?series dbo:abstract ?abs .}}
            OPTIONAL{{?series dbp:firstReleaseDate ?date .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?series
        """
        responses = query_dbpedia(endpoint, query_series)["results"]["bindings"]
        responses.sort(key=lambda x: x["series"]["value"])
        print(i)
        for j in range(0, len(responses)):
            out_dict[responses[j]["series"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; "))),
                "debutDate": list(set(responses[j]["dates"]["value"].split("; ")))
            }
        
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def get_eng_info(eng_URIs_txt, devs_URIs_txt, platforms_URIs_txt, out_json_filename):
    out_dict = {}
    (all_eng_URIs, all_eng_Names) = collect_URIs(eng_URIs_txt, "engine")
    
    for engN in all_eng_Names:
        out_dict[engN] = {
            "name": [engN],
            "abstract": [engN + " is a videogame engine."],
            "platforms": [],
            "devs": []
        }
    i = 0
    while i < len(all_eng_URIs):
        values = "".join(f"<{uri}>\n" for uri in all_eng_URIs[i : (i+50 if i+50 < len(all_eng_URIs) else len(all_eng_URIs))])
        query_eng = f"""
        SELECT ?eng (GROUP_CONCAT(DISTINCT ?label; separator="; ") as ?labels) (GROUP_CONCAT(DISTINCT ?abs; separator="; ") as ?abstract) 
        (GROUP_CONCAT(DISTINCT ?plat; separator="; ") as ?platforms) (GROUP_CONCAT(DISTINCT ?plat2; separator="; ") as ?platforms2)
        (GROUP_CONCAT(DISTINCT ?dev; separator="; ") as ?devs) (GROUP_CONCAT(DISTINCT ?dev2; separator="; ") as ?devs2) WHERE {{
            VALUES ?eng {{ {values} }}
            ?eng rdfs:label ?label .
            OPTIONAL{{?eng dbo:abstract ?abs .}}
            OPTIONAL{{?eng dbo:computingPlatform ?plat .}}
            OPTIONAL{{?eng dbp:platform ?plat2 .}}
            OPTIONAL{{?eng dbp:dbo:developer ?dev .}}
            OPTIONAL{{?eng dbp:developer ?dev2 .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?eng
        """
        responses = query_dbpedia(endpoint, query_eng)["results"]["bindings"]
        responses.sort(key=lambda x: x["eng"]["value"])
        for j in range(0, len(responses)):
            platform_list = list(set(responses[j]["platforms"]["value"].split("; ")))
            platform2_list = list(set(responses[j]["platforms2"]["value"].split("; ")))
            platform_list = platform_list if not is_list_empty(platform_list) else (platform2_list if not is_list_empty(platform2_list) else [])
            devs_list = list(set(responses[j]["devs"]["value"].split("; ")))
            devs2_list = list(set(responses[j]["devs2"]["value"].split("; ")))
            devs_list = devs_list if not is_list_empty(devs_list) else (devs2_list if not is_list_empty(devs2_list) else [])
            out_dict[responses[j]["eng"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; "))),
                "platforms": platform_list,
                "devs": devs_list
            }
            fplats = open(platforms_URIs_txt, "a", encoding='utf-8')
            fdevs = open(devs_URIs_txt, "a", encoding='utf-8')
            fplats.write(json.dumps({"platforms": platform_list}, ensure_ascii=False) + "\n")
            fdevs.write(json.dumps({"devs": devs_list}, ensure_ascii=False) + "\n")
            fplats.close(); fdevs.close()
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def get_platforms_info(platforms_URIs_txt, devs_URIs_txt, fam_URIs_txt, out_json_filename):
    out_dict = {}
    (all_plat_URIs, all_plat_Names) = collect_URIs(platforms_URIs_txt, "platforms")
    for platN in all_plat_Names:
        out_dict[platN] = {
            "name": [platN],
            "abstract": [platN + " is a videogame platform."],
            "debutDate": [],
            "devs": [],
            "families": []
        }
    i = 0
    while i < len(all_plat_URIs):
        values = "".join(f"<{uri}>\n" for uri in all_plat_URIs[i : (i+50 if i+50 < len(all_plat_URIs) else len(all_plat_URIs))])
        query_platform = f"""
        SELECT ?plat (GROUP_CONCAT(?label; separator="; ") as ?labels) (GROUP_CONCAT(?abs; separator="; ") as ?abstract) 
        (GROUP_CONCAT(?date; separator="; ") as ?dates) (GROUP_CONCAT(?dev; separator="; ") as ?devs) 
        (GROUP_CONCAT(?fam; separator="; ") as ?families) WHERE {{
            VALUES ?plat {{ {values} }}
            ?plat rdfs:label ?label .
            OPTIONAL{{?plat dbo:abstract ?abs .}}
            OPTIONAL{{?plat dbp:date ?date .}}
            OPTIONAL{{?plat dbp:developer ?dev .}}
            OPTIONAL{{?plat dbp:family ?fam .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?plat
        """
        responses = query_dbpedia(endpoint, query_platform)["results"]["bindings"]
        responses.sort(key=lambda x: x["plat"]["value"])
        for j in range(0, len(responses)):
            devs_list = list(set(responses[j]["devs"]["value"].split("; ")))
            devs_list = devs_list if not is_list_empty(devs_list) else []
            fDevs = open(devs_URIs_txt, "a", encoding='utf-8')
            fDevs.write(json.dumps({"devs": devs_list}, ensure_ascii=False) + "\n")
            fDevs.close()
            
            fam_list = list(set(responses[j]["families"]["value"].split("; ")))
            fFam = open(fam_URIs_txt, "a", encoding='utf-8')
            fFam.write(json.dumps({"families": fam_list}, ensure_ascii=False) + "\n")
            fFam.close()
                
            out_dict[responses[j]["plat"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; "))),
                "debutDate": list(set(responses[j]["dates"]["value"].split("; "))),
                "devs": devs_list,
                "families": fam_list
            }
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)

def get_fams_info(fam_URIs_txt, out_json_filename):
    out_dict = {}
    (all_fam_URIs, all_fam_Names) = collect_URIs(fam_URIs_txt, "families")
    for famN in all_fam_Names:
        out_dict[famN] = {
            "name": [famN],
            "abstract": [famN + " is a videogame platform family."]
        }
    i = 0
    while i < len(all_fam_URIs):
        values = "".join(f"<{uri}>\n" for uri in all_fam_URIs[i : (i+50 if i+50 < len(all_fam_URIs) else len(all_fam_URIs))])
        query_fam = f"""
        SELECT ?fam (GROUP_CONCAT(?label; separator="; ") as ?labels) (GROUP_CONCAT(?abs; separator="; ") as ?abstract) WHERE {{
            VALUES ?fam {{ {values} }}
            ?fam rdfs:label ?label .
            OPTIONAL{{?fam dbo:abstract ?abs .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?fam
        """
        responses = query_dbpedia(endpoint, query_fam)["results"]["bindings"]
        responses.sort(key=lambda x: x["fam"]["value"])
        for j in range(0, len(responses)):
            out_dict[responses[j]["fam"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; ")))
            }
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def get_devs_info(devs_URIs_txt, out_json_filename):
    out_dict = {}
    (all_devs_URIs, all_devs_Names) = collect_URIs(devs_URIs_txt, "devs")
    for devN in all_devs_Names:
        out_dict[devN] = {
            "name": [devN],
            "abstract": [devN + " is a videogame development company."],
            "debutDate": []
        }
    i = 0
    while i < len(all_devs_URIs):
        values = "".join(f"<{uri}>\n" for uri in all_devs_URIs[i : (i+50 if i+50 < len(all_devs_URIs) else len(all_devs_URIs))])
        query_dev = f"""
        SELECT ?dev (GROUP_CONCAT(?label; separator="; ") as ?labels) (GROUP_CONCAT(?date; separator="; ") as ?dates) (GROUP_CONCAT(?date2; separator="; ") as ?dates2) (GROUP_CONCAT(?date3; separator="; ") as ?dates3) (GROUP_CONCAT(?abs; separator="; ") as ?abstract) WHERE {{
            VALUES ?dev {{ {values} }}
            ?dev rdfs:label ?label .
            OPTIONAL{{?dev dbo:abstract ?abs .}}
            OPTIONAL{{?dev dbo:foundingDate ?date .}}
            OPTIONAL{{?dev dbp:foundation ?date2 .}}
            OPTIONAL{{?dev dbo:foundingYear ?date3 .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?dev
        """
        responses = query_dbpedia(endpoint, query_dev)["results"]["bindings"]
        responses.sort(key=lambda x: x["dev"]["value"])
        for j in range(0, len(responses)):
            dates_list = list(set(responses[j]["dates"]["value"].split("; ")))
            dates2_list = list(set(responses[j]["dates2"]["value"].split("; ")))
            dates3_list = list(set(responses[j]["dates3"]["value"].split("; ")))
            dates_list = dates_list if not is_list_empty(dates_list) else (dates2_list if not is_list_empty(dates2_list) else (dates3_list if not is_list_empty(dates3_list) else []))
            out_dict[responses[j]["dev"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; "))),
                "debutDate": dates_list
            }
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)

def get_pubs_info(pubs_URIs_txt, out_json_filename):
    out_dict = {}
    (all_pubs_URIs, all_pubs_Names) = collect_URIs(pubs_URIs_txt, "publisher")
    for pubN in all_pubs_Names:
        out_dict[pubN] = {
            "name": [pubN],
            "abstract": [pubN + " is a videogame publishing company."],
            "debutDate": []
        }
    i = 0
    while i < len(all_pubs_URIs):
        values = "".join(f"<{uri}>\n" for uri in all_pubs_URIs[i : (i+50 if i+50 < len(all_pubs_URIs) else len(all_pubs_URIs))])
        query_pub = f"""
        SELECT ?pub (GROUP_CONCAT(?label; separator="; ") as ?labels) (GROUP_CONCAT(?date; separator="; ") as ?dates) (GROUP_CONCAT(?date2; separator="; ") as ?dates2) (GROUP_CONCAT(?date3; separator="; ") as ?dates3) (GROUP_CONCAT(?abs; separator="; ") as ?abstract) WHERE {{
            VALUES ?pub {{ {values} }}
            ?pub rdfs:label ?label .
            OPTIONAL{{?pub dbo:abstract ?abs .}}
            OPTIONAL{{?pub dbo:foundingDate ?date .}}
            OPTIONAL{{?pub dbp:foundation ?date2 .}}
            OPTIONAL{{?pub dbo:foundingYear ?date3 .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?pub
        """
        responses = query_dbpedia(endpoint, query_pub)["results"]["bindings"]
        responses.sort(key=lambda x: x["pub"]["value"])
        for j in range(0, len(responses)):
            dates_list = list(set(responses[j]["dates"]["value"].split("; ")))
            dates2_list = list(set(responses[j]["dates2"]["value"].split("; ")))
            dates3_list = list(set(responses[j]["dates3"]["value"].split("; ")))
            dates_list = dates_list if not is_list_empty(dates_list) else (dates2_list if not is_list_empty(dates2_list) else (dates3_list if not is_list_empty(dates3_list) else []))
            out_dict[responses[j]["pub"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; "))),
                "debutDate": dates_list
            }    
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def get_genres_info(genres_URIs_txt, out_json_filename):
    out_dict = {}
    (all_genres_URIs, all_genres_Names) = collect_URIs(genres_URIs_txt, "genre")
    for genN in all_genres_Names:
        out_dict[genN] = {
            "name": [genN],
            "abstract": [genN + " is a videogame genre."]
        }
    i = 0
    while i < len(all_genres_URIs):
        values = "".join(f"<{uri}>\n" for uri in all_genres_URIs[i : (i+50 if i+50 < len(all_genres_URIs) else len(all_genres_URIs))])
        query_genre = f"""
        SELECT ?gen (GROUP_CONCAT(?label; separator="; ") as ?labels) (GROUP_CONCAT(?abs; separator="; ") as ?abstract) WHERE {{
            VALUES ?gen {{ {values} }}
            ?gen rdfs:label ?label .
            OPTIONAL{{?gen dbo:abstract ?abs .}}
            FILTER(LANG(?label)="en")
            FILTER(LANG(?abs)="en")
        }}GROUP BY ?gen
        """
        responses = query_dbpedia(endpoint, query_genre)["results"]["bindings"]
        responses.sort(key=lambda x: x["gen"]["value"])
        for j in range(0, len(responses)):
            out_dict[responses[j]["gen"]["value"]] = {
                "name": list(set(responses[j]["labels"]["value"].split("; "))),
                "abstract": list(set(responses[j]["abstract"]["value"].split("; ")))
            }
        print("waiting 5 secs before next pull...")
        time.sleep(5)
        i += 50
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
                        
def main():
    print("extracting series info...")
    get_series_info("game_info_dbpedia/seriesURIsOUT.txt", "final_datasets_dbpedia/series_info.json")
    print("series success.")
    time.sleep(1)
    print("extracting engines info...")
    get_eng_info("game_info_dbpedia/engineURIsOUT.txt", "game_info_dbpedia/devsURIsOUT.txt", "game_info_dbpedia/platformsURIsOUT.txt", "final_datasets_dbpedia/engines_info.json")
    print("engines success.")
    time.sleep(1)
    print("extracting platforms info...")
    get_platforms_info("game_info_dbpedia/platformsURIsOUT.txt", "game_info_dbpedia/devsURIsOUT.txt", "game_info_dbpedia/familiesURIsOUT.txt", "final_datasets_dbpedia/platforms_info.json")
    print("platforms success.")
    time.sleep(1)
    print("extracting console families info...")
    get_fams_info("game_info_dbpedia/familiesURIsOUT.txt", "final_datasets_dbpedia/families_info.json")
    print("families success.")
    time.sleep(1)
    print("extracting devs info...")
    get_devs_info("game_info_dbpedia/devsURIsOUT.txt", "final_datasets_dbpedia/devs_info.json")
    print("devs success.")
    time.sleep(1)
    print("extracting publishers info...")
    get_pubs_info("game_info_dbpedia/publisherURIsOUT.txt", "final_datasets_dbpedia/publishers_info.json")
    print("publishers success.")
    time.sleep(1)
    print("extracting genres info...")
    get_genres_info("game_info_dbpedia/genreURIsOUT.txt", "final_datasets_dbpedia/genres_info.json")
    print("genres success.")
    print("all done.")

if __name__ == "__main__":
    main()