import json
import os

modal=set()

def create_ttl_content(json_data):
    ttl_content = ""
    
    base_uri = "http://rpcw.di.uminho.pt/pedro/2025/tpc1"
    
    for person in json_data:
        first_name = person["nome"]["primeiro"]
        last_name = person["nome"]["último"]
        person_id = f"{first_name}_{last_name[0]}"
        
        # Person
        ttl_content += f"\n###  {base_uri}#{person_id}\n"
        ttl_content += f":{person_id} rdf:type owl:NamedIndividual ,\n"
        ttl_content += "                  :Pessoa ;\n"
        ttl_content += f"         :fez_exame :Exame_{person['index']} ;\n"
        ttl_content += f"         :pratica_modal :{person['modalidade']} ;\n"
        ttl_content += f"         :clube \"{person['clube']}\" ;\n"
        ttl_content += f"         :email \"{person['email']}\" ;\n"
        ttl_content += f"         :federado \"{str(person['federado']).lower()}\"^^xsd:boolean ;\n"
        ttl_content += f"         :idade {person['idade']} ;\n"
        ttl_content += f"         :nome \"{first_name} {last_name}\" .\n\n"
        
        # Exam
        ttl_content += f"\n###  {base_uri}#Exame_{person['index']}\n"
        ttl_content += f":Exame_{person['index']} rdf:type owl:NamedIndividual ,\n"
        ttl_content += "                  :Exame ;\n"
        ttl_content += f"         :data \"{person['dataEMD']}\" ;\n"
        ttl_content += f"         :resultado \"{str(person['resultado']).lower()}\"^^xsd:boolean .\n\n"

        # Modal
        if person['modalidade'] not in modal:
            modal.add(person['modalidade'])
            
            ttl_content += f"\n###  {base_uri}#Exame_{person['modalidade']}\n"
            ttl_content += f":{person['modalidade']} rdf:type owl:NamedIndividual ,\n"
            ttl_content += "                  :Modal .\n"
    
    return ttl_content

def convert_json_to_ttl(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        ttl_content = """@prefix : <http://rpcw.di.uminho.pt/pedro/2025/tpc1#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://rpcw.di.uminho.pt/pedro/2025/tpc1/> .


<http://rpcw.di.uminho.pt/pedro/2025/tpc1> rdf:type owl:Ontology .

#################################################################
#    Object Properties
#################################################################

###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#fez_exame
:fez_exame rdf:type owl:ObjectProperty ;
           rdfs:domain :Pessoa ;
           rdfs:range :Exame .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#pratica_modal
:pratica_modal rdf:type owl:ObjectProperty ;
               rdfs:domain :Pessoa ;
               rdfs:range :Modal .


#################################################################
#    Data properties
#################################################################

###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#clube
:clube rdf:type owl:DatatypeProperty ;
       rdfs:domain :Pessoa ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#data
:data rdf:type owl:DatatypeProperty ;
      rdfs:domain :Exame ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#email
:email rdf:type owl:DatatypeProperty ;
       rdfs:domain :Pessoa ;
       rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#federado
:federado rdf:type owl:DatatypeProperty ;
          rdfs:domain :Pessoa ;
          rdfs:range xsd:boolean .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#idade
:idade rdf:type owl:DatatypeProperty ;
       rdfs:domain :Pessoa ;
       rdfs:range xsd:short .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#nome
:nome rdf:type owl:DatatypeProperty ;
      rdfs:domain :Pessoa ;
      rdfs:range xsd:string .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1#resultado
:resultado rdf:type owl:DatatypeProperty ;
           rdfs:domain :Exame ;
           rdfs:range xsd:boolean .


#################################################################
#    Classes
#################################################################

###  http://rpcw.di.uminho.pt/pedro/2025/tpc1/Exame
:Exame rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1/Modal
:Modal rdf:type owl:Class .


###  http://rpcw.di.uminho.pt/pedro/2025/tpc1/Pessoa
:Pessoa rdf:type owl:Class .


#################################################################
#    Individuals
#################################################################
"""
        ttl_content += create_ttl_content(json_data)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(ttl_content)
            
        print(f"Successfully converted {input_file} to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "med.json")
    output_file = os.path.join(script_dir, "Final.ttl")

    convert_json_to_ttl(input_file, output_file)


