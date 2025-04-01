# 1) Quantas classes estão definidas na Ontologia?
```bash
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select (count (DISTINCT ?s) as ?count) where {
    ?s rdf:type owl:Class
}
```
# 2) Quantas Object Properties estão definidas na Ontologia?
```bash
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select (count (DISTINCT ?s) as ?count) where {
    ?s rdf:type owl:ObjectProperty
}
```
# 3) Quantos indivíduos existem na tua ontologia?
```bash
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
select (count (DISTINCT ?s) as ?count) where {
    ?s rdf:type owl:NamedIndividual
}
```
# 4) Quem planta tomates?
```bash
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX mine:<http://www.semanticweb.org/eduardo/ontologies/2025/1/untitled-ontology-2/>
select ?o {
    mine:tomate mine:éCultivadoPor ?o
}
```
# 5) Quem contrata trabalhadores temporários?
```bash
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX mine:<http://www.semanticweb.org/eduardo/ontologies/2025/1/untitled-ontology-2/>
select ?s {
    ?s mine:usaTrabalhadorTemporário true
}
```