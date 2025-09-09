import os
import logging
from typing import List, Optional, Tuple, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from datetime import datetime

from app.models.pokemon import Pokemon

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Serviço para gerenciar conexões e operações com MongoDB.
    """
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "pokemon_db")
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.pokemon_collection: Optional[AsyncIOMotorCollection] = None
        
    async def connect(self):
        """
        Conecta ao MongoDB.
        """
        try:
            logger.info(f"Connecting to MongoDB at: {self.mongodb_url}")
            
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.database = self.client[self.database_name]
            self.pokemon_collection = self.database["pokemons"]
            
            # Criar índices
            await self._create_indexes()
            
            # Testar conexão
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """
        Desconecta do MongoDB.
        """
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """
        Cria índices necessários no banco de dados.
        """
        try:
            # Índice único no nome do pokémon
            await self.pokemon_collection.create_index("name", unique=True)
            
            # Índice no ID do pokémon
            await self.pokemon_collection.create_index("id")
            
            # Índice na data de criação
            await self.pokemon_collection.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    async def save_pokemon(self, pokemon_data: Dict[str, Any]) -> Pokemon:
        """
        Salva um pokémon no banco de dados.
        """
        try:
            # Adicionar timestamps
            now = datetime.utcnow()
            pokemon_data["created_at"] = now
            pokemon_data["updated_at"] = now
            
            # Tentar inserir
            try:
                result = await self.pokemon_collection.insert_one(pokemon_data)
                logger.info(f"Pokemon {pokemon_data['name']} saved with ID: {result.inserted_id}")
                
            except DuplicateKeyError:
                # Se já existe, atualizar
                pokemon_data["updated_at"] = now
                # Remover _id se existir para evitar erro de campo imutável
                update_data = {k: v for k, v in pokemon_data.items() if k != "_id"}
                await self.pokemon_collection.update_one(
                    {"name": pokemon_data["name"]},
                    {"$set": update_data}
                )
                logger.info(f"Pokemon {pokemon_data['name']} updated")
            
            # Retornar o pokémon salvo
            saved_pokemon = await self.pokemon_collection.find_one(
                {"name": pokemon_data["name"]}
            )
            
            if saved_pokemon:
                # Remover _id do MongoDB para serialização
                saved_pokemon.pop("_id", None)
                return Pokemon(**saved_pokemon)
            else:
                raise Exception("Failed to retrieve saved pokemon")
                
        except Exception as e:
            logger.error(f"Error saving pokemon: {str(e)}")
            raise
    
    async def get_pokemon_by_name(self, name: str) -> Optional[Pokemon]:
        """
        Busca um pokémon pelo nome.
        """
        try:
            pokemon_doc = await self.pokemon_collection.find_one({"name": name})
            
            if pokemon_doc:
                # Remover _id do MongoDB para serialização
                pokemon_doc.pop("_id", None)
                return Pokemon(**pokemon_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pokemon by name {name}: {str(e)}")
            raise
    
    async def list_pokemons(self, skip: int = 0, limit: int = 100) -> Tuple[List[Pokemon], int]:
        """
        Lista pokémons com paginação.
        """
        try:
            # Contar total de documentos
            total = await self.pokemon_collection.count_documents({})
            
            # Buscar pokémons com paginação
            cursor = self.pokemon_collection.find({}).skip(skip).limit(limit).sort("name", 1)
            pokemon_docs = await cursor.to_list(length=limit)
            
            # Converter para objetos Pokemon
            pokemons = []
            for doc in pokemon_docs:
                doc.pop("_id", None)  # Remover _id do MongoDB
                pokemons.append(Pokemon(**doc))
            
            logger.info(f"Retrieved {len(pokemons)} pokemons (total: {total})")
            return pokemons, total
            
        except Exception as e:
            logger.error(f"Error listing pokemons: {str(e)}")
            raise
    
    async def delete_pokemon(self, name: str) -> bool:
        """
        Remove um pokémon do banco de dados.
        """
        try:
            result = await self.pokemon_collection.delete_one({"name": name})
            
            if result.deleted_count > 0:
                logger.info(f"Pokemon {name} deleted successfully")
                return True
            else:
                logger.warning(f"Pokemon {name} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting pokemon {name}: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da conexão com o banco de dados.
        """
        try:
            # Ping no banco
            await self.client.admin.command('ping')
            
            # Contar documentos na coleção
            count = await self.pokemon_collection.count_documents({})
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "pokemon_count": count
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
