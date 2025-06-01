import json
import re
import os
from rdflib import Graph, Namespace, RDF, OWL, URIRef, Literal, XSD, RDFS

n = Namespace("http://rpcw.di.uminho.pt/2025/videogames#")
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

index = 0
deviceSet = set()
genreSet = set()

folder_path = "archive/VideoGames/"
files = os.listdir(folder_path)

i=0

for filename in files:
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="UTF-8") as file:
            data = json.load(file)
        for value in data["games"]:
            if i%2500 == 0 and i > 0:
                g.serialize(format="turtle",destination=f"turtle/videgame_ontology{index}.ttl")
                index += 1
                g = Graph()
                g.parse("turtle/videgame_base.ttl")
                
                g.bind("\n", n)
                g.bind("owl", OWL)
                g.bind("rdf", RDF)
                g.bind("rdfs", RDFS)
                g.bind("xsd", XSD)

            gameURI = URIRef(n + value["slug"].replace(" ","_"))
            g.add((gameURI, RDF.type, OWL.NamedIndividual))
            g.add((gameURI, RDF.type, n.Game))
            g.add((gameURI, n.Name, Literal(value["name"])))
            if value["esrb_rating"] and value["esrb_rating"] != "None":
                g.add((gameURI, n.ESRB_RATING, Literal(value["esrb_rating"]["name"])))
            else:
                g.add((gameURI, n.ESRB_RATING, Literal("None")))

            g.add((gameURI, n.Playtime, Literal(value["playtime"],datatype=XSD.float)))
            g.add((gameURI, n.Metacritic, Literal(value["metacritic"])))
            g.add((gameURI, n.Release_Date, Literal(value["released"])))


            if value["platforms"]:
                for platform in value["platforms"]:
                    platformURI = URIRef(n + platform["platform"]["slug"].replace(" ","_"))
                    if platform["platform"]["slug"] not in deviceSet:
                        deviceSet.add(platform["platform"]["slug"])
                        g.add((platformURI, RDF.type, OWL.NamedIndividual))
                        g.add((platformURI, RDF.type, n.Device))
                        g.add((platformURI, n.Name, Literal(platform["platform"]["name"])))

                    g.add((gameURI, n.availableOn, platformURI))

            if value["genres"]:
                for genre in value["genres"]:
                    genreURI = URIRef(n + genre["slug"].replace(" ","_"))
                    if genre["slug"] not in genreSet:
                        genreSet.add(genre["slug"])
                        g.add((genreURI, RDF.type, OWL.NamedIndividual))
                        g.add((genreURI, RDF.type, n.Genre))
                        g.add((genreURI, n.Name, Literal(genre["name"])))

                    g.add((gameURI, n.hasGenre, genreURI))

            if value["tags"]:
                for genre in value["tags"]:
                    if int(genre["id"]) < 50:
                        genreURI = URIRef(n + genre["slug"].replace(" ","_"))
                        if genre["slug"] not in genreSet:
                            genreSet.add(genre["slug"])
                            g.add((genreURI, RDF.type, OWL.NamedIndividual))
                            g.add((genreURI, RDF.type, n.Genre))
                            g.add((genreURI, n.Name, Literal(genre["name"])))

                        g.add((gameURI, n.hasGenre, genreURI))
            i += 1
g.close()
#########################################################################
################################ DBPEDIA ################################
#########################################################################

def is_list_empty(list):
    ret = True
    if list == []:
        return True
    for elem in list:
        if elem != "":
            ret = False
            break
    return ret

def joined_list(strList):
    res = []
    ret = ""
    if not is_list_empty(strList):
        for s in strList:
            if s.strip() != "":
                res.append(s)
        for i in range(0, len(res)):
            if i == len(res) - 1:
                ret += res[i]
            else:
                ret += res[i] + " ; "
    return ret

def isDateable(str):
    if re.search(r'^(19[4-9][0-9]|20[0-2][0-9])', str) is not None:
        return True
    elif re.search(r'(19[4-9][0-9]|20[0-2][0-9])', str) is not None:
        return re.search(r'(19[4-9][0-9]|20[0-2][0-9])', str)[0]
    else:
        return False

fGenres = open("data-dbpedia/final_datasets_dbpedia/genres_info.json", "r", encoding='utf-8')
fDevs = open("data-dbpedia/final_datasets_dbpedia/devs_info.json", "r", encoding='utf-8')
fPublishers = open("data-dbpedia/final_datasets_dbpedia/publishers_info.json", "r", encoding='utf-8')
fFamilies = open("data-dbpedia/final_datasets_dbpedia/families_info.json", "r", encoding='utf-8')
fPlatforms = open("data-dbpedia/final_datasets_dbpedia/platforms_info.json", "r", encoding='utf-8')
fEngines = open("data-dbpedia/final_datasets_dbpedia/engines_info.json", "r", encoding='utf-8')
fSeries = open("data-dbpedia/final_datasets_dbpedia/series_info.json", "r", encoding='utf-8')
fGames = open("data-dbpedia/final_datasets_dbpedia/games_dbpedia.json", "r", encoding='utf-8')

devs = set()
families = set()
engines = set()
series = set()
games = set()

######## GENRES ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_genres = json.load(fGenres)
fGenres.close()

for (uri, values) in all_genres.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        genreURI = URIRef(n + "GENRE_" + uriSplit.replace("&","AND"))
        if genreURI not in genreSet:
            genreSet.add(genreURI)
            g.add((genreURI, RDF.type, OWL.NamedIndividual))
            g.add((genreURI, RDF.type, n.Genre))
            g.add((genreURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((genreURI, n.Abstract, Literal(joined_list(values["abstract"]))))

for (uri, values) in all_genres.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        genreURI = URIRef(n + "GENRE_" + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if genreURI not in genreSet:
            genreSet.add(genreURI)
            g.add((genreURI, RDF.type, OWL.NamedIndividual))
            g.add((genreURI, RDF.type, n.Genre))
            g.add((genreURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((genreURI, n.Abstract, Literal(joined_list(values["abstract"]))))

all_genres = None
g.serialize(destination="turtle/videogame_dbpedia_genres.ttl", format="turtle")
g.close()
######## DEVELOPERS ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_devs = json.load(fDevs)
fDevs.close()

for (uri, values) in all_devs.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        devURI = URIRef(n + "DEVELOPER_" + uriSplit.replace("&","AND"))
        if devURI not in devs:
            devs.add(devURI)
            g.add((devURI, RDF.type, OWL.NamedIndividual))
            g.add((devURI, RDF.type, n.Developer))
            g.add((devURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((devURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((devURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
            
for (uri, values) in all_devs.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        devURI = URIRef(n + "DEVELOPER_" + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if devURI not in devs:
            devs.add(devURI)
            g.add((devURI, RDF.type, OWL.NamedIndividual))
            g.add((devURI, RDF.type, n.Developer))
            g.add((devURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((devURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((devURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
            
all_devs = None
g.serialize(destination="turtle/videogame_dbpedia_devs.ttl", format="turtle")
g.close()
######## PUBLISHERS ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_pubs = json.load(fPublishers)
fPublishers.close()

for (uri, values) in all_pubs.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        pubURI = URIRef(n + "DEVELOPER_" + uriSplit.replace("&","AND"))
        if pubURI not in devs:
            devs.add(pubURI)
            g.add((pubURI, RDF.type, OWL.NamedIndividual))
            g.add((pubURI, RDF.type, n.Developer))
            g.add((pubURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((pubURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((pubURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
            
for (uri, values) in all_pubs.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        pubURI = URIRef(n + "DEVELOPER_" + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if pubURI not in devs:
            devs.add(pubURI)
            g.add((pubURI, RDF.type, OWL.NamedIndividual))
            g.add((pubURI, RDF.type, n.Developer))
            g.add((pubURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((pubURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((pubURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))

all_pubs = None
g.serialize(destination="turtle/videogame_dbpedia_publishers.ttl", format="turtle")
g.close()

######## FAMILIES/platforms ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_fams = json.load(fFamilies)
fFamilies.close()

for (uri, values) in all_fams.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        famURI = URIRef(n + "PLATFORM_" + uriSplit.replace("&","AND"))
        if famURI not in families:
            families.add(famURI)
            g.add((famURI, RDF.type, OWL.NamedIndividual))
            g.add((famURI, RDF.type, n.Platform))
            g.add((famURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((famURI, n.Abstract, Literal(joined_list(values["abstract"]))))

for (uri, values) in all_fams.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        famURI = URIRef(n + "PLATFORM_"  + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if famURI not in families:
            families.add(famURI)
            g.add((famURI, RDF.type, OWL.NamedIndividual))
            g.add((famURI, RDF.type, n.Platform))
            g.add((famURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((famURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            
all_fams = None
g.serialize(destination="turtle/videogame_dbpedia_platforms.ttl", format="turtle")
g.close()
######## PLATFORMS/devices ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_plats = json.load(fPlatforms)
fPlatforms.close()

for (uri, values) in all_plats.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        platURI = URIRef(n + "DEVICE_" + uriSplit.replace("&","AND"))
        if platURI not in deviceSet:
            deviceSet.add(platURI)
            g.add((platURI, RDF.type, OWL.NamedIndividual))
            g.add((platURI, RDF.type, n.Device))
            g.add((platURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((platURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((platURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
            for dev in values["devs"]:
                if dev.strip() != "":
                    devURI = dev
                    if "http://dbpedia.org/" in dev:
                        devSplit = dev.split("http://dbpedia.org/resource/")[-1]
                        devSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', devSplit)
                        devURI = URIRef(n + "DEVELOPER_" + devSplit.replace("&","AND"))
                    else:
                        dev = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', dev)
                        devURI = URIRef(n + "DEVELOPER_" + dev.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if devURI in devs:
                        g.add((devURI, n.developedDevice, platURI))
                        g.add((platURI, n.deviceDevelopedBy, devURI))
            for fam in values["families"]:
                if fam.strip() != "":
                    famURI = fam
                    if "http://dbpedia.org/" in fam:
                        famSplit = fam.split("http://dbpedia.org/resource/")[-1]
                        famSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', famSplit)
                        famURI = URIRef(n + "PLATFORM_" + famSplit.replace("&","AND"))
                    else:
                        fam = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', fam)
                        famURI = URIRef(n + "PLATFORM_"  + fam.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if famURI in families:
                        g.add((famURI, n.isPlatformOf, platURI))
                        g.add((platURI, n.isDeviceFrom, famURI))

for (uri, values) in all_plats.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        platURI = URIRef(n + "DEVICE_" + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if platURI not in deviceSet:
            deviceSet.add(platURI)
            g.add((platURI, RDF.type, OWL.NamedIndividual))
            g.add((platURI, RDF.type, n.Device))
            g.add((platURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((platURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((platURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
            for dev in values["devs"]:
                if dev.strip() != "":
                    devURI = dev
                    if "http://dbpedia.org/" in dev:
                        devSplit = dev.split("http://dbpedia.org/resource/")[-1]
                        devSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', devSplit)
                        devURI = URIRef(n + "DEVELOPER_" + devSplit.replace("&","AND"))
                    else:
                        dev = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', dev)
                        devURI = URIRef(n + "DEVELOPER_" + dev.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if devURI in devs:
                        g.add((devURI, n.developedDevice, platURI))
                        g.add((platURI, n.deviceDevelopedBy, devURI))
            for fam in values["families"]:
                if fam.strip() != "":
                    famURI = fam
                    if "http://dbpedia.org/" in fam:
                        famSplit = fam.split("http://dbpedia.org/resource/")[-1]
                        famSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', famSplit)
                        famURI = URIRef(n + "PLATFORM_" + famSplit.replace("&","AND"))
                    else:
                        fam = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', fam)
                        famURI = URIRef(n + "PLATFORM_"  + fam.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if famURI in families:
                        g.add((famURI, n.isPlatformOf, platURI))
                        g.add((platURI, n.isDeviceFrom, famURI))

all_plats = None
g.serialize(destination="turtle/videogame_dbpedia_devices.ttl", format="turtle")
g.close()
######## ENGINES ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_engs = json.load(fEngines)
fEngines.close()

for (uri, values) in all_engs.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        engURI = URIRef(n + "ENGINE_" + uriSplit.replace("&","AND"))
        if engURI not in engines:
            engines.add(engURI)
            g.add((engURI, RDF.type, OWL.NamedIndividual))
            g.add((engURI, RDF.type, n.Engine))
            g.add((engURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((engURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            for plat in values["platforms"]:
                if plat.strip() != "":
                    platURI = plat
                    if "http://dbpedia.org/" in plat:
                        platSplit = plat.split("http://dbpedia.org/resource/")[-1]
                        platSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', platSplit)
                        platURI = URIRef(n + "DEVICE_" + platSplit.replace("&","AND"))
                    else:
                        plat = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', plat)
                        platURI = URIRef(n + "DEVICE_" + plat.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if platURI in deviceSet:
                        g.add((engURI, n.engineMadeFor, platURI))
                        g.add((platURI, n.deviceForEngine, engURI))
            for dev in values["devs"]:
                if dev.strip() != "":
                    devURI = dev
                    if "http://dbpedia.org/" in dev:
                        devSplit = dev.split("http://dbpedia.org/resource/")[-1]
                        devSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', devSplit)
                        devURI = URIRef(n + "DEVELOPER_" + devSplit.replace("&","AND"))
                    else:
                        dev = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', dev)
                        devURI = URIRef(n + "DEVELOPER_" + dev.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if devURI in devs:
                        g.add((engURI, n.engineDevelopedBy, devURI))
                        g.add((devURI, n.developedEngine, engURI))
                        
for (uri, values) in all_engs.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        engURI = URIRef(n + "ENGINE_" + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if engURI not in engines:
            engines.add(engURI)
            g.add((engURI, RDF.type, OWL.NamedIndividual))
            g.add((engURI, RDF.type, n.Engine))
            g.add((engURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((engURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            for plat in values["platforms"]:
                if plat.strip() != "":
                    platURI = plat
                    if "http://dbpedia.org/" in plat:
                        platSplit = plat.split("http://dbpedia.org/resource/")[-1]
                        platSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', platSplit)
                        platURI = URIRef(n + "DEVICE_" + platSplit.replace("&","AND"))
                    else:
                        plat = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', plat)
                        platURI = URIRef(n + "DEVICE_" + plat.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if platURI in deviceSet:
                        g.add((engURI, n.engineMadeFor, platURI))
                        g.add((platURI, n.deviceForEngine, engURI))
            for dev in values["devs"]:
                if dev.strip() != "":
                    devURI = dev
                    if "http://dbpedia.org/" in dev:
                        devSplit = dev.split("http://dbpedia.org/resource/")[-1]
                        devSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', devSplit)
                        devURI = URIRef(n + "DEVELOPER_" + devSplit.replace("&","AND"))
                    else:
                        dev = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', dev)
                        devURI = URIRef(n + "DEVELOPER_" + dev.replace(" ", "_").replace('"', '').replace("&","AND"))
                    if devURI in devs:
                        g.add((engURI, n.engineDevelopedBy, devURI))
                        g.add((devURI, n.developedEngine, engURI))

all_engs = None
g.serialize(destination="turtle/videogame_dbpedia_engines.ttl", format="turtle")
g.close()
######## SERIES ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_series = json.load(fSeries)
fSeries.close()

for (uri, values) in all_series.items():
    if "http://dbpedia.org/" in uri:
        uriSplit = uri.split("http://dbpedia.org/resource/")[-1]
        uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
        serURI = URIRef(n + "SERIES_" + uriSplit.replace("&","AND"))
        if serURI not in series:
            series.add(serURI)
            g.add((serURI, RDF.type, OWL.NamedIndividual))
            g.add((serURI, RDF.type, n.Series))
            g.add((serURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((serURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((serURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
                
for (uri, values) in all_series.items():
    if "http://dbpedia.org/" not in uri:
        uri = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uri)
        serURI = URIRef(n + "SERIES_" + uri.replace(" ", "_").replace('"', '').replace("&","AND"))
        if serURI not in series:
            series.add(serURI)
            g.add((serURI, RDF.type, OWL.NamedIndividual))
            g.add((serURI, RDF.type, n.Series))
            g.add((serURI, n.Name, Literal(joined_list(values["name"]))))
            g.add((serURI, n.Abstract, Literal(joined_list(values["abstract"]))))
            if not is_list_empty(values["debutDate"]):
                g.add((serURI, n.Release_Date, Literal(joined_list(values["debutDate"]))))
                
all_series = None
g.serialize(destination="turtle/videogame_dbpedia_series.ttl", format="turtle")
g.close()
######## GAMES ########
g = Graph()
g.parse("turtle/videgame_base.ttl")

g.bind("\n", n)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

all_games = json.load(fGames)
fGames.close()
fgURIs = open("data-dbpedia/uri_label_dates_dbpedia/games_uris_dbpedia.json", "r", encoding='utf-8')
all_games_labels = json.load(fgURIs)["games"]
fgURIs.close()

for game_dict in all_games["games"]:
    uriSplit = game_dict["uri"].split("http://dbpedia.org/resource/")[-1]
    uriSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', uriSplit)
    gURI = URIRef(n + "GAME_" + uriSplit.replace("&","AND"))
    g.add((gURI, RDF.type, OWL.NamedIndividual))
    g.add((gURI, RDF.type, n.Game))
    g.add((gURI, n.Name, Literal(all_games_labels[game_dict["uri"]][0])))
    if not is_list_empty([all_games_labels[game_dict["uri"]][1].strip()]):
        aux = joined_list([all_games_labels[game_dict["uri"]][1].strip()])
        check = isDateable(aux)
        if check == True:
            g.add((gURI, n.Release_Date, Literal(aux)))
        elif check == False:
            pass
        else:
            g.add((gURI, n.Release_Date, Literal(check + " ; " + aux)))
    if not is_list_empty(game_dict["abstract"]):
        g.add((gURI, n.Abstract, Literal(joined_list(game_dict["abstract"]))))
    if not is_list_empty(game_dict["metacritic"]):
        g.add((gURI, n.Metacritic, Literal(joined_list(game_dict["metacritic"]))))
    if not is_list_empty(game_dict["series"]):
        for ser in game_dict["series"]:
            if ser.strip() != "":
                serURI = ser
                if "http://dbpedia.org/" in ser:
                    serSplit = ser.split("http://dbpedia.org/resource/")[-1]
                    serSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', serSplit)
                    serURI = URIRef(n + "SERIES_" + serSplit.replace("&","AND"))
                else:
                    ser = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', ser)
                    serURI = URIRef(n + "SERIES_" + ser.replace(" ", "_").replace('"', '').replace("&","AND"))
                if serURI in series:
                    g.add((gURI, n.partOf, serURI))
                    g.add((serURI, n.includes, gURI))
    if not is_list_empty(game_dict["devs"]):
        for dev in game_dict["devs"]:
            if dev.strip() != "":
                devURI = dev
                if "http://dbpedia.org/" in dev:
                    devSplit = dev.split("http://dbpedia.org/resource/")[-1]
                    devSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', devSplit)
                    devURI = URIRef(n + "DEVELOPER_" + devSplit.replace("&","AND"))
                else:
                    dev = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', dev)
                    devURI = URIRef(n + "DEVELOPER_" + dev.replace(" ", "_").replace('"', '').replace("&","AND"))
                if devURI in devs:
                    g.add((gURI, n.developedBy, devURI))
                    g.add((devURI, n.hasDeveloped, gURI))
    if not is_list_empty(game_dict["engine"]):
        for eng in game_dict["engine"]:
            if eng.strip() != "":
                engURI = eng
                if "http://dbpedia.org/" in eng:
                    engSplit = eng.split("http://dbpedia.org/resource/")[-1]
                    engSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', engSplit)
                    engURI = URIRef(n + "ENGINE_" + engSplit.replace("&","AND"))
                else:
                    eng = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', eng)
                    engURI = URIRef(n + "ENGINE_" + eng.replace(" ", "_").replace('"', '').replace("&","AND"))
                if engURI in engines:
                    g.add((gURI, n.builtOn, engURI))
                    g.add((engURI, n.engineFor, gURI))
    if not is_list_empty(game_dict["genre"]):
        for gen in game_dict["genre"]:
            if gen.strip() != "":
                genURI = gen
                if "http://dbpedia.org/" in gen:
                    genSplit = gen.split("http://dbpedia.org/resource/")[-1]
                    genSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', genSplit)
                    genURI = URIRef(n + "GENRE_" + genSplit.replace("&","AND"))
                else:
                    gen = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', gen)
                    genURI = URIRef(n + "GENRE_" + gen.replace(" ", "_").replace('"', '').replace("&","AND"))
                if genURI in genreSet:
                    g.add((gURI, n.hasGenre, genURI))
                    g.add((genURI, n.appliesTo, gURI))
    if not is_list_empty(game_dict["publisher"]):
        for dev in game_dict["publisher"]:
            if dev.strip() != "":
                devURI = dev
                if "http://dbpedia.org/" in dev:
                    devSplit = dev.split("http://dbpedia.org/resource/")[-1]
                    devSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', devSplit)
                    devURI = URIRef(n + "DEVELOPER_" + devSplit.replace("&","AND"))
                else:
                    dev = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', dev)
                    devURI = URIRef(n + "DEVELOPER_" + dev.replace(" ", "_").replace('"', '').replace("&","AND"))
                if devURI in devs:
                    g.add((gURI, n.developedBy, devURI))
                    g.add((devURI, n.hasDeveloped, gURI))
    if not is_list_empty(game_dict["platforms"]):
        for plat in game_dict["platforms"]:
            if plat.strip() != "":
                platURI = plat
                if "http://dbpedia.org/" in plat:
                    platSplit = plat.split("http://dbpedia.org/resource/")[-1]
                    platSplit = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', platSplit)
                    platURI = URIRef(n + "DEVICE_" + platSplit.replace("&","AND"))
                else:
                    plat = re.sub(r'(\n|\r|\[|\]|\:|\.|\,|\;|\'|\?|\!|\\|\/|\#|\(|\))', r'', plat)
                    platURI = URIRef(n + "DEVICE_" + plat.replace(" ", "_").replace('"', '').replace("&","AND"))
                if platURI in deviceSet:
                    g.add((gURI, n.availableOn, platURI))
                    g.add((platURI, n.hosts, gURI))

all_games = None
all_games_labels = None
g.serialize(destination="turtle/videogame_dbpedia_games.ttl", format="turtle")
g.close()