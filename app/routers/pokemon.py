from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.models.pokemon import Pokemon, PokemonResponse, PokemonListResponse
from app.services.database import DatabaseService
from app.services.pokemon_service import PokemonService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db_service():
    from app.main import app
    return app.state.db_service


async def get_pokemon_service(db_service: DatabaseService = Depends(get_db_service)):
    return PokemonService(db_service)


@router.get("/import-pokemon", response_model=PokemonResponse)
async def import_pokemon(
    name: str = Query(..., description="Nome do Pokémon para importar"),
    pokemon_service: PokemonService = Depends(get_pokemon_service)
):
    """
    Busca informações do pokémon via Pokémon MCP e salva no MongoDB via MongoDB MCP.
    """
    try:
        logger.info(f"Importing pokemon: {name}")
        
        # Fetch pokemon data from Pokemon MCP
        pokemon_data = await pokemon_service.fetch_pokemon_from_api(name.lower())
        
        if not pokemon_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Pokémon '{name}' não encontrado"
            )
        
        # Save to MongoDB via MongoDB MCP
        saved_pokemon = await pokemon_service.save_pokemon(pokemon_data)
        
        return PokemonResponse(
            success=True,
            message=f"Pokémon '{name}' importado com sucesso",
            data=saved_pokemon
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing pokemon {name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao importar pokémon: {str(e)}"
        )


@router.get("/pokemons", response_model=PokemonListResponse)
async def list_pokemons(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros para retornar"),
    pokemon_service: PokemonService = Depends(get_pokemon_service)
):
    """
    Lista todos os pokémons registrados no banco.
    """
    try:
        logger.info(f"Listing pokemons with skip={skip}, limit={limit}")
        
        pokemons, total = await pokemon_service.list_pokemons(skip=skip, limit=limit)
        
        return PokemonListResponse(
            success=True,
            message=f"Encontrados {len(pokemons)} pokémons",
            data=pokemons,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing pokemons: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao listar pokémons: {str(e)}"
        )


@router.get("/pokemons/{name}", response_model=PokemonResponse)
async def get_pokemon(
    name: str,
    pokemon_service: PokemonService = Depends(get_pokemon_service)
):
    """
    Retorna os dados de um pokémon específico do banco.
    """
    try:
        logger.info(f"Getting pokemon: {name}")

        pokemon = await pokemon_service.get_pokemon_by_name(name.lower())

        if not pokemon:
            raise HTTPException(
                status_code=404,
                detail=f"Pokémon '{name}' não encontrado no banco de dados"
            )

        return PokemonResponse(
            success=True,
            message=f"Pokémon '{name}' encontrado",
            data=pokemon
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pokemon {name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar pokémon: {str(e)}"
        )


@router.get("/health")
async def health_check(
    pokemon_service: PokemonService = Depends(get_pokemon_service)
):
    """
    Verifica a saúde de todos os serviços.
    """
    try:
        health_status = await pokemon_service.health_check()
        return health_status

    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no health check: {str(e)}"
        )
