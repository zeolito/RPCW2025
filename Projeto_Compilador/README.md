# Projeto RPCW

## 1. Dependências

- Python 3.7+  
- Bibliotecas Python:
  - `requests`
  - `rdflib`
  - `Flask`

Instalação rápida (em ambiente virtual):
```bash
pip install requests rdflib flask
````

## 2. Configuração

* **Chave RAWG**: definir `API_KEY` em `scrapper.py`.
* **GraphDB**: configurar o endpoint SPARQL em `app.py` (por padrão `http://localhost:7200/repositories/videogames`).
* **SECRET\_KEY**: opcionalmente personalizar em `app.py` para sessões Flask.
* Pastas esperadas:

  * `archive/VideoGames/` (JSONs brutos de jogos)
  * `data-dbpedia/` (JSONs DBpedia, se usados)
  * `turtle/` (saida TTL do povoador)

## 3. Scrapper

Gera JSONs brutos de jogos via API RAWG.

```bash
# Ajuste API_KEY em scrapper.py e OUTPUT_DIR se necessário
python scrapper.py
```

Os arquivos JSON criados irão para a pasta definida em `OUTPUT_DIR` (padrão: `D:\VideoGames`).

## 4. PovoadorJSON

Transforma os JSONs brutos em instâncias RDF e gera arquivos Turtle.

```bash
# Certifique-se de que archive/VideoGames/ e data-dbpedia/ estejam preenchidos
python povoadorJSON.py
```

Saídas TTL serão colocadas em `turtle/` (ex.: `videgame_ontology0.ttl`, `videgame_ontology1.ttl`, …).

## 5. Web App (Flask + Jinja)

Exibe buscas, consultas SPARQL customizadas e modo quiz sobre a ontologia de jogos.

1. **Instalar dependências** .
2. **Ajustar** `app.py`:

   * `SPARQL_ENDPOINT` (usar URL correta do repositório GraphDB).
   * `SECRET_KEY` (string aleatória para sessões Flask).
3. **Executar**:

   ```bash
   python app.py
   ```
4. **Aceder no navegador**:

   ```
   http://localhost:5000
   ```

   - **Search**: busca rápida por jogo, gênero, plataforma ou desenvolvedor.
   - **Advanced Search**: insira SPARQL customizada (somente SELECT).
   - **Quiz Mode**: selecione número de perguntas e responda múltipla escolha.

---

### Resumo de Comandos

```bash
# 1. Obter JSONs RAWG
python scrapper.py

# 2. Gerar ontologia em Turtle
python povoadorJSON.py

# 3. Iniciar servidor Flask
python app.py
```

