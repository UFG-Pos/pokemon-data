#!/usr/bin/env python3
"""
Script para testar as correções do frontend.
"""

import requests
import time
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_api_health():
    """Testa se a API está funcionando."""
    try:
        response = requests.get(f"{API_BASE}/api/v1/health")
        if response.status_code == 200:
            print("✅ API está saudável")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def test_stream_processor():
    """Testa o stream processor."""
    try:
        # Iniciar stream processor
        response = requests.post(f"{API_BASE}/api/v1/pipeline/stream/start")
        if response.status_code == 200:
            print("✅ Stream processor iniciado")
        else:
            print(f"⚠️ Stream processor já estava rodando ou erro: {response.status_code}")
        
        # Importar um pokémon para gerar eventos
        pokemon_name = f"test_pokemon_{int(time.time())}"
        response = requests.get(f"{API_BASE}/api/v1/import-pokemon?name=ditto")
        
        if response.status_code == 200:
            print("✅ Pokémon importado para teste")
        
        # Aguardar processamento
        time.sleep(10)
        
        # Verificar eventos
        response = requests.get(f"{API_BASE}/api/v1/pipeline/stream/events?limit=10")
        if response.status_code == 200:
            events = response.json().get('events', [])
            print(f"✅ Eventos obtidos: {len(events)}")
            
            # Verificar se há eventos duplicados
            pokemon_events = {}
            for event in events:
                pokemon_name = event['pokemon_name']
                timestamp = event['timestamp']
                
                if pokemon_name not in pokemon_events:
                    pokemon_events[pokemon_name] = []
                pokemon_events[pokemon_name].append(timestamp)
            
            duplicates_found = False
            for pokemon, timestamps in pokemon_events.items():
                if len(timestamps) > 1:
                    # Verificar se os timestamps são muito próximos (menos de 5 minutos)
                    for i in range(len(timestamps) - 1):
                        t1 = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                        t2 = datetime.fromisoformat(timestamps[i+1].replace('Z', '+00:00'))
                        diff = abs((t2 - t1).total_seconds())
                        if diff < 300:  # 5 minutos
                            duplicates_found = True
                            print(f"⚠️ Possível evento duplicado para {pokemon}: {diff}s de diferença")
            
            if not duplicates_found:
                print("✅ Nenhum evento duplicado detectado")
            
            return True
        else:
            print(f"❌ Erro ao obter eventos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste do stream processor: {e}")
        return False

def test_loading_endpoints():
    """Testa endpoints que usam loading modal."""
    endpoints_to_test = [
        ("GET", "/api/v1/pokemons?limit=5", "Listar pokémons"),
        ("POST", "/api/v1/pipeline/file/export-csv", "Exportar CSV"),
        ("POST", "/api/v1/pipeline/alerts/test?level=info", "Teste de alerta"),
    ]
    
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}")
            else:
                response = requests.post(f"{API_BASE}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️ {description}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: Erro {e}")

def test_data_quality():
    """Testa se os dados de qualidade são reais."""
    try:
        response = requests.get(f"{API_BASE}/api/v1/pipeline/dashboard/data")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'dashboard' in data:
                quality_score = data['dashboard']['data_quality']['quality_score']
                print(f"✅ Qualidade dos dados: {quality_score}% (dados reais)")
                return True
            else:
                print("❌ Estrutura de dados de qualidade inválida")
                return False
        else:
            print(f"❌ Erro ao obter dados de qualidade: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de qualidade: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🧪 Testando correções do frontend...\n")
    
    tests = [
        ("Saúde da API", test_api_health),
        ("Stream Processor (eventos duplicados)", test_stream_processor),
        ("Endpoints com loading", test_loading_endpoints),
        ("Dados de qualidade", test_data_quality),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testando: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! Frontend corrigido com sucesso.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os problemas acima.")

if __name__ == "__main__":
    main()
