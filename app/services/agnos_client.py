import asyncio
import json
import logging
from typing import Dict, Any, Optional
import httpx
import os

logger = logging.getLogger(__name__)


class AgnosClient:
    """
    Cliente para interagir com o Agnos e orquestrar comunicação com MCPs.
    """
    
    def __init__(self):
        self.pokemon_mcp_url = os.getenv("POKEMON_MCP_URL")
        self.mongodb_mcp_url = os.getenv("MONGODB_MCP_URL")
        self.timeout = 30.0
        
    async def call_pokemon_mcp(self, pokemon_name: str) -> Optional[Dict[str, Any]]:
        """
        Chama o Pokémon MCP para buscar informações de um pokémon.
        """
        try:
            logger.info(f"Calling Pokemon MCP for: {pokemon_name}")
            
            # Simular chamada para o Pokemon MCP via Agnos
            # Na implementação real, isso seria uma chamada para o Agnos
            # que orquestraria a comunicação com o MCP
            
            # Por enquanto, vamos usar a PokeAPI diretamente como fallback
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Transformar dados da PokeAPI para nosso formato
                    pokemon_data = {
                        "id": data["id"],
                        "name": data["name"],
                        "height": data["height"],
                        "weight": data["weight"],
                        "base_experience": data.get("base_experience"),
                        "types": [
                            {
                                "name": type_info["type"]["name"],
                                "url": type_info["type"]["url"]
                            }
                            for type_info in data["types"]
                        ],
                        "abilities": [
                            {
                                "name": ability_info["ability"]["name"],
                                "url": ability_info["ability"]["url"],
                                "is_hidden": ability_info.get("is_hidden", False)
                            }
                            for ability_info in data["abilities"]
                        ],
                        "stats": {
                            stat["stat"]["name"].replace("-", "_"): stat["base_stat"]
                            for stat in data["stats"]
                        },
                        "sprites": {
                            "front_default": data["sprites"].get("front_default"),
                            "front_shiny": data["sprites"].get("front_shiny"),
                            "back_default": data["sprites"].get("back_default"),
                            "back_shiny": data["sprites"].get("back_shiny")
                        }
                    }
                    
                    logger.info(f"Successfully fetched pokemon data for: {pokemon_name}")
                    return pokemon_data
                    
                elif response.status_code == 404:
                    logger.warning(f"Pokemon not found: {pokemon_name}")
                    return None
                else:
                    logger.error(f"Error fetching pokemon {pokemon_name}: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching pokemon: {pokemon_name}")
            return None
        except Exception as e:
            logger.error(f"Error calling Pokemon MCP for {pokemon_name}: {str(e)}")
            return None
    
    async def call_mongodb_mcp(self, operation: str, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chama o MongoDB MCP para operações de banco de dados.
        """
        try:
            logger.info(f"Calling MongoDB MCP for operation: {operation}")
            
            # Simular chamada para o MongoDB MCP via Agnos
            # Na implementação real, isso seria uma chamada para o Agnos
            # que orquestraria a comunicação com o MCP do MongoDB
            
            # Por enquanto, retornamos um resultado simulado
            # A implementação real do MongoDB será feita no DatabaseService
            
            result = {
                "success": True,
                "operation": operation,
                "collection": collection,
                "data": data
            }
            
            logger.info(f"MongoDB MCP operation completed: {operation}")
            return result
            
        except Exception as e:
            logger.error(f"Error calling MongoDB MCP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da conexão com os MCPs.
        """
        try:
            # Verificar conectividade com os MCPs
            pokemon_status = "unknown"
            mongodb_status = "unknown"
            
            # Teste simples para Pokemon MCP
            try:
                test_result = await self.call_pokemon_mcp("pikachu")
                pokemon_status = "healthy" if test_result else "unhealthy"
            except:
                pokemon_status = "unhealthy"
            
            # Teste simples para MongoDB MCP
            try:
                test_result = await self.call_mongodb_mcp("ping", "test", {})
                mongodb_status = "healthy" if test_result.get("success") else "unhealthy"
            except:
                mongodb_status = "unhealthy"
            
            return {
                "agnos_status": "connected",
                "pokemon_mcp": pokemon_status,
                "mongodb_mcp": mongodb_status
            }
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            return {
                "agnos_status": "error",
                "error": str(e)
            }
