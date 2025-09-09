import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from app.models.pokemon import Pokemon
from app.services.database import DatabaseService
from app.services.agnos_client import AgnosClient

logger = logging.getLogger(__name__)


class PokemonService:
    """
    Serviço principal para operações com Pokémons.
    Integra Agnos Client e Database Service.
    """
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.agnos_client = AgnosClient()
    
    async def fetch_pokemon_from_api(self, pokemon_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações do pokémon via Pokémon MCP através do Agnos.
        """
        try:
            logger.info(f"Fetching pokemon from API: {pokemon_name}")
            
            # Chamar o Pokémon MCP via Agnos
            pokemon_data = await self.agnos_client.call_pokemon_mcp(pokemon_name)
            
            if not pokemon_data:
                logger.warning(f"Pokemon not found in API: {pokemon_name}")
                return None
            
            # Validar e normalizar dados
            normalized_data = self._normalize_pokemon_data(pokemon_data)
            
            logger.info(f"Successfully fetched pokemon data: {pokemon_name}")
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error fetching pokemon from API {pokemon_name}: {str(e)}")
            raise
    
    def _normalize_pokemon_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza os dados do pokémon para o formato esperado.
        """
        try:
            # Normalizar stats
            stats = raw_data.get("stats", {})
            normalized_stats = {
                "hp": stats.get("hp", 0),
                "attack": stats.get("attack", 0),
                "defense": stats.get("defense", 0),
                "special-attack": stats.get("special_attack", stats.get("special-attack", 0)),
                "special-defense": stats.get("special_defense", stats.get("special-defense", 0)),
                "speed": stats.get("speed", 0)
            }
            
            # Normalizar tipos
            types = raw_data.get("types", [])
            normalized_types = []
            for type_info in types:
                if isinstance(type_info, dict):
                    normalized_types.append({
                        "name": type_info.get("name", ""),
                        "url": type_info.get("url", "")
                    })
            
            # Normalizar habilidades
            abilities = raw_data.get("abilities", [])
            normalized_abilities = []
            for ability_info in abilities:
                if isinstance(ability_info, dict):
                    normalized_abilities.append({
                        "name": ability_info.get("name", ""),
                        "url": ability_info.get("url", ""),
                        "is_hidden": ability_info.get("is_hidden", False)
                    })
            
            # Normalizar sprites
            sprites = raw_data.get("sprites", {})
            normalized_sprites = {
                "front_default": sprites.get("front_default"),
                "front_shiny": sprites.get("front_shiny"),
                "back_default": sprites.get("back_default"),
                "back_shiny": sprites.get("back_shiny")
            }
            
            normalized_data = {
                "id": raw_data.get("id", 0),
                "name": raw_data.get("name", "").lower(),
                "height": raw_data.get("height", 0),
                "weight": raw_data.get("weight", 0),
                "base_experience": raw_data.get("base_experience"),
                "types": normalized_types,
                "abilities": normalized_abilities,
                "stats": normalized_stats,
                "sprites": normalized_sprites
            }
            
            return normalized_data
            
        except Exception as e:
            logger.error(f"Error normalizing pokemon data: {str(e)}")
            raise
    
    async def save_pokemon(self, pokemon_data: Dict[str, Any]) -> Pokemon:
        """
        Salva um pokémon no MongoDB via MongoDB MCP através do Agnos.
        """
        try:
            logger.info(f"Saving pokemon: {pokemon_data.get('name')}")
            
            # Chamar o MongoDB MCP via Agnos para notificar a operação
            await self.agnos_client.call_mongodb_mcp(
                operation="insert",
                collection="pokemons",
                data=pokemon_data
            )
            
            # Salvar no banco de dados
            saved_pokemon = await self.db_service.save_pokemon(pokemon_data)
            
            logger.info(f"Pokemon saved successfully: {saved_pokemon.name}")
            return saved_pokemon
            
        except Exception as e:
            logger.error(f"Error saving pokemon: {str(e)}")
            raise
    
    async def get_pokemon_by_name(self, name: str) -> Optional[Pokemon]:
        """
        Busca um pokémon pelo nome no banco de dados.
        """
        try:
            logger.info(f"Getting pokemon by name: {name}")
            
            pokemon = await self.db_service.get_pokemon_by_name(name.lower())
            
            if pokemon:
                logger.info(f"Pokemon found: {name}")
            else:
                logger.info(f"Pokemon not found: {name}")
            
            return pokemon
            
        except Exception as e:
            logger.error(f"Error getting pokemon by name {name}: {str(e)}")
            raise
    
    async def list_pokemons(self, skip: int = 0, limit: int = 100) -> Tuple[List[Pokemon], int]:
        """
        Lista pokémons com paginação.
        """
        try:
            logger.info(f"Listing pokemons with skip={skip}, limit={limit}")
            
            pokemons, total = await self.db_service.list_pokemons(skip=skip, limit=limit)
            
            logger.info(f"Retrieved {len(pokemons)} pokemons out of {total} total")
            return pokemons, total
            
        except Exception as e:
            logger.error(f"Error listing pokemons: {str(e)}")
            raise
    
    async def delete_pokemon(self, name: str) -> bool:
        """
        Remove um pokémon do banco de dados.
        """
        try:
            logger.info(f"Deleting pokemon: {name}")
            
            # Chamar o MongoDB MCP via Agnos para notificar a operação
            await self.agnos_client.call_mongodb_mcp(
                operation="delete",
                collection="pokemons",
                data={"name": name.lower()}
            )
            
            # Deletar do banco de dados
            deleted = await self.db_service.delete_pokemon(name.lower())
            
            if deleted:
                logger.info(f"Pokemon deleted successfully: {name}")
            else:
                logger.warning(f"Pokemon not found for deletion: {name}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting pokemon {name}: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde de todos os serviços.
        """
        try:
            # Verificar Agnos e MCPs
            agnos_health = await self.agnos_client.health_check()
            
            # Verificar banco de dados
            db_health = await self.db_service.health_check()
            
            overall_status = "healthy"
            if (agnos_health.get("agnos_status") != "connected" or 
                db_health.get("status") != "healthy"):
                overall_status = "degraded"
            
            return {
                "overall_status": overall_status,
                "agnos": agnos_health,
                "database": db_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
