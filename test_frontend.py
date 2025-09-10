#!/usr/bin/env python3
"""
Script para testar o frontend e verificar se os dados são reais
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_api_endpoint(endpoint, method="GET", data=None):
    """Testa um endpoint da API"""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_BASE}{endpoint}", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro {response.status_code} em {endpoint}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão em {endpoint}: {e}")
        return None

def main():
    print("🧪 Testando Frontend e Dados Reais")
    print("=" * 50)
    
    # 1. Teste de saúde
    print("\n1. 🏥 Teste de Saúde")
    health = test_api_endpoint("/health")
    if health:
        print(f"✅ API saudável: {health}")
    
    # 2. Importar um pokémon para teste
    print("\n2. 🎮 Importando Pokémon de Teste")
    import_result = test_api_endpoint("/api/v1/import-pokemon?name=ditto")
    if import_result and import_result.get('success'):
        print(f"✅ Pokémon importado: {import_result['data']['name']}")
    
    # 3. Verificar lista de pokémons
    print("\n3. 📋 Verificando Lista de Pokémons")
    pokemon_list = test_api_endpoint("/api/v1/pokemons?limit=5")
    if pokemon_list and pokemon_list.get('success'):
        print(f"✅ Total de pokémons: {pokemon_list['total']}")
        for pokemon in pokemon_list['data'][:3]:
            print(f"   - {pokemon['name']} (ID: {pokemon['id']})")
    
    # 4. Teste de status da pipeline
    print("\n4. ⚙️ Status da Pipeline")
    pipeline_status = test_api_endpoint("/api/v1/pipeline/status")
    if pipeline_status:
        status = pipeline_status['pipeline_status']
        stream_running = status['stream_processor']['is_running']
        total_alerts = status['alert_system']['total_alerts']
        print(f"✅ Stream Processor: {'🟢 Ativo' if stream_running else '🔴 Inativo'}")
        print(f"✅ Total de Alertas: {total_alerts}")
    
    # 5. Teste de dados do dashboard
    print("\n5. 📊 Dados do Dashboard")
    dashboard_data = test_api_endpoint("/api/v1/pipeline/dashboard/data")
    if dashboard_data:
        data = dashboard_data['dashboard']
        quality_score = data['data_quality']['quality_score']
        total_pokemons = data['summary']['total_pokemons']
        unique_types = data['summary']['unique_types']
        print(f"✅ Qualidade dos Dados: {quality_score}%")
        print(f"✅ Total de Pokémons: {total_pokemons}")
        print(f"✅ Tipos Únicos: {unique_types}")
        
        # Verificar se os dados são reais (não mockados)
        if total_pokemons > 0 and quality_score > 0:
            print("✅ Dados são REAIS (não mockados)")
        else:
            print("⚠️ Dados podem estar mockados")
    
    # 6. Teste de exportação
    print("\n6. 📁 Teste de Exportação")
    export_result = test_api_endpoint("/api/v1/pipeline/file/export-csv", method="POST")
    if export_result and export_result.get('success'):
        print(f"✅ CSV exportado: {export_result['filepath']}")
    
    # 7. Teste de eventos
    print("\n7. 📝 Eventos Recentes")
    events = test_api_endpoint("/api/v1/pipeline/stream/events?limit=3")
    if events:
        event_count = len(events.get('events', []))
        print(f"✅ Eventos encontrados: {event_count}")
        for event in events.get('events', [])[:2]:
            timestamp = event.get('timestamp', 'N/A')
            pokemon_name = event.get('pokemon_name', 'N/A')
            print(f"   - {pokemon_name} em {timestamp}")
    
    # 8. Teste de alertas
    print("\n8. 🚨 Sistema de Alertas")
    alert_test = test_api_endpoint("/api/v1/pipeline/alerts/test?level=info", method="POST")
    if alert_test and alert_test.get('success'):
        print("✅ Alerta de teste enviado")
    
    alerts_history = test_api_endpoint("/api/v1/pipeline/alerts/history?limit=3")
    if alerts_history:
        alert_count = len(alerts_history.get('alerts', []))
        print(f"✅ Alertas no histórico: {alert_count}")
    
    # 9. Verificar arquivos gerados
    print("\n9. 📂 Verificando Arquivos Gerados")
    import os
    data_dir = "./data"
    if os.path.exists(data_dir):
        for subdir in ['exports', 'reports', 'dashboards', 'alerts']:
            subdir_path = os.path.join(data_dir, subdir)
            if os.path.exists(subdir_path):
                files = os.listdir(subdir_path)
                print(f"✅ {subdir}: {len(files)} arquivos")
            else:
                print(f"⚠️ {subdir}: diretório não encontrado")
    else:
        print("❌ Diretório data/ não encontrado")
    
    print("\n" + "=" * 50)
    print("🎉 Teste do Frontend Concluído!")
    print("\n💡 Acesse o dashboard em: http://localhost:8000")
    print("📚 Documentação da API: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
