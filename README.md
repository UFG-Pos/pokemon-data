# Pokemon Agent API com Pipeline de Dados

Uma aplicação Python completa que integra MCPs (Model Control Protocols) da Smithery usando Docker e o agente Agnos para buscar, armazenar e processar informações de pokémons com pipeline de dados em tempo real.

## 🚀 Funcionalidades Principais

### Core Features
- **Pokémon MCP**: Busca informações de pokémons via PokeAPI
- **MongoDB MCP**: Armazena dados em banco MongoDB
- **Agnos**: Orquestra a comunicação entre MCPs
- **API FastAPI**: Endpoints completos para gerenciamento de pokémons

### 🔧 Pipeline de Processamento de Dados
- **File Processor MCP**: Processamento de arquivos CSV/JSON
- **Stream Processor MCP**: Processamento em tempo real
- **Sistema de Alertas**: Detecção automática de anomalias
- **Dashboard**: Visualizações e relatórios automáticos
- **Relatórios Programados**: Diários, semanais e mensais

### 📊 Funcionalidades Avançadas
- **Exportação de Dados**: CSV, JSON com transformações
- **Limpeza e Normalização**: Automática de dados
- **Detecção de Anomalias**: Stats negativos, tipos inválidos, etc.
- **Alertas em Tempo Real**: Sistema configurável de notificações
- **Dashboards Interativos**: HTML com métricas e visualizações
- **Monitoramento**: Status da pipeline e métricas de qualidade

## 📋 Endpoints da API

### Pokémons (Core)
- `GET /api/v1/import-pokemon?name=pikachu` - Importa pokémon via Pokémon MCP
- `GET /api/v1/pokemons` - Lista todos os pokémons do banco
- `GET /api/v1/pokemons/{name}` - Busca pokémon específico

### Pipeline - Processamento de Arquivos
- `POST /api/v1/pipeline/file/export-csv` - Exporta dados para CSV
- `POST /api/v1/pipeline/file/export-json` - Exporta dados para JSON
- `POST /api/v1/pipeline/file/clean-data` - Limpeza e normalização
- `GET /api/v1/pipeline/file/aggregations` - Estatísticas e agregações
- `POST /api/v1/pipeline/file/generate-report` - Relatórios automáticos
- `POST /api/v1/pipeline/file/upload` - Upload e processamento de arquivos

### Pipeline - Stream Processing
- `POST /api/v1/pipeline/stream/start` - Inicia processamento em tempo real
- `POST /api/v1/pipeline/stream/stop` - Para processamento
- `GET /api/v1/pipeline/stream/status` - Status do stream processor
- `GET /api/v1/pipeline/stream/events` - Eventos recentes
- `POST /api/v1/pipeline/stream/anomaly-rule` - Configura regras de anomalia
- `POST /api/v1/pipeline/stream/simulate-anomaly` - Simula anomalias para teste

### Pipeline - Dashboard
- `GET /api/v1/pipeline/dashboard/data` - Dados completos do dashboard
- `GET /api/v1/pipeline/dashboard/html` - Dashboard em HTML
- `POST /api/v1/pipeline/dashboard/report` - Relatórios programados
- `POST /api/v1/pipeline/dashboard/clear-cache` - Limpa cache

### Pipeline - Alertas
- `POST /api/v1/pipeline/alerts/send` - Envia alerta manual
- `GET /api/v1/pipeline/alerts/history` - Histórico de alertas
- `GET /api/v1/pipeline/alerts/metrics` - Métricas do sistema
- `POST /api/v1/pipeline/alerts/configure-channel` - Configura canais
- `POST /api/v1/pipeline/alerts/test` - Teste de alertas

### Sistema
- `GET /health` - Health check da aplicação
- `GET /api/v1/health` - Health check detalhado
- `GET /api/v1/pipeline/status` - Status geral da pipeline
- `GET /api/v1/pipeline/download/{type}/{filename}` - Download de arquivos

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **MongoDB**: Banco de dados NoSQL
- **Docker**: Containerização da aplicação
- **Agnos**: Orquestração da comunicação com MCPs
- **Motor**: Driver assíncrono para MongoDB
- **Pydantic**: Validação de dados
- **Pandas**: Processamento e análise de dados
- **AsyncIO**: Processamento assíncrono

## 📁 Estrutura do Projeto

```
poke-agent/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── pokemon.py              # Modelos Pydantic
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pokemon.py              # Rotas da API (core)
│   │   └── pipeline.py             # Rotas da Pipeline
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agnos_client.py         # Cliente Agnos para MCPs
│   │   ├── database.py             # Serviço de banco de dados
│   │   ├── pokemon_service.py      # Serviço principal
│   │   ├── file_processor.py       # MCP File Processor
│   │   ├── stream_processor.py     # MCP Stream Processor
│   │   ├── dashboard_service.py    # Serviço de Dashboard
│   │   └── alert_system.py         # Sistema de Alertas
│   ├── static/                     # Frontend Dashboard
│   │   ├── index.html              # Interface principal
│   │   └── dashboard.js            # JavaScript do dashboard
│   ├── __init__.py
│   ├── config.py                   # Configurações
│   └── main.py                     # Aplicação principal
├── data/                           # Dados gerados pela pipeline
│   ├── exports/                    # Exportações CSV/JSON
│   ├── reports/                    # Relatórios gerados
│   ├── dashboards/                 # Dashboards HTML
│   ├── alerts/                     # Logs de alertas
│   └── temp/                       # Arquivos temporários
├── examples/
│   ├── demo.py                     # Demo original
│   └── pipeline_demo.py            # Demo da pipeline
├── tests/                          # Testes automatizados
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## 🚀 Como Usar

### Pré-requisitos

- Docker
- Docker Compose

### 1. Executando com Docker Compose

```bash
# Clone o repositório
git clone <repository-url>
cd poke-agent

# Execute a aplicação
docker-compose up --build -d
```

### 2. 🎯 Acessar o Frontend Dashboard (RECOMENDADO)

**Interface Principal**: http://localhost:8000

O dashboard web oferece uma interface intuitiva para:
- **🎮 Gerenciar Pokémons**: Importar, listar e visualizar
- **⚙️ Controlar Pipeline**: Iniciar/parar stream processing
- **🚨 Monitorar Alertas**: Visualizar alertas em tempo real
- **📊 Gerar Relatórios**: Exportar dados e criar dashboards
- **📈 Visualizar Métricas**: Status da pipeline e qualidade dos dados

### 3. Outras Interfaces

- **API Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

## 🧪 Testando a Pipeline

### Demonstração Completa da Pipeline

Execute o script de demonstração que testa todas as funcionalidades:

```bash
# Certifique-se de que a aplicação está rodando
docker-compose up -d

# Execute a demonstração da pipeline
python3 examples/pipeline_demo.py
```

### Testando Funcionalidades Específicas

```bash
# 1. Processamento de Arquivos
curl -X POST "http://localhost:8000/api/v1/pipeline/file/export-csv"
curl -X POST "http://localhost:8000/api/v1/pipeline/file/clean-data"
curl "http://localhost:8000/api/v1/pipeline/file/aggregations"

# 2. Stream Processing
curl -X POST "http://localhost:8000/api/v1/pipeline/stream/start"
curl "http://localhost:8000/api/v1/pipeline/stream/status"
curl -X POST "http://localhost:8000/api/v1/pipeline/stream/simulate-anomaly?pokemon_name=pikachu&anomaly_type=negative_stats"

# 3. Dashboard
curl "http://localhost:8000/api/v1/pipeline/dashboard/data"
curl -X POST "http://localhost:8000/api/v1/pipeline/dashboard/report?report_type=daily"

# 4. Sistema de Alertas
curl -X POST "http://localhost:8000/api/v1/pipeline/alerts/test?level=info"
curl "http://localhost:8000/api/v1/pipeline/alerts/metrics"

# 5. Status Geral
curl "http://localhost:8000/api/v1/pipeline/status"
```

### Arquivos Gerados

A pipeline gera vários tipos de arquivos na pasta `data/`:

- **Exportações**: `data/exports/` - Arquivos CSV/JSON exportados
- **Relatórios**: `data/reports/` - Relatórios automáticos
- **Dashboards**: `data/dashboards/` - Dashboards HTML
- **Alertas**: `data/alerts/` - Logs de alertas
- **Temporários**: `data/temp/` - Arquivos temporários

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
