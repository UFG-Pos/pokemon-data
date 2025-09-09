import logging
import os
from typing import Dict, Any


def setup_logging():
    """
    Configura o sistema de logging da aplicação.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # Configurar loggers específicos
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)


def get_settings() -> Dict[str, Any]:
    """
    Retorna as configurações da aplicação.
    """
    return {
        "mongodb_url": os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
        "database_name": os.getenv("DATABASE_NAME", "pokemon_db"),
        "pokemon_mcp_url": os.getenv("POKEMON_MCP_URL"),
        "mongodb_mcp_url": os.getenv("MONGODB_MCP_URL"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
