import csv, json

base = """
@prefix : <http://www.example.org/disease-ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix swrl: <http://www.w3.org/2003/11/swrl#> .
@prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .

<http://www.example.org/disease-ontology> rdf:type owl:Ontology .

# Classes
:Disease a owl:Class .
:Symptom a owl:Class .
:Treatment a owl:Class .
:Patient a owl:Class .

# Properties
:hasSymptom a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range :Symptom .

:hasDescription a owl:DatatypeProperty ;
    rdfs:domain :Disease ;
    rdfs:range xsd:string .

:hasTreatment a owl:ObjectProperty ;
    rdfs:domain :Disease ;
    rdfs:range :Treatment .

:exhibitsSymptom a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Symptom .

:hasDisease a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Disease .

:receivesTreatment a owl:ObjectProperty ;
    rdfs:domain :Patient ;
    rdfs:range :Treatment .


"""

def parse_disease_descriptions(filename):
    disease_descriptions = {}

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        
        # Read the header if present (assumes first row is a header)
        header = next(reader, None)
        if header is None:
            print("CSV file is empty.")
            return {}
        
        # Process each row in the CSV file.
        for row in reader:
            # Expecting two columns: disease and description
            if len(row) < 2:
                continue  # Skip rows that don't have enough columns
            
            # Extract disease name and description (description)
            disease = row[0].strip().replace(" ","_").replace("__","_").replace("(","").replace(")","").lower()
            description = row[1].strip().replace('"','')
            
            # Create or update the disease entry with the description
            if disease not in disease_descriptions:
                disease_descriptions[disease] = {
                    "description": set(),
                    "symptoms": set(),
                    "treatments": set()
                }
            # Add description to the description set
            disease_descriptions[disease]["description"].add(description)
    
    return disease_descriptions

def parse_disease_extra(filename,dictionary,field):
    return_dict = set()
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        
        # Read the header if present (assumes first row is a header)
        header = next(reader, None)
        if header is None:
            print("CSV file is empty.")
            return {}
        
        # Process each row in the CSV file.

        for row in reader:
            # Expecting two columns: disease and description
            if len(row) < 2:
                continue  # Skip rows that don't have enough columns
            
            # Extract disease name and description (description)
            disease = row[0].strip().replace(" ","_").replace("__","_").replace("(","").replace(")","").lower()
            for element in row[1:]:
                synptom = element.strip().replace(" ","_").replace("__","_").replace("(","").replace(")","").lower()
                if disease in dictionary and len(synptom) > 0:
                    dictionary[disease][field].add(synptom)
                    return_dict.add(synptom)

    return return_dict

def process_patient_data(json_file_path, symptoms_set):
    # Read data from JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    
    # Process the data into the required dictionary
    patient_symptoms = {}
    for patient in json_data:
        name = patient["nome"].strip()
        symptoms_old = patient["sintomas"]
        symptoms = []
        for elem in symptoms_old:
            sym = elem.strip().replace(" ","_").replace("__","_").replace("(","").replace(")","").lower()
            if sym in symptoms_set:
                symptoms.append(sym)

        patient_symptoms[name] = symptoms
    
    return patient_symptoms

def createTurtle1(filename, dictionary,alt_set):
    full_filename = f"ex2/{filename}.ttl"

    with open(full_filename, 'w') as file:
        file.write(base)
        
        for disease in dictionary.keys():
            name = ":" + disease + """ a :Disease ;
            :hasSymptom :"""
            for symptom in dictionary[disease]["symptoms"]:
                name = name + symptom + ", :"
            name = name[:-3]+" ; \n            :hasDescription \""
            for symptom in dictionary[disease]["description"]:
                name = name + symptom
            file.write(name+"\" .\n\n")

        file.write("\n\n")

        for elem in alt_set:
            file.write(":" + elem + " a :Symptom .\n")

def createTurtle2(filename, dictionary,alt_set1,alt_set2):
    full_filename = f"ex2/{filename}.ttl"

    with open(full_filename, 'w') as file:
        file.write(base)
        
        for disease in dictionary.keys():
            name = ":" + disease + """ a :Disease ;
            :hasSymptom :"""
            for symptom in dictionary[disease]["symptoms"]:
                name = name + symptom + ", :"
            name = name[:-3]+" ; \n            :hasDescription \""
            for symptom in dictionary[disease]["description"]:
                name = name + symptom
            name = name+"\" ; \n            :hasTreatment :"
            for symptom in dictionary[disease]["treatments"]:
                name = name + symptom + ", :"
            file.write(name[:-3]+" .\n\n")

        file.write("\n\n")

        for elem in alt_set1:
            file.write(":" + elem + " a :Symptom .\n")

        file.write("\n\n")

        for elem in alt_set2:
            file.write(":" + elem + " a :Treatment .\n")

def createTurtle3(filename, dictionary,alt_set1,alt_set2,dictionary2):
    full_filename = f"ex2/{filename}.ttl"

    with open(full_filename, 'w', encoding='utf-8') as file:
        file.write(base)
        
        for disease in dictionary.keys():
            name = ":" + disease + """ a :Disease ;
            :hasSymptom :"""
        
            for symptom in dictionary[disease]["symptoms"]:
                name = name + symptom + ", :"
            name = name[:-3]+" ; \n            :hasDescription \""
            for symptom in dictionary[disease]["description"]:
                name = name + symptom
            name = name+"\" ; \n            :hasTreatment :"
            for symptom in dictionary[disease]["treatments"]:
                name = name + symptom + ", :"
            file.write(name[:-3]+" .\n\n")

        file.write("\n\n")

        for elem in alt_set1:
            file.write(":" + elem + " a :Symptom .\n")

        file.write("\n\n")

        for elem in alt_set2:
            file.write(":" + elem + " a :Treatment .\n")

        file.write("\n\n")

        id = 1
        for patient in dictionary2.keys():
            line = ":Patient" + str(id) + """ a :Patient ;\n    :name \"""" + patient + "\" ;\n"

            for symp in dictionary2[patient]:
                line = line + "    :exhibitsSymptom :" + symp + " ;\n"

            
            id +=1
            file.write(line[:-3] + " .\n\n")

def main():
    disease_data = parse_disease_descriptions('Disease_Description.csv')
    unique_symptoms = parse_disease_extra('Disease_Syntoms.csv',disease_data,"symptoms")
    unique_treatments = parse_disease_extra('Disease_Treatment.csv',disease_data,"treatments")
    patient_data = process_patient_data('doentes.json',unique_symptoms)

    createTurtle1("med_doencas", disease_data, unique_symptoms)
    createTurtle2("med_tratamentos", disease_data,unique_symptoms, unique_treatments)
    createTurtle3("med_doentes", disease_data,unique_symptoms, unique_treatments, patient_data)
        
if __name__ == "__main__":
    main()
