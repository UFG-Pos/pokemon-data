# Pokemon Agent API

Uma aplicação Python que integra dois MCPs da Smithery usando Docker e o agente Agnos:
- **Pokémon MCP**: para buscar informações de pokémons
- **MongoDB MCP**: para armazenar dados em uma base MongoDB

## Funcionalidades

A aplicação expõe uma API REST com as seguintes rotas:

1. `GET /api/v1/import-pokemon?name=pikachu` - Busca informações do pokémon via Pokémon MCP e salva no MongoDB
2. `GET /api/v1/pokemons` - Lista todos os pokémons registrados no banco
3. `GET /api/v1/pokemons/{name}` - Retorna os dados de um pokémon específico do banco
4. `GET /api/v1/health` - Verifica a saúde de todos os serviços

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **MongoDB**: Banco de dados NoSQL
- **Docker**: Containerização da aplicação
- **Agnos**: Orquestração da comunicação com MCPs
- **Motor**: Driver assíncrono para MongoDB
- **Pydantic**: Validação de dados

## Estrutura do Projeto

```
poke-agent/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── pokemon.py          # Modelos Pydantic
│   ├── routers/
│   │   ├── __init__.py
│   │   └── pokemon.py          # Rotas da API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agnos_client.py     # Cliente Agnos para MCPs
│   │   ├── database.py         # Serviço de banco de dados
│   │   └── pokemon_service.py  # Serviço principal
│   ├── __init__.py
│   ├── config.py               # Configurações
│   └── main.py                 # Aplicação principal
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Como Executar

### Pré-requisitos

- Docker
- Docker Compose

### Executando com Docker Compose

1. Clone o repositório:
```bash
git clone <repository-url>
cd poke-agent
```

2. Execute a aplicação:
```bash
docker-compose up --build
```

3. A API estará disponível em: http://localhost:8000

4. Documentação da API (Swagger): http://localhost:8000/docs

### Executando Localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente no arquivo `.env`:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pokemon_db
POKEMON_MCP_URL=https://smithery.ai/server/@NaveenBandarage/poke-mcp
MONGODB_MCP_URL=https://smithery.ai/server/@mongodb-js/mongodb-mcp-server
```

3. Execute o MongoDB:
```bash
docker run -d -p 27017:27017 mongo:7.0
```

4. Execute a aplicação:
```bash
uvicorn app.main:app --reload
```

## Exemplos de Uso

### Importar um Pokémon
```bash
curl "http://localhost:8000/api/v1/import-pokemon?name=pikachu"
```

### Listar todos os Pokémons
```bash
curl "http://localhost:8000/api/v1/pokemons"
```

### Buscar um Pokémon específico
```bash
curl "http://localhost:8000/api/v1/pokemons/pikachu"
```

### Verificar saúde dos serviços
```bash
curl "http://localhost:8000/api/v1/health"
```

## Variáveis de Ambiente

- `MONGODB_URL`: URL de conexão com MongoDB (padrão: mongodb://localhost:27017)
- `DATABASE_NAME`: Nome do banco de dados (padrão: pokemon_db)
- `POKEMON_MCP_URL`: URL do Pokémon MCP
- `MONGODB_MCP_URL`: URL do MongoDB MCP
- `LOG_LEVEL`: Nível de log (padrão: INFO)
- `ENVIRONMENT`: Ambiente de execução (padrão: development)

## Testes

### Executando os Testes

Para executar os testes da aplicação:

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio

# Executar todos os testes
pytest

# Executar testes com mais detalhes
pytest -v

# Executar um teste específico
pytest tests/test_api.py::TestPokemonAPI::test_import_pokemon_success
```

### Executando Testes no Docker

```bash
# Executar testes dentro do container
docker-compose exec app pytest

# Ou construir uma imagem específica para testes
docker build -t poke-agent-test .
docker run --rm poke-agent-test pytest
```

## Desenvolvimento

### Estrutura de Dados

Os pokémons são armazenados com a seguinte estrutura:

```json
{
  "id": 25,
  "name": "pikachu",
  "height": 4,
  "weight": 60,
  "base_experience": 112,
  "types": [
    {
      "name": "electric",
      "url": "https://pokeapi.co/api/v2/type/13/"
    }
  ],
  "abilities": [
    {
      "name": "static",
      "url": "https://pokeapi.co/api/v2/ability/9/",
      "is_hidden": false
    }
  ],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special_attack": 50,
    "special_defense": 50,
    "speed": 90
  },
  "sprites": {
    "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    "front_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png",
    "back_default": null,
    "back_shiny": null
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Licença

Este projeto é licenciado sob a MIT License.
