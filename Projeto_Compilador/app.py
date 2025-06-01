# app.py
from flask import Flask, render_template, request, jsonify
import requests
import json
from urllib.parse import quote, unquote
import logging
import re
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

MAXINT = 1000

SPARQL_ENDPOINT = "http://localhost:7200/repositories/videogames"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphDBClient:
    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
        self.headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query'
        }
    
    def execute_query(self, sparql_query):
        """Execute SPARQL query against GraphDB"""
        try:
            
            response = requests.post(
                self.endpoint_url,
                data=sparql_query,
                headers=self.headers,
                timeout=2000
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"GraphDB error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None

# Initialize GraphDB client
graphdb_client = GraphDBClient(SPARQL_ENDPOINT)

def build_search_query(query_text, category=None, sort_by='name'):
    """Build SPARQL query based on search parameters"""
    
    # Base prefixes - adjust these to match your ontology
    prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX vg: <http://rpcw.di.uminho.pt/2025/videogames#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dct: <http://purl.org/dc/terms/>
    """
    
    # Build WHERE clause based on category
    if category == 'game':
        where_clause = f"""
        WHERE {{
            ?item a vg:Game .
            ?item vg:Name ?title .
            BIND("Game" as ?type)
            OPTIONAL {{ ?item vg:Release_Date ?year . }}
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
        }}
        """
    elif category == 'genre':
        where_clause = f"""
        WHERE {{
            ?item a vg:Genre .
            ?item vg:Name ?title .
            BIND("Genre" as ?type)
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
        }}
        """
    elif category == 'platform':
        where_clause = f"""
        WHERE {{
            ?item a vg:Device .
            ?item vg:Name ?title .
            BIND("Platform" as ?type)
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
        }}
        """
    elif category == 'developer':
        where_clause = f"""
        WHERE {{
            ?item a vg:Developer .
            ?item vg:Name ?title .
            BIND("Developer" as ?type)
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
        }}
        """
    elif category == 'series':
        where_clause = f"""
        WHERE {{
            ?item a vg:Series .
            ?item vg:Name ?title .
            BIND("Series" as ?type)
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
        }}
        """
    elif category == 'gengine':
        where_clause = f"""
        WHERE {{
            ?item a vg:Engine .
            ?item vg:Name ?title .
            BIND("Game Engine" as ?type)
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
        }}
        """
    else:  # General search across all types
        where_clause = f"""
        WHERE {{
            ?item a ?type .
            ?item vg:Name ?title .
            OPTIONAL {{ ?item vg:Release_Date ?year . }}
            
            FILTER(CONTAINS(LCASE(?title), LCASE("{query_text}")))
            FILTER( ?type != owl:NamedIndividual)
        }}
        """
    
    # Build ORDER BY clause
    order_clause = ""
    if sort_by == 'name':
        order_clause = "ORDER BY ?title"
    elif sort_by == 'year':
        order_clause = "ORDER BY DESC(?year)"
    elif sort_by == 'old':
        order_clause = "ORDER BY (?year)"
    
    # Combine the query
    sparql_query = f"""
    {prefixes}
    SELECT DISTINCT ?item ?title ?type ?year
    {where_clause}
    {order_clause}

    """
    
    return sparql_query

def validate_sparql_query(query):
    """Basic SPARQL query validation"""
    # Check for dangerous operations
    dangerous_patterns = [
        r'\bDROP\b', r'\bDELETE\b', r'\bCLEAR\b',
        r'\bCREATE\b', r'\bALTER\b', r'\bUPDATE\b'
    ]
    
    query_upper = query.upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_upper):
            return False, f"Query contains potentially dangerous operation: {pattern}"
    
    # Check for SELECT statement
    if not re.search(r'\bSELECT\b', query_upper):
        return False, "Query must contain a SELECT statement"
    
    return True, "Valid query"

def format_custom_sparql_results(sparql_results):
    """Format custom SPARQL query results for table display"""
    if not sparql_results or 'results' not in sparql_results:
        return {'headers': [], 'rows': []}

    bindings = sparql_results['results']['bindings']
    if not bindings:
        return {'headers': [], 'rows': []}
    
    # Get headers from the first result
    headers = list(bindings[0].keys())
    forbid = ["Game","Genre","Platform","Developer","Device","Series","Engine"]

    # Format each row
    rows = []
    for binding in bindings:
        row = {}
        for header in headers:
            if header in binding:
                entity_uri = ""
                value = binding[header]['value']
                flag = False
                if (binding[header]['type'] == 'uri') and ("#" in value):
                        sub = value.split("#")
                        if (("w3" or "owl") not in sub[0]) and sub[1] not in forbid:
                            flag = True
                            entity_uri = sub[1]
                row[header] = (value, flag, "entity/" + entity_uri)
            else:
                row[header] = ''
        rows.append(row)
    
    return {'headers': headers, 'rows': rows}

def format_search_results(sparql_results):
    """Convert SPARQL results to frontend format"""
    if not sparql_results or 'results' not in sparql_results:
        return []
    
    formatted_results = []
    
    for binding in sparql_results['results']['bindings']:
        
        type_str = binding.get('type', {}).get('value', 'Game')
        if "#" in type_str:
            type_str = type_str.split("#")[1]
         
        result = {
            'title': binding.get('title', {}).get('value', 'Unknown'),
            'type': type_str,
            'uri': "entity/" + binding.get('item', {}).get('value', '').split('#')[1]
        }
        
        # Add optional fields if they exist
        
        if 'year' in binding:
            result['year'] = binding['year']['value']
        
        formatted_results.append(result)
    
    return formatted_results

@app.route('/')
def index():
    """Render the main page"""
    return render_template('jinja_template.html')

def get_entity_details(entity_id):
    query = f"""
        PREFIX : <http://rpcw.di.uminho.pt/2025/videogames#>
        
        SELECT distinct ?name ?p ?o ?names WHERE {{
            :{entity_id} ?p ?o .
            OPTIONAL {{ :{entity_id} :Name ?name . }}
            OPTIONAL {{ ?o :Name ?names . }}
            FILTER( ?p != owl:topObjectProperty)
        }}
    """
    params = []
    sparql_results = graphdb_client.execute_query(query)
    link = False

    for value in sparql_results['results']['bindings']:
        if value['name']:
            name = value['name']['value']
        else:
            name = entity_id

        link_value =  ""

        if "names" in value and value["names"]:
            title = value["names"]["value"]
            if value["o"]["type"] == "uri":
                link = True
                link_value += value["o"]["value"].split("#")[1]
        else:
            o_value = value.get("o", {}).get("value", "")
            if "#" in o_value:
                title = o_value.split("#")[1]
            else:
                title = o_value



        params.append({
            'value': value["p"]["value"].split("#")[1],
            'display': title,
            'is_link': link,
            'entity_id': link_value
        })

    return {"title" : name,
        'params': params
        }


@app.route('/entity/<entity_id>')
def entity_detail(entity_id):
    """Display detailed information about a specific entity"""
    try:
        # Decode the entity_id in case it's URL encoded
        entity_id = unquote(entity_id)
        
        # Get entity details from SPARQL
        entity_data = get_entity_details(entity_id)
        
        if not entity_data:
            return render_template('entity_detail.html', 
                                   error=f"Entity '{entity_id}' not found"), 404
        
        return render_template('entity_detail.html', entity=entity_data)
        
    except Exception as e:
        logger.error(f"Entity detail error: {e}")
        return render_template('entity_detail.html', 
                               error=f"Error loading entity details: {str(e)}"), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search requests"""
    try:
        data = request.get_json()
        query_text = data.get('query', '').strip()
        category = data.get('category', '')
        sort_by = data.get('sort', 'relevance')
        
        if not query_text:
            return jsonify({'error': 'Query text is required'}), 400
        
        # Build and execute SPARQL query
        sparql_query = build_search_query(query_text, category, sort_by)
        sparql_results = graphdb_client.execute_query(sparql_query)
        
        if sparql_results is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        # Format results for frontend
        formatted_results = format_search_results(sparql_results)
        
        return jsonify({
            'results': formatted_results,
            'total': len(formatted_results),
            'query': query_text
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sparql-query', methods=['POST'])
def execute_custom_sparql():
    """Handle custom SPARQL query requests"""
    try:
        data = request.get_json()
        sparql_query = data.get('query', '').strip()
        
        if not sparql_query:
            return jsonify({'error': 'SPARQL query is required'}), 400
        
        # Validate the query
        is_valid, message = validate_sparql_query(sparql_query)
        if not is_valid:
            return jsonify({'error': f'Invalid query: {message}'}), 400
        
        # Execute the query
        sparql_results = graphdb_client.execute_query(sparql_query)
        
        if sparql_results is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        # Format results for table display
        formatted_results = format_custom_sparql_results(sparql_results)
        
        return jsonify({
            'results': formatted_results,
            'total': len(formatted_results['rows']) if formatted_results['rows'] else 0
        })
        
    except Exception as e:
        logger.error(f"Custom SPARQL error: {e}")
        return jsonify({'error': f'Query execution error: {str(e)}'}), 500

@app.route('/api/quiz-questions')
def get_quiz_questions():
    """Get quiz questions from the ontology"""
    try:
        # Get the number of questions from query parameter, default to 5
        num_questions = request.args.get('count', default=5, type=int)
        
        # Validate the count (minimum 1, maximum 20 for reasonable limits)
        num_questions = max(1, min(num_questions, 20))
        
        questions = []

        if num_questions <= 3:
            questions += random_data_question(1)
            questions += random_platform_question(1)
            questions += random_genre_question(1)
        else:
            amnts = random_int_list(num_questions, 4)

            questions += random_data_question(amnts[0])
            questions += random_platform_question(amnts[1])
            questions += random_genre_question(amnts[2])
            questions += random_genre2_question(amnts[3])

        random.shuffle(questions)

        return jsonify({'questions': questions})
        
    except Exception as e:
        logger.error(f"Quiz questions error: {e}")
        return jsonify({'error': 'Failed to load quiz questions'}), 500

def random_int_list(total, length):
    """
    Return a list of `length` non-negative integers whose sum == `total`.
    The distribution is uniform over all such lists.
    """
    # pick `length-1` distinct cut points in the range (0, total)
    cuts = sorted(random.sample(range(1, total), length - 1))
    
    # prepend 0, append `total`, then take successive differences
    parts = [b - a for a, b in zip([0] + cuts, cuts + [total])]
    return parts


def random_data_question(amnt):
    sparql_query = f"""
    PREFIX vg: <http://rpcw.di.uminho.pt/2025/videogames#>

    SELECT ?nome ?year
    WHERE {{
    {{
        SELECT 
        ?game
        ?nome
        ?year
        (RAND() AS ?rnd)
        WHERE {{
        ?game       a              vg:Game ;
                    vg:Name       ?nome ;
                    vg:Release_Date ?year .

        # Exclude any game with a "nudity" genre
        FILTER NOT EXISTS {{
            ?game vg:hasGenre ?g2 .
            ?g2   vg:Name     ?name2 .
            FILTER regex(?name2, "nudity", "i")
        }}
        }}
    }}
    }}
    ORDER BY ?rnd
    LIMIT {amnt}

    """
    
    sparql_results = graphdb_client.execute_query(sparql_query)
    response = []

    for binding in sparql_results['results']['bindings']:
        
        year = int(binding['year']['value'][:4])

        options = set()
        nmbs = random.sample([-5,-4,-3,-2,-1,1,2,3,4,5],3)

        options.add(str(min(year + nmbs[0],2025)))
        options.add(str(min(year + nmbs[1],2025)))
        options.add(str(min(year + nmbs[2],2025)))
        while len(options) < 4:
            nmbs = random.sample([-5,-4,-3,-2,-1,1,2,3,4,5],4-len(options))
            for nmb in nmbs:
                options.add(str(min(year + nmb,2025)))

        options = list(options)
        random.shuffle(options)

        correct = random.randint(0, len(options))
        options.insert(correct, str(year))
        response.append({
            "question": f"On what year was \"{binding['nome']['value']}\" released?",
            "options": options,
            "correct": correct
        })

    return response

def random_platform_question(amnt):
    sparql_query = f"""
        PREFIX vg: <http://rpcw.di.uminho.pt/2025/videogames#>
            
        SELECT ?nome ?rsp
        WHERE {{
        {{
            SELECT 
            ?game 
            ?nome
            (GROUP_CONCAT(?nconsole; separator="; ") AS ?rsp) 
            (RAND()         AS ?rnd)
            WHERE {{
            ?game       a         vg:Game ;
                        vg:Name  ?nome ;
                        vg:availableOn ?console .
            ?console    vg:Name   ?nconsole .
            
            FILTER NOT EXISTS {{
                ?game vg:hasGenre ?g2 .
                ?g2   vg:Name     ?name2 .
                FILTER regex(?name2, "nudity", "i")
            }}
            }}
            GROUP BY ?game ?nome
        }}
        }}
        ORDER BY ?rnd
        LIMIT {amnt}
        """
    
    sparql_results = graphdb_client.execute_query(sparql_query)

    response = []
    for binding in sparql_results['results']['bindings']:
            
        given_platforms = binding['rsp']['value'].split("; ")
        platforms = ["PC","macOS","Linux","PlayStation 5","Xbox Series S/X","Nintendo Switch","PlayStation 4","Xbox One","iOS","Android"
                    ,"Game Boy Color","PlayStation"]

        sparql_results = graphdb_client.execute_query(sparql_query)
        options = ["Yes","No"]
        choice = random.randint(0,1)
        if choice:
            final = random.choice([x for x in platforms if x not in given_platforms])
            correct = 1
        else:
            final = random.choice(given_platforms)
            correct = 0

        response.append({
                "question": f"Is \"{binding['nome']['value']}\" available on {final}?",
                "options": options,
                "correct": correct
            })
    return response

def random_genre_question(amnt):

    if random.choice([True,False]):
        result = 0
        options = ["Singleplayer","Multiplayer"]
        first = "^single[- _]?player$"
        snd = "^multi[- _]?player$"
    else:
        result = 1
        options = ["Singleplayer","Multiplayer"]
        first = "^multi[- _]?player$"
        snd = "^single[- _]?player$"

    sparql_query = f"""
    PREFIX : <http://rpcw.di.uminho.pt/2025/videogames#>

        SELECT ?nome
        WHERE {{
        {{
            SELECT ?game ?nome (RAND() AS ?rnd)
            WHERE {{
        ?game a :Game .
        ?game :Name ?nome .
        ?game :hasGenre ?g1 .
        ?g1 :Name ?name1 .
        FILTER regex(?name1, "{first}", "i")

        FILTER NOT EXISTS {{
            ?game :hasGenre ?g2 .
            ?g2 :Name ?name2 .
            FILTER regex(?name2, "{snd}", "i")
        }}
            
        FILTER NOT EXISTS {{
            ?game :hasGenre ?g3 .
            ?g3 :Name ?name3 .
            FILTER regex(?name3, "nudity", "i")
                }}
            }}
        }}
        }}
        ORDER BY ?rnd
        LIMIT {amnt}
    """
    
    sparql_results = graphdb_client.execute_query(sparql_query)
    response = []
    for binding in sparql_results['results']['bindings']:

        response.append({
            "question": f"What is the genre of \"{binding['nome']['value']}\":",
            "options": options,
            "correct": result 
        })
    return response


def random_genre2_question(amnt):
    options = ["VR","Platformer","Firstperson"]
    regexs = ["^v[- _]?r$","^platformer$","^first[- _]?person$"]
    result = random.randint(0,len(regexs)-1)
    correct = regexs.pop(result)


    sparql_query = f"""
    PREFIX : <http://rpcw.di.uminho.pt/2025/videogames#>

        SELECT ?nome
        WHERE {{
        {{
            SELECT ?game ?nome (RAND() AS ?rnd)
            WHERE {{
        ?game a :Game .
        ?game :Name ?nome .
        ?game :hasGenre ?g1 .
        ?g1 :Name ?name1 .
        FILTER regex(?name1, "{correct}", "i")

        FILTER NOT EXISTS {{
            ?game :hasGenre ?g2 .
            ?g2 :Name ?name2 .
            FILTER regex(?name2, "{regexs[0]}", "i")
        }}

        FILTER NOT EXISTS {{
            ?game :hasGenre ?g4 .
            ?g4 :Name ?name4 .
            FILTER regex(?name4, "{regexs[1]}", "i")
        }}
            
        FILTER NOT EXISTS {{
            ?game :hasGenre ?g3 .
            ?g3 :Name ?name3 .
            FILTER regex(?name3, "nudity", "i")
                }}
            }}
        }}
        }}
        ORDER BY ?rnd
        LIMIT {amnt}
    """
    
    sparql_results = graphdb_client.execute_query(sparql_query)
    response = []
    for binding in sparql_results['results']['bindings']:

        response.append({
            "question": f"What is the genre of \"{binding['nome']['value']}\":",
            "options": options,
            "correct": result 
        })
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)