from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routers import pokemon, pipeline
from app.services.database import DatabaseService
from app.config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Pokemon Agent API with Pipeline...")

    # Initialize database connection
    global database_service
    database_service = DatabaseService()
    await database_service.connect()
    app.state.db_service = database_service

    # Create data directories
    from pathlib import Path
    data_dirs = ["data/exports", "data/reports", "data/dashboards", "data/alerts", "data/temp"]
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print("✅ Pipeline services initialized")

    yield

    # Shutdown
    print("Shutting down Pokemon Agent API...")
    if hasattr(app.state, 'db_service'):
        await app.state.db_service.disconnect()


app = FastAPI(
    title="Pokemon Agent API",
    description="API para buscar e armazenar informações de Pokémons usando MCPs",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pokemon.router, prefix="/api/v1", tags=["pokemon"])
app.include_router(pipeline.router, tags=["pipeline"])


@app.get("/")
async def root():
    return {
        "message": "Pokemon Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Global database service instance for dependencies
database_service = None


# Dependency to get database service
async def get_db_service():
    return app.state.db_service
