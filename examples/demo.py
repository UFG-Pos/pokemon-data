#!/usr/bin/env python3
"""
Script de demonstração da Pokemon Agent API.

Este script demonstra como usar todas as funcionalidades da API.
"""

import requests
import json
import time
import sys


class PokemonAPIDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def check_api_health(self):
        """Verifica se a API está funcionando."""
        print("🔍 Verificando saúde da API...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API está funcionando!")
                return True
            else:
                print(f"❌ API retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar com a API: {e}")
            return False
    
    def check_services_health(self):
        """Verifica a saúde dos serviços."""
        print("\n🔍 Verificando saúde dos serviços...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Status geral: {health_data['overall_status']}")
                print(f"📊 Agnos: {health_data['agnos']['agnos_status']}")
                print(f"🐛 Pokemon MCP: {health_data['agnos']['pokemon_mcp']}")
                print(f"🗄️  MongoDB MCP: {health_data['agnos']['mongodb_mcp']}")
                print(f"💾 Database: {health_data['database']['status']}")
                print(f"📈 Pokémons no banco: {health_data['database']['pokemon_count']}")
                return True
            else:
                print(f"❌ Health check falhou: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro no health check: {e}")
            return False
    
    def import_pokemon(self, name):
        """Importa um pokémon."""
        print(f"\n📥 Importando pokémon: {name}")
        try:
            response = requests.get(f"{self.api_url}/import-pokemon", 
                                  params={"name": name}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    pokemon = data["data"]
                    print(f"✅ {pokemon['name'].title()} importado com sucesso!")
                    print(f"   ID: {pokemon['id']}")
                    print(f"   Altura: {pokemon['height']} decímetros")
                    print(f"   Peso: {pokemon['weight']} hectogramas")
                    print(f"   Tipos: {', '.join([t['name'] for t in pokemon['types']])}")
                    return True
                else:
                    print(f"❌ Falha na importação: {data['message']}")
                    return False
            else:
                error_data = response.json()
                print(f"❌ Erro na importação: {error_data.get('detail', 'Erro desconhecido')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def list_pokemons(self):
        """Lista todos os pokémons."""
        print("\n📋 Listando pokémons...")
        try:
            response = requests.get(f"{self.api_url}/pokemons", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    pokemons = data["data"]
                    total = data["total"]
                    print(f"✅ Encontrados {total} pokémons:")
                    
                    for pokemon in pokemons:
                        types_str = ", ".join([t['name'] for t in pokemon['types']])
                        print(f"   • {pokemon['name'].title()} (ID: {pokemon['id']}) - Tipos: {types_str}")
                    
                    return pokemons
                else:
                    print(f"❌ Falha na listagem: {data['message']}")
                    return []
            else:
                print(f"❌ Erro na listagem: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return []
    
    def get_pokemon(self, name):
        """Busca um pokémon específico."""
        print(f"\n🔍 Buscando pokémon: {name}")
        try:
            response = requests.get(f"{self.api_url}/pokemons/{name}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    pokemon = data["data"]
                    print(f"✅ {pokemon['name'].title()} encontrado!")
                    print(f"   ID: {pokemon['id']}")
                    print(f"   Altura: {pokemon['height']} decímetros")
                    print(f"   Peso: {pokemon['weight']} hectogramas")
                    print(f"   Experiência base: {pokemon['base_experience']}")
                    print(f"   Tipos: {', '.join([t['name'] for t in pokemon['types']])}")
                    
                    # Mostrar stats
                    stats = pokemon['stats']
                    print("   📊 Stats:")
                    print(f"      HP: {stats['hp']}")
                    print(f"      Ataque: {stats['attack']}")
                    print(f"      Defesa: {stats['defense']}")
                    print(f"      Ataque Especial: {stats['special-attack']}")
                    print(f"      Defesa Especial: {stats['special-defense']}")
                    print(f"      Velocidade: {stats['speed']}")
                    
                    return pokemon
                else:
                    print(f"❌ Falha na busca: {data['message']}")
                    return None
            elif response.status_code == 404:
                print(f"❌ Pokémon '{name}' não encontrado no banco de dados")
                return None
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    def run_demo(self):
        """Executa a demonstração completa."""
        print("🚀 Iniciando demonstração da Pokemon Agent API")
        print("=" * 50)
        
        # Verificar saúde da API
        if not self.check_api_health():
            print("\n❌ API não está disponível. Verifique se a aplicação está rodando.")
            sys.exit(1)
        
        # Verificar saúde dos serviços
        self.check_services_health()
        
        # Lista de pokémons para demonstração
        demo_pokemons = ["pikachu", "charizard", "blastoise", "venusaur"]
        
        # Importar pokémons
        print("\n" + "=" * 50)
        print("📥 IMPORTANDO POKÉMONS")
        print("=" * 50)
        
        for pokemon_name in demo_pokemons:
            self.import_pokemon(pokemon_name)
            time.sleep(1)  # Pequena pausa entre importações
        
        # Listar todos os pokémons
        print("\n" + "=" * 50)
        print("📋 LISTANDO POKÉMONS")
        print("=" * 50)
        
        pokemons = self.list_pokemons()
        
        # Buscar pokémons específicos
        print("\n" + "=" * 50)
        print("🔍 BUSCANDO POKÉMONS ESPECÍFICOS")
        print("=" * 50)
        
        if pokemons:
            # Buscar os dois primeiros pokémons da lista
            for pokemon in pokemons[:2]:
                self.get_pokemon(pokemon['name'])
                time.sleep(1)
        
        # Tentar buscar um pokémon que não existe
        print("\n🔍 Testando busca de pokémon inexistente...")
        self.get_pokemon("pokemon_inexistente")
        
        print("\n" + "=" * 50)
        print("✅ Demonstração concluída!")
        print("=" * 50)
        print("\n📖 Para mais informações, acesse:")
        print(f"   • Documentação da API: {self.base_url}/docs")
        print(f"   • Health Check: {self.base_url}/health")
        print(f"   • Health Check Detalhado: {self.api_url}/health")


if __name__ == "__main__":
    demo = PokemonAPIDemo()
    demo.run_demo()
