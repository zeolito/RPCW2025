import json, requests, os
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

def collect_missing(txt_filename, dict_key, final_filename):
    (all_txt_URIs, all_txt_Names) = collect_URIs(txt_filename, dict_key)
    
    with open(final_filename, "r", encoding='utf-8') as f:
        all_final = json.load(f)
    all_final = list(all_final.keys())
    all_final_miss_URIs = set()
    all_final_miss_Names = set()
    
    for e in all_txt_URIs:
        if (e not in all_final):
            all_final_miss_URIs.add(e)
    for e in all_txt_Names:
        if (e not in all_final):
            all_final_miss_Names.add(e)
            
    if len(all_final_miss_URIs) > 0 or len(all_final_miss_Names) > 0:
        print(f"detected missing for type '{dict_key}'")
    else:
        print(f"no missing for type '{dict_key}'")
    
    return (list(all_final_miss_URIs), list(all_final_miss_Names))

def complete_series_info(series_URIs_txt, out_json_filename):
    out_dict = {}
    (all_series, all_series_Names) = collect_missing(series_URIs_txt, "series", out_json_filename)
    for sN in all_series_Names:
        out_dict[sN] = {
            "name": [sN],
            "abstract": [sN + " is a video game series."],
            "debutDate": []
        }
        
    for sURI in all_series:
        out_dict[sURI] = {
                "name": [sURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
                "abstract": [sURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a video game series."],
                "debutDate": []
            }
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        

def complete_eng_info(eng_URIs_txt, devs_URIs_txt, platforms_URIs_txt, out_json_filename):
    out_dict = {}
    (all_eng_URIs, all_eng_Names) = collect_missing(eng_URIs_txt, "engine", out_json_filename)
    
    for engN in all_eng_Names:
        out_dict[engN] = {
            "name": [engN],
            "abstract": [engN + " is a videogame engine."],
            "platforms": [],
            "devs": []
        }
    for engURI in all_eng_URIs:
        out_dict[engURI] = {
            "name": [engURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
            "abstract": [engURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a videogame engine."],
            "platforms": [],
            "devs": []
        }
    
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def complete_platforms_info(platforms_URIs_txt, devs_URIs_txt, fam_URIs_txt, out_json_filename):
    out_dict = {}
    (all_plat_URIs, all_plat_Names) = collect_missing(platforms_URIs_txt, "platforms", out_json_filename)
    for platN in all_plat_Names:
        out_dict[platN] = {
            "name": [platN],
            "abstract": [platN + " is a videogame platform."],
            "debutDate": [],
            "devs": [],
            "families": []
        }
    for platURI in all_plat_URIs:
        out_dict[platURI] = {
            "name": [platURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
            "abstract": [platURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a videogame platform."],
            "debutDate": [],
            "devs": [],
            "families": []
        }
    
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def complete_fams_info(fam_URIs_txt, out_json_filename):
    out_dict = {}
    (all_fam_URIs, all_fam_Names) = collect_missing(fam_URIs_txt, "families", out_json_filename)
    for famN in all_fam_Names:
        out_dict[famN] = {
            "name": [famN],
            "abstract": [famN + " is a videogame platform family."]
        }
    for famURI in all_fam_URIs:
        out_dict[famURI] = {
            "name": [famURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
            "abstract": [famURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a videogame platform family."]
        }
    
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def complete_devs_info(devs_URIs_txt, out_json_filename):
    out_dict = {}
    (all_devs_URIs, all_devs_Names) = collect_missing(devs_URIs_txt, "devs", out_json_filename)
    for devN in all_devs_Names:
        out_dict[devN] = {
            "name": [devN],
            "abstract": [devN + " is a videogame development company."],
            "debutDate": []
        }
    for devURI in all_devs_URIs:
        out_dict[devURI] = {
            "name": [devURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
            "abstract": [devURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a videogame development company."],
            "debutDate": []
        }
    
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
        
def complete_pubs_info(pubs_URIs_txt, out_json_filename):
    out_dict = {}
    (all_pubs_URIs, all_pubs_Names) = collect_missing(pubs_URIs_txt, "publisher", out_json_filename)
    for pubN in all_pubs_Names:
        out_dict[pubN] = {
            "name": [pubN],
            "abstract": [pubN + " is a videogame publishing company."],
            "debutDate": []
        }
    for pubURI in all_pubs_URIs:
        out_dict[pubURI] = {
            "name": [pubURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
            "abstract": [pubURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a videogame publishing company."],
            "debutDate": []
        }
    
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)

def complete_genres_info(genres_URIs_txt, out_json_filename):
    out_dict = {}
    (all_genres_URIs, all_genres_Names) = collect_missing(genres_URIs_txt, "genre", out_json_filename)
    for genN in all_genres_Names:
        out_dict[genN] = {
            "name": [genN],
            "abstract": [genN + " is a videogame genre."]
        }
    for genURI in all_genres_URIs:
        out_dict[genURI] = {
            "name": [genURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ")],
            "abstract": [genURI.split("http://dbpedia.org/resource/")[-1].replace("_", " ") + " is a videogame genre."]
        }
    
    with open(out_json_filename, "r", encoding='utf-8') as outF:
        old_dict = json.load(outF)
    
    out_dict.update(old_dict)
    os.remove(out_json_filename)
    with open(out_json_filename, "w", encoding='utf-8') as outF:
        json.dump(out_dict, outF, ensure_ascii=False)
    
def main():
    print("starting to fill missing empty info...")
    print("extracting series info...")
    complete_series_info("game_info_dbpedia/seriesURIsOUT.txt", "final_datasets_dbpedia/series_info.json")
    print("series success.")
    time.sleep(1)
    print("extracting engines info...")
    complete_eng_info("game_info_dbpedia/engineURIsOUT.txt", "game_info_dbpedia/devsURIsOUT.txt", "game_info_dbpedia/platformsURIsOUT.txt", "final_datasets_dbpedia/engines_info.json")
    print("engines success.")
    time.sleep(1)
    print("extracting platforms info...")
    complete_platforms_info("game_info_dbpedia/platformsURIsOUT.txt", "game_info_dbpedia/devsURIsOUT.txt", "game_info_dbpedia/familiesURIsOUT.txt", "final_datasets_dbpedia/platforms_info.json")
    print("platforms success.")
    time.sleep(1)
    print("extracting console families info...")
    complete_fams_info("game_info_dbpedia/familiesURIsOUT.txt", "final_datasets_dbpedia/families_info.json")
    print("families success.")
    time.sleep(1)
    print("extracting devs info...")
    complete_devs_info("game_info_dbpedia/devsURIsOUT.txt", "final_datasets_dbpedia/devs_info.json")
    print("devs success.")
    time.sleep(1)
    print("extracting publishers info...")
    complete_pubs_info("game_info_dbpedia/publisherURIsOUT.txt", "final_datasets_dbpedia/publishers_info.json")
    print("publishers success.")
    time.sleep(1)
    print("extracting genres info...")
    complete_genres_info("game_info_dbpedia/genreURIsOUT.txt", "final_datasets_dbpedia/genres_info.json")
    print("genres success.")
    print("all done.")
    
if __name__ == "__main__":
    main()