import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app


class TestPokemonAPI:
    """
    Testes para a API de Pokémon.
    """
    
    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Testa o endpoint raiz."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Pokemon Agent API"
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self):
        """Testa o endpoint de health check."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @patch('app.services.pokemon_service.PokemonService.fetch_pokemon_from_api')
    @patch('app.services.pokemon_service.PokemonService.save_pokemon')
    def test_import_pokemon_success(self, mock_save, mock_fetch):
        """Testa importação bem-sucedida de pokémon."""
        # Mock dos dados do pokémon
        mock_pokemon_data = {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "base_experience": 112,
            "types": [{"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}],
            "abilities": [{"name": "static", "url": "https://pokeapi.co/api/v2/ability/9/", "is_hidden": False}],
            "stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
            "sprites": {"front_default": "https://example.com/pikachu.png", "front_shiny": None, "back_default": None, "back_shiny": None}
        }
        
        # Configurar mocks
        mock_fetch.return_value = mock_pokemon_data
        mock_save.return_value = mock_pokemon_data
        
        # Fazer requisição
        response = self.client.get("/api/v1/import-pokemon?name=pikachu")
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "pikachu" in data["message"]
        assert data["data"]["name"] == "pikachu"
    
    def test_import_pokemon_not_found(self):
        """Testa importação de pokémon não encontrado."""
        with patch('app.services.pokemon_service.PokemonService.fetch_pokemon_from_api') as mock_fetch:
            mock_fetch.return_value = None
            
            response = self.client.get("/api/v1/import-pokemon?name=nonexistent")
            
            assert response.status_code == 404
            data = response.json()
            assert "não encontrado" in data["detail"]
    
    def test_import_pokemon_missing_name(self):
        """Testa importação sem nome do pokémon."""
        response = self.client.get("/api/v1/import-pokemon")
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.pokemon_service.PokemonService.list_pokemons')
    def test_list_pokemons(self, mock_list):
        """Testa listagem de pokémons."""
        # Mock da lista de pokémons
        mock_pokemons = [
            {
                "id": 25,
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "base_experience": 112,
                "types": [{"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}],
                "abilities": [{"name": "static", "url": "https://pokeapi.co/api/v2/ability/9/", "is_hidden": False}],
                "stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
                "sprites": {"front_default": "https://example.com/pikachu.png", "front_shiny": None, "back_default": None, "back_shiny": None}
            }
        ]
        
        mock_list.return_value = (mock_pokemons, 1)
        
        response = self.client.get("/api/v1/pokemons")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 1
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "pikachu"
    
    @patch('app.services.pokemon_service.PokemonService.get_pokemon_by_name')
    def test_get_pokemon_by_name_success(self, mock_get):
        """Testa busca de pokémon por nome - sucesso."""
        mock_pokemon = {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "base_experience": 112,
            "types": [{"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}],
            "abilities": [{"name": "static", "url": "https://pokeapi.co/api/v2/ability/9/", "is_hidden": False}],
            "stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
            "sprites": {"front_default": "https://example.com/pikachu.png", "front_shiny": None, "back_default": None, "back_shiny": None}
        }
        
        mock_get.return_value = mock_pokemon
        
        response = self.client.get("/api/v1/pokemons/pikachu")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "pikachu"
    
    @patch('app.services.pokemon_service.PokemonService.get_pokemon_by_name')
    def test_get_pokemon_by_name_not_found(self, mock_get):
        """Testa busca de pokémon por nome - não encontrado."""
        mock_get.return_value = None
        
        response = self.client.get("/api/v1/pokemons/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "não encontrado" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__])
