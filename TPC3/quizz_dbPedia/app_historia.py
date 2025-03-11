from flask import Flask, render_template, request, session, redirect, url_for
from flask_cors import CORS
import random
import requests
import re
import logging
from functools import lru_cache
from dataclasses import dataclass
from typing import List, Dict, Any, Callable, Optional, Union
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'História de Portugal')
CORS(app)

GRAPHDB_ENDPOINT = os.environ.get('GRAPHDB_ENDPOINT', "http://localhost:7200/repositories/Historia_Portugal")

@dataclass
class King:
    nome: str
    dataNasc: str
    
@dataclass
class Battle:
    batalha: str
    data: str
    
@dataclass
class Dynasty:
    rei: str
    dinastia: str
    
@dataclass
class Conquest:
    conquista: str
    data: str
    
@dataclass
class KingCognome:
    nome: str
    cognome: str
    
@dataclass
class Question:
    question: str
    options: List[Any]
    answer: Any

@lru_cache(maxsize=32)
def query_graphdb(endpoint_url: str, sparql_query: str) -> Dict[str, Any]:
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(endpoint_url, params={'query': sparql_query}, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"GraphDB query failed: {e}")
        raise Exception(f"Error querying GraphDB: {e}")

KINGS_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?n ?o
    WHERE {
        ?s a :Rei.
        ?s :nome ?n .
        ?s :nascimento ?o.
    }
"""

BATTLES_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nomebatalha ?data
    WHERE {
        ?batalha a :Batalha.
        ?batalha :data ?data.
        ?batalha :nome ?nomebatalha .
    }
"""

DYNASTY_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nomerei ?nomedinastia
    WHERE {
        ?reinado a :Reinado.
        ?reinado :temMonarca ?rei .
        ?rei :nome ?nomerei.
        ?reinado :dinastia ?dinastia.
        ?dinastia :nome ?nomedinastia.
    }
"""

CONQUEST_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome ?data
    WHERE {
        ?conquista a :Conquista.
        ?conquista :nome ?nome.
        ?conquista :data ?data .
    }
"""

KING_COGNOME_QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
SELECT ?nome ?cognomes
    WHERE {
        ?rei a :Rei.
        ?rei :nome ?nome.
        ?rei :cognomes ?cognomes .
    }
"""

def parse_kings() -> List[King]:
    result = query_graphdb(GRAPHDB_ENDPOINT, KINGS_QUERY)
    return [
        King(
            nome=r['n']['value'].split('#')[-1],
            dataNasc=r['o']['value'].split('#')[-1]
        )
        for r in result['results']['bindings']
    ]

def parse_battles() -> List[Battle]:
    result = query_graphdb(GRAPHDB_ENDPOINT, BATTLES_QUERY)
    return [
        Battle(
            batalha=r['nomebatalha']['value'].split('#')[-1],
            data=re.search(r"\d{4}$", r['data']['value'].split('#')[-1]).group(0) if re.search(r"\d{4}$", r['data']['value'].split('#')[-1]) else None
        )
        for r in result['results']['bindings']
    ]

def parse_dynasties() -> List[Dynasty]:
    result = query_graphdb(GRAPHDB_ENDPOINT, DYNASTY_QUERY)
    return [
        Dynasty(
            rei=r['nomerei']['value'].split('#')[-1],
            dinastia=r['nomedinastia']['value'].split('#')[-1]
        )
        for r in result['results']['bindings']
    ]

def parse_conquests() -> List[Conquest]:
    result = query_graphdb(GRAPHDB_ENDPOINT, CONQUEST_QUERY)
    return [
        Conquest(
            conquista=r['nome']['value'].split('#')[-1],
            data=r['data']['value'].split('#')[-1]
        )
        for r in result['results']['bindings']
    ]

def parse_king_cognomes() -> List[KingCognome]:
    result = query_graphdb(GRAPHDB_ENDPOINT, KING_COGNOME_QUERY)
    return [
        KingCognome(
            nome=r['nome']['value'].split('#')[-1],
            cognome=r['cognomes']['value'].split('#')[-1]
        )
        for r in result['results']['bindings']
    ]

def generate_battle_year_question() -> Question:
    """Generate a question about the year of a battle."""
    batalhas = random.choices(parse_battles(), k=4)
    batalhaSel = batalhas[random.randrange(0, 4)]
    
    options = list({b.data for b in batalhas if b.data})
    while len(options) < 4:
        options.append(str(random.randint(1000, 1500)))
        options = list(set(options))
        
    return Question(
        question=f"Em que ano é que ocorreu a batalha {batalhaSel.batalha}?",
        options=random.sample(options, 4),
        answer=batalhaSel.data
    )

def generate_king_dynasty_question() -> Question:
    """Generate a question about a king's dynasty."""
    dinastia_rei_list = parse_dynasties()
    dinastia = random.choice(dinastia_rei_list)
    diff_dinastias = list({entrada.dinastia for entrada in dinastia_rei_list})
    
    options = random.sample([d for d in diff_dinastias if d != dinastia.dinastia], min(3, len(diff_dinastias) - 1))
    options.append(dinastia.dinastia)
    random.shuffle(options)
    
    return Question(
        question=f"A que dinastia pertence o rei {dinastia.rei}?",
        options=options,
        answer=dinastia.dinastia
    )

def generate_conquest_date_question() -> Question:
    """Generate a true/false question about conquest dates."""
    conquistas = random.choices(parse_conquests(), k=2)
    answer = random.choice([True, False])
    
    indexConquista = 0 if answer else 1
        
    return Question(
        question=f"A conquista {conquistas[0].conquista} ocorreu em {conquistas[indexConquista].data}?",
        options=[True, False],
        answer=answer
    )

def generate_king_cognome_question() -> Question:
    """Generate a true/false question about king's cognomes."""
    reis = random.choices(parse_king_cognomes(), k=3)
    answer = random.choice([True, False])
    
    indexConquista = 0 if answer else 1
        
    return Question(
        question=f"O rei {reis[0].nome} é conhecido como {reis[indexConquista].cognome}?",
        options=[True, False],
        answer=answer
    )

def generate_cognome_king_question() -> Question:
    """Generate a question about identifying a king by their cognome."""
    cognomes = random.choices(parse_king_cognomes(), k=4)
    cognomeSel = cognomes[random.randrange(0, 4)]
    
    options = list({c.nome for c in cognomes})
    while len(options) < 4:
        extra_cognomes = random.choices(parse_king_cognomes(), k=1)
        options.append(extra_cognomes[0].nome)
        options = list(set(options))
    
    return Question(
        question=f"O rei conhecido por {cognomeSel.cognome} é o...",
        options=random.sample(options, 4),
        answer=cognomeSel.nome
    )

def generate_conquest_date_multiple_choice_question() -> Question:
    """Generate a multiple choice question about conquest dates."""
    conquistas = random.choices(parse_conquests(), k=4)
    conquistaSel = conquistas[random.randrange(0, 4)]
    
    options = list({c.data for c in conquistas if c.data})
    while len(options) < 4:
        options.append(str(random.randint(1000, 1500)))
        options = list(set(options))
    
    return Question(
        question=f"Quando ocorreu a conquista {conquistaSel.conquista}?",
        options=random.sample(options, 4),
        answer=conquistaSel.data
    )

QUESTION_GENERATORS = [
    generate_king_dynasty_question,
    generate_conquest_date_question,
    generate_king_cognome_question,
    generate_cognome_king_question,
    generate_conquest_date_multiple_choice_question,
    generate_battle_year_question
]

@app.route('/')
def home():
    session['score'] = 0
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        answer_correct = request.form.get('answerCorrect')
        
        if user_answer == 'True':
            user_answer = True
        elif user_answer == 'False':
            user_answer = False
            
        if answer_correct == 'True':
            answer_correct = True
        elif answer_correct == 'False':
            answer_correct = False
        
        correct = answer_correct == user_answer
        session['score'] = session.get('score', 0) + (1 if correct else 0)
        return render_template('result.html', correct=correct, correct_answer=answer_correct, score=session['score'])

    try:
        question_func = random.choice(QUESTION_GENERATORS)
        question = question_func()
        return render_template('quiz.html', question=question)
    except Exception as e:
        logger.error(f"Error generating question: {e}")
        return render_template('error.html', error=str(e))

@app.route('/score')
def score():
    return render_template('score.html', score=session.get('score', 0))

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))