from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routers import pokemon
from app.services.database import DatabaseService
from app.config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Pokemon Agent API...")
    
    # Initialize database connection
    db_service = DatabaseService()
    await db_service.connect()
    app.state.db_service = db_service
    
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


# Dependency to get database service
async def get_db_service():
    return app.state.db_service
