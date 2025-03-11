# Jogo Quiz - História de Portugal

## Descrição
Este projeto consiste num jogo de quiz desenvolvido em Flask que testa o conhecimento dos jogadores sobre a história de Portugal. O jogo consulta uma base de dados em GraphDB para formular perguntas sobre reis, batalhas, dinastias e conquistas históricas portuguesas.

## Funcionalidades

- **Perguntas Diversificadas:** O jogo gera vários tipos de perguntas:
  - Identificação do ano em que ocorreu uma batalha
  - Associação de reis às suas dinastias
  - Verificação de datas de conquistas históricas
  - Associação de reis aos seus cognomes
  - Identificação de reis pelos seus cognomes conhecidos
  - Datas de conquistas importantes

- **Sistema de Pontuação:** O jogo mantém uma contagem da pontuação do jogador através de sessões.

- **Interface Web:** Implementada com Flask, fornecendo uma experiência intuitiva de quiz.

- **Integração com GraphDB:** Consulta em tempo real uma base de dados de conhecimento sobre a história de Portugal.

## Requisitos

- Python 3.7+
- Flask
- Requests
- GraphDB com o repositório "Historia_Portugal" configurado