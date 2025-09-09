from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PokemonStats(BaseModel):
    hp: int
    attack: int
    defense: int
    special_attack: int = Field(alias="special-attack")
    special_defense: int = Field(alias="special-defense")
    speed: int

    class Config:
        populate_by_name = True


class PokemonType(BaseModel):
    name: str
    url: str


class PokemonAbility(BaseModel):
    name: str
    url: str
    is_hidden: bool = False


class PokemonSprite(BaseModel):
    front_default: Optional[str] = None
    front_shiny: Optional[str] = None
    back_default: Optional[str] = None
    back_shiny: Optional[str] = None


class Pokemon(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    base_experience: Optional[int] = None
    types: List[PokemonType]
    abilities: List[PokemonAbility]
    stats: PokemonStats
    sprites: PokemonSprite
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PokemonResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Pokemon] = None


class PokemonListResponse(BaseModel):
    success: bool
    message: str
    data: List[Pokemon] = []
    total: int = 0
