# Guia de Uso - Pokemon Agent API

## Início Rápido

### 1. Executar a Aplicação

```bash
# Clonar o repositório
git clone <repository-url>
cd poke-agent

# Executar com Docker Compose
docker-compose up --build -d

# Verificar se está funcionando
curl http://localhost:8000/health
```

### 2. Testar as Funcionalidades

#### Importar um Pokémon
```bash
curl "http://localhost:8000/api/v1/import-pokemon?name=pikachu"
```

#### Listar Pokémons
```bash
curl "http://localhost:8000/api/v1/pokemons"
```

#### Buscar Pokémon Específico
```bash
curl "http://localhost:8000/api/v1/pokemons/pikachu"
```

#### Health Check Detalhado
```bash
curl "http://localhost:8000/api/v1/health"
```

### 3. Executar Demonstração Completa

```bash
python3 examples/demo.py
```

## Endpoints da API

### Base URL: `http://localhost:8000`

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Health check básico |
| GET | `/docs` | Documentação Swagger |
| GET | `/api/v1/import-pokemon?name={name}` | Importa pokémon |
| GET | `/api/v1/pokemons` | Lista pokémons |
| GET | `/api/v1/pokemons/{name}` | Busca pokémon |
| GET | `/api/v1/health` | Health check detalhado |

## Parâmetros de Query

### `/api/v1/import-pokemon`
- `name` (obrigatório): Nome do pokémon para importar

### `/api/v1/pokemons`
- `skip` (opcional): Número de registros para pular (padrão: 0)
- `limit` (opcional): Número máximo de registros (padrão: 100, máximo: 1000)

## Exemplos de Resposta

### Importação Bem-sucedida
```json
{
  "success": true,
  "message": "Pokémon 'pikachu' importado com sucesso",
  "data": {
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
      "special-attack": 50,
      "special-defense": 50,
      "speed": 90
    },
    "sprites": {
      "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
      "front_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/25.png",
      "back_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/25.png",
      "back_shiny": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/shiny/25.png"
    },
    "created_at": "2025-09-09T11:57:12.485000",
    "updated_at": "2025-09-09T11:57:12.485000"
  }
}
```

### Lista de Pokémons
```json
{
  "success": true,
  "message": "Encontrados 2 pokémons",
  "data": [
    {
      "id": 25,
      "name": "pikachu",
      "height": 4,
      "weight": 60,
      "types": [{"name": "electric", "url": "..."}],
      "..."
    },
    {
      "id": 6,
      "name": "charizard",
      "height": 17,
      "weight": 905,
      "types": [{"name": "fire", "url": "..."}, {"name": "flying", "url": "..."}],
      "..."
    }
  ],
  "total": 2
}
```

### Health Check
```json
{
  "overall_status": "healthy",
  "agnos": {
    "agnos_status": "connected",
    "pokemon_mcp": "healthy",
    "mongodb_mcp": "healthy"
  },
  "database": {
    "status": "healthy",
    "database": "pokemon_db",
    "pokemon_count": 4
  },
  "timestamp": "2025-09-09T11:55:51.199430"
}
```

## Códigos de Status

- `200`: Sucesso
- `404`: Pokémon não encontrado
- `422`: Erro de validação (parâmetros inválidos)
- `500`: Erro interno do servidor

## Troubleshooting

### Problema: Porta 27017 já em uso
**Solução**: A aplicação usa a porta 27019 para MongoDB. Verifique se não há conflitos.

### Problema: API não responde
**Solução**: 
1. Verifique se os containers estão rodando: `docker-compose ps`
2. Verifique os logs: `docker-compose logs app`

### Problema: Erro de conexão com MongoDB
**Solução**: 
1. Verifique se o MongoDB está rodando: `docker-compose logs mongodb`
2. Reinicie os serviços: `docker-compose restart`

## Desenvolvimento

### Executar Testes
```bash
# Instalar dependências
pip install pytest pytest-asyncio

# Executar testes
pytest

# Executar testes no Docker
docker-compose exec app pytest
```

### Logs
```bash
# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do MongoDB
docker-compose logs -f mongodb
```

### Parar Aplicação
```bash
docker-compose down
```

### Limpar Dados
```bash
# Parar e remover volumes (apaga dados do banco)
docker-compose down -v
```
