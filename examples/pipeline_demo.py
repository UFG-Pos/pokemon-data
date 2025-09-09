#!/usr/bin/env python3
"""
Demonstração completa da Pipeline de Processamento de Dados Pokemon.
Este script testa todas as funcionalidades da pipeline implementada.
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000"


class PipelineDemo:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_section(self, title: str):
        """Imprime seção formatada."""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print('='*60)
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso."""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro."""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Imprime informação."""
        print(f"ℹ️  {message}")
    
    async def check_api_health(self):
        """Verifica se a API está funcionando."""
        self.print_section("Verificação de Saúde da API")
        
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.print_success("API está funcionando")
                return True
            else:
                self.print_error(f"API retornou status {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Erro ao conectar com a API: {e}")
            return False
    
    async def import_sample_pokemons(self):
        """Importa pokémons de exemplo."""
        self.print_section("Importação de Pokémons de Exemplo")
        
        sample_pokemons = ["pikachu", "charizard", "blastoise", "venusaur", "alakazam"]
        
        for pokemon_name in sample_pokemons:
            try:
                response = await self.client.get(f"{BASE_URL}/api/v1/import-pokemon?name={pokemon_name}")
                if response.status_code == 200:
                    self.print_success(f"Pokémon {pokemon_name} importado")
                else:
                    self.print_error(f"Erro ao importar {pokemon_name}: {response.status_code}")
            except Exception as e:
                self.print_error(f"Erro ao importar {pokemon_name}: {e}")
        
        # Verificar total de pokémons
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pokemons")
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                self.print_info(f"Total de pokémons no banco: {total}")
                self.results['total_pokemons'] = total
        except Exception as e:
            self.print_error(f"Erro ao verificar total: {e}")
    
    async def test_file_processing(self):
        """Testa funcionalidades de processamento de arquivos."""
        self.print_section("Teste de Processamento de Arquivos")
        
        # Exportar para CSV
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/file/export-csv")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Exportação CSV: {data['filepath']}")
                self.results['csv_export'] = data['filepath']
            else:
                self.print_error(f"Erro na exportação CSV: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro na exportação CSV: {e}")
        
        # Exportar para JSON
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/file/export-json")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Exportação JSON: {data['filepath']}")
                self.results['json_export'] = data['filepath']
            else:
                self.print_error(f"Erro na exportação JSON: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro na exportação JSON: {e}")
        
        # Limpeza de dados
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/file/clean-data")
            if response.status_code == 200:
                data = response.json()
                result = data['result']
                self.print_success(f"Limpeza concluída: {result['processed']} pokémons processados")
                if result['issues_found'] > 0:
                    self.print_info(f"Problemas encontrados: {result['issues_found']}")
            else:
                self.print_error(f"Erro na limpeza: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro na limpeza: {e}")
        
        # Gerar agregações
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/file/aggregations")
            if response.status_code == 200:
                data = response.json()
                agg = data['aggregations']
                self.print_success("Agregações geradas:")
                self.print_info(f"  - Total de pokémons: {agg['total_pokemons']}")
                self.print_info(f"  - Tipos mais comuns: {list(agg['type_distribution'].keys())[:3]}")
                self.print_info(f"  - Pokémon mais forte: {agg['top_attack'][0]['name'] if agg['top_attack'] else 'N/A'}")
            else:
                self.print_error(f"Erro nas agregações: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro nas agregações: {e}")
        
        # Gerar relatório
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/file/generate-report?report_type=summary")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Relatório gerado: {data['filepath']}")
                self.results['report_file'] = data['filepath']
            else:
                self.print_error(f"Erro no relatório: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro no relatório: {e}")
    
    async def test_stream_processing(self):
        """Testa processamento em tempo real."""
        self.print_section("Teste de Stream Processing")
        
        # Verificar status inicial
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/stream/status")
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                self.print_info(f"Stream processor rodando: {status['is_running']}")
            else:
                self.print_error(f"Erro ao verificar status: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro ao verificar status: {e}")
        
        # Iniciar stream processor
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/stream/start")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.print_success("Stream processor iniciado")
                else:
                    self.print_info(data['message'])
            else:
                self.print_error(f"Erro ao iniciar stream: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro ao iniciar stream: {e}")
        
        # Aguardar um pouco para processamento
        self.print_info("Aguardando processamento por 10 segundos...")
        await asyncio.sleep(10)
        
        # Verificar eventos
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/stream/events?limit=5")
            if response.status_code == 200:
                data = response.json()
                events = data['events']
                self.print_success(f"Eventos capturados: {len(events)}")
                for event in events[-3:]:  # Últimos 3 eventos
                    self.print_info(f"  - {event['pokemon_name']}: {event['anomalies_count']} anomalias")
            else:
                self.print_error(f"Erro ao obter eventos: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro ao obter eventos: {e}")
        
        # Simular anomalia
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/v1/pipeline/stream/simulate-anomaly?pokemon_name=pikachu&anomaly_type=negative_stats"
            )
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.print_success("Anomalia simulada com sucesso")
                else:
                    self.print_error(f"Erro na simulação: {data['result']}")
            else:
                self.print_error(f"Erro ao simular anomalia: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro ao simular anomalia: {e}")
        
        # Parar stream processor
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/stream/stop")
            if response.status_code == 200:
                self.print_success("Stream processor parado")
            else:
                self.print_error(f"Erro ao parar stream: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro ao parar stream: {e}")
    
    async def test_dashboard(self):
        """Testa funcionalidades do dashboard."""
        self.print_section("Teste de Dashboard")
        
        # Obter dados do dashboard
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/dashboard/data?refresh_cache=true")
            if response.status_code == 200:
                data = response.json()
                dashboard = data['dashboard']
                summary = dashboard['summary']
                
                self.print_success("Dashboard gerado com sucesso:")
                self.print_info(f"  - Total de pokémons: {summary['total_pokemons']}")
                self.print_info(f"  - Tipos únicos: {summary['unique_types']}")
                self.print_info(f"  - Experiência média: {summary['average_base_experience']}")
                
                # Qualidade dos dados
                quality = dashboard['data_quality']
                self.print_info(f"  - Score de qualidade: {quality['quality_score']}%")
                
                self.results['dashboard_data'] = dashboard
            else:
                self.print_error(f"Erro no dashboard: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro no dashboard: {e}")
        
        # Gerar relatório programado
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/dashboard/report?report_type=daily")
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Relatório diário gerado: {data['filepath']}")
                self.results['daily_report'] = data['filepath']
            else:
                self.print_error(f"Erro no relatório diário: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro no relatório diário: {e}")
    
    async def test_alerts(self):
        """Testa sistema de alertas."""
        self.print_section("Teste de Sistema de Alertas")
        
        # Enviar alerta de teste
        try:
            response = await self.client.post(f"{BASE_URL}/api/v1/pipeline/alerts/test?level=info")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.print_success("Alerta de teste enviado")
                else:
                    self.print_error("Falha no alerta de teste")
            else:
                self.print_error(f"Erro no teste de alerta: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro no teste de alerta: {e}")
        
        # Obter métricas de alertas
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/alerts/metrics")
            if response.status_code == 200:
                data = response.json()
                metrics = data['metrics']
                self.print_success("Métricas de alertas:")
                self.print_info(f"  - Total de alertas: {metrics['total_alerts']}")
                self.print_info(f"  - Alertas nas últimas 24h: {metrics['recent_24h']}")
                self.print_info(f"  - Alertas suprimidos: {metrics['suppressed_alerts']}")
            else:
                self.print_error(f"Erro nas métricas: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro nas métricas: {e}")
        
        # Obter histórico de alertas
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/alerts/history?limit=5")
            if response.status_code == 200:
                data = response.json()
                alerts = data['alerts']
                self.print_success(f"Histórico de alertas: {len(alerts)} alertas recentes")
                for alert in alerts[:3]:  # Primeiros 3
                    self.print_info(f"  - [{alert['level']}] {alert['title']}")
            else:
                self.print_error(f"Erro no histórico: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro no histórico: {e}")
    
    async def test_pipeline_status(self):
        """Testa status geral da pipeline."""
        self.print_section("Status Geral da Pipeline")
        
        try:
            response = await self.client.get(f"{BASE_URL}/api/v1/pipeline/status")
            if response.status_code == 200:
                data = response.json()
                pipeline = data['pipeline_status']
                
                self.print_success("Status da Pipeline:")
                
                # Stream processor
                stream = pipeline['stream_processor']
                self.print_info(f"  Stream Processor: {'🟢 Ativo' if stream['is_running'] else '🔴 Inativo'}")
                self.print_info(f"    - Pokémons processados: {stream['metrics']['processed_count']}")
                self.print_info(f"    - Anomalias detectadas: {stream['metrics']['anomalies_detected']}")
                
                # Sistema de alertas
                alerts = pipeline['alert_system']
                self.print_info(f"  Sistema de Alertas: 🟢 Ativo")
                self.print_info(f"    - Total de alertas: {alerts['total_alerts']}")
                
                # Serviços
                services = pipeline['services']
                self.print_info(f"  Serviços:")
                for service, status in services.items():
                    self.print_info(f"    - {service}: {'🟢' if status in ['available', 'connected'] else '🔴'} {status}")
                
            else:
                self.print_error(f"Erro no status: {response.status_code}")
        except Exception as e:
            self.print_error(f"Erro no status: {e}")
    
    async def print_summary(self):
        """Imprime resumo dos resultados."""
        self.print_section("Resumo da Demonstração")
        
        self.print_success("🎉 Demonstração da Pipeline Concluída!")
        self.print_info("\n📊 Resultados:")
        
        if 'total_pokemons' in self.results:
            self.print_info(f"  - Pokémons no banco: {self.results['total_pokemons']}")
        
        if 'csv_export' in self.results:
            self.print_info(f"  - Exportação CSV: ✅")
        
        if 'json_export' in self.results:
            self.print_info(f"  - Exportação JSON: ✅")
        
        if 'report_file' in self.results:
            self.print_info(f"  - Relatório gerado: ✅")
        
        if 'daily_report' in self.results:
            self.print_info(f"  - Relatório diário: ✅")
        
        self.print_info("\n🔧 Funcionalidades testadas:")
        self.print_info("  ✅ Processamento de arquivos (CSV/JSON)")
        self.print_info("  ✅ Limpeza e normalização de dados")
        self.print_info("  ✅ Agregações e estatísticas")
        self.print_info("  ✅ Stream processing em tempo real")
        self.print_info("  ✅ Detecção de anomalias")
        self.print_info("  ✅ Sistema de alertas")
        self.print_info("  ✅ Dashboard e relatórios")
        self.print_info("  ✅ Relatórios programados")
        
        self.print_info("\n🌐 Acesse o dashboard em: http://localhost:8000/docs")
        self.print_info("📁 Arquivos gerados em: ./data/")
    
    async def run_demo(self):
        """Executa demonstração completa."""
        print("🚀 Iniciando Demonstração da Pipeline Pokemon")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar API
        if not await self.check_api_health():
            self.print_error("API não está disponível. Certifique-se de que está rodando.")
            return
        
        # Executar testes
        await self.import_sample_pokemons()
        await self.test_file_processing()
        await self.test_stream_processing()
        await self.test_dashboard()
        await self.test_alerts()
        await self.test_pipeline_status()
        
        # Resumo
        await self.print_summary()


async def main():
    """Função principal."""
    async with PipelineDemo() as demo:
        await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
