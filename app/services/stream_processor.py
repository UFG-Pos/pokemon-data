import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import json
from pathlib import Path

from app.models.pokemon import Pokemon
from app.services.database import DatabaseService
from app.services.alert_system import AlertSystem

logger = logging.getLogger(__name__)


class StreamProcessorMCP:
    """
    MCP Stream Processor para processamento em tempo real dos dados de pokémons.
    Detecta anomalias e dispara alertas automáticos.
    """
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.alert_system = AlertSystem()
        self.is_running = False
        self.processing_interval = 5  # segundos
        self.anomaly_rules = self._initialize_anomaly_rules()
        self.recent_events = deque(maxlen=1000)  # Buffer para eventos recentes
        self.processed_pokemons = {}  # Cache para evitar processamento duplicado
        self.cache_duration = 300  # 5 minutos em segundos
        self.metrics = {
            'processed_count': 0,
            'anomalies_detected': 0,
            'alerts_sent': 0,
            'last_processed': None,
            'start_time': None
        }
        
        # Configurações de anomalias
        self.stat_thresholds = {
            'hp': {'min': 1, 'max': 255},
            'attack': {'min': 1, 'max': 255},
            'defense': {'min': 1, 'max': 255},
            'special_attack': {'min': 1, 'max': 255},
            'special_defense': {'min': 1, 'max': 255},
            'speed': {'min': 1, 'max': 255}
        }
        
        self.valid_types = {
            'normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting',
            'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost',
            'dragon', 'dark', 'steel', 'fairy'
        }
    
    def _initialize_anomaly_rules(self) -> List[Dict[str, Any]]:
        """
        Inicializa regras de detecção de anomalias.
        """
        return [
            {
                'name': 'negative_stats',
                'description': 'Detecta stats negativos',
                'severity': 'high',
                'enabled': True
            },
            {
                'name': 'invalid_types',
                'description': 'Detecta tipos inexistentes',
                'severity': 'medium',
                'enabled': True
            },
            {
                'name': 'extreme_stats',
                'description': 'Detecta stats extremamente altos ou baixos',
                'severity': 'medium',
                'enabled': True
            },
            {
                'name': 'duplicate_pokemon',
                'description': 'Detecta pokémons duplicados',
                'severity': 'low',
                'enabled': True
            },
            {
                'name': 'missing_data',
                'description': 'Detecta dados obrigatórios ausentes',
                'severity': 'high',
                'enabled': True
            }
        ]

    def _clean_processed_cache(self):
        """
        Remove entradas antigas do cache de pokémons processados.
        """
        current_time = datetime.utcnow()
        expired_keys = []

        for pokemon_id, last_processed in self.processed_pokemons.items():
            if (current_time - last_processed).total_seconds() > self.cache_duration:
                expired_keys.append(pokemon_id)

        for key in expired_keys:
            del self.processed_pokemons[key]

    def _should_process_pokemon(self, pokemon: Pokemon) -> bool:
        """
        Verifica se um pokémon deve ser processado baseado no cache.
        """
        current_time = datetime.utcnow()
        last_processed = self.processed_pokemons.get(pokemon.id)

        if last_processed is None:
            return True

        # Só processa novamente se passou mais de 5 minutos
        time_since_last = (current_time - last_processed).total_seconds()
        return time_since_last > self.cache_duration

    async def start_stream_processing(self):
        """
        Inicia o processamento em tempo real.
        """
        if self.is_running:
            logger.warning("Stream processor já está rodando")
            return
        
        self.is_running = True
        self.metrics['start_time'] = datetime.utcnow()
        logger.info("Iniciando stream processor")
        
        try:
            while self.is_running:
                await self._process_stream_batch()
                await asyncio.sleep(self.processing_interval)
        except Exception as e:
            logger.error(f"Erro no stream processor: {str(e)}")
            self.is_running = False
            raise
    
    async def stop_stream_processing(self):
        """
        Para o processamento em tempo real.
        """
        self.is_running = False
        logger.info("Stream processor parado")
    
    async def _process_stream_batch(self):
        """
        Processa um lote de dados em tempo real.
        """
        try:
            # Limpar cache de pokémons processados
            self._clean_processed_cache()

            # Buscar pokémons modificados recentemente (últimos 5 minutos)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)

            # Simular stream - na prática, isso viria de um sistema de streaming real
            recent_pokemons = await self._get_recent_pokemons(cutoff_time)

            if not recent_pokemons:
                return

            # Filtrar pokémons que já foram processados recentemente
            pokemons_to_process = [
                pokemon for pokemon in recent_pokemons
                if self._should_process_pokemon(pokemon)
            ]

            if not pokemons_to_process:
                logger.debug("Nenhum pokémon novo para processar")
                return

            logger.info(f"Processando {len(pokemons_to_process)} pokémons no stream (de {len(recent_pokemons)} candidatos)")

            for pokemon in pokemons_to_process:
                await self._process_pokemon_stream(pokemon)
                self.metrics['processed_count'] += 1
                # Marcar como processado
                self.processed_pokemons[pokemon.id] = datetime.utcnow()

            self.metrics['last_processed'] = datetime.utcnow()

        except Exception as e:
            logger.error(f"Erro no processamento do lote: {str(e)}")
    
    async def _get_recent_pokemons(self, cutoff_time: datetime) -> List[Pokemon]:
        """
        Busca pokémons modificados recentemente.
        """
        try:
            # Por simplicidade, vamos buscar todos e filtrar
            # Em um sistema real, isso seria uma query otimizada
            pokemons, _ = await self.db_service.list_pokemons(skip=0, limit=1000)
            
            recent_pokemons = [
                pokemon for pokemon in pokemons 
                if pokemon.updated_at >= cutoff_time
            ]
            
            return recent_pokemons
            
        except Exception as e:
            logger.error(f"Erro ao buscar pokémons recentes: {str(e)}")
            return []
    
    async def _process_pokemon_stream(self, pokemon: Pokemon):
        """
        Processa um pokémon individual no stream.
        """
        try:
            anomalies = await self._detect_anomalies(pokemon)
            
            if anomalies:
                self.metrics['anomalies_detected'] += len(anomalies)
                await self._handle_anomalies(pokemon, anomalies)
            
            # Registrar evento
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'pokemon_id': pokemon.id,
                'pokemon_name': pokemon.name,
                'anomalies_count': len(anomalies),
                'anomalies': anomalies
            }
            
            self.recent_events.append(event)
            
        except Exception as e:
            logger.error(f"Erro ao processar pokémon {pokemon.name}: {str(e)}")
    
    async def _detect_anomalies(self, pokemon: Pokemon) -> List[Dict[str, Any]]:
        """
        Detecta anomalias em um pokémon.
        """
        anomalies = []
        
        # Verificar stats negativos
        if self._is_rule_enabled('negative_stats'):
            negative_stats = self._check_negative_stats(pokemon)
            if negative_stats:
                anomalies.append({
                    'rule': 'negative_stats',
                    'severity': 'high',
                    'description': f"Stats negativos detectados: {negative_stats}",
                    'details': negative_stats
                })
        
        # Verificar tipos inválidos
        if self._is_rule_enabled('invalid_types'):
            invalid_types = self._check_invalid_types(pokemon)
            if invalid_types:
                anomalies.append({
                    'rule': 'invalid_types',
                    'severity': 'medium',
                    'description': f"Tipos inválidos detectados: {invalid_types}",
                    'details': invalid_types
                })
        
        # Verificar stats extremos
        if self._is_rule_enabled('extreme_stats'):
            extreme_stats = self._check_extreme_stats(pokemon)
            if extreme_stats:
                anomalies.append({
                    'rule': 'extreme_stats',
                    'severity': 'medium',
                    'description': f"Stats extremos detectados: {extreme_stats}",
                    'details': extreme_stats
                })
        
        # Verificar dados ausentes
        if self._is_rule_enabled('missing_data'):
            missing_data = self._check_missing_data(pokemon)
            if missing_data:
                anomalies.append({
                    'rule': 'missing_data',
                    'severity': 'high',
                    'description': f"Dados obrigatórios ausentes: {missing_data}",
                    'details': missing_data
                })
        
        return anomalies
    
    def _is_rule_enabled(self, rule_name: str) -> bool:
        """
        Verifica se uma regra está habilitada.
        """
        for rule in self.anomaly_rules:
            if rule['name'] == rule_name:
                return rule['enabled']
        return False
    
    def _check_negative_stats(self, pokemon: Pokemon) -> List[str]:
        """
        Verifica stats negativos.
        """
        negative_stats = []
        stats_dict = pokemon.stats.dict()
        
        for stat_name, stat_value in stats_dict.items():
            if stat_value < 0:
                negative_stats.append(f"{stat_name}={stat_value}")
        
        return negative_stats
    
    def _check_invalid_types(self, pokemon: Pokemon) -> List[str]:
        """
        Verifica tipos inválidos.
        """
        invalid_types = []
        
        for pokemon_type in pokemon.types:
            if pokemon_type.name not in self.valid_types:
                invalid_types.append(pokemon_type.name)
        
        return invalid_types
    
    def _check_extreme_stats(self, pokemon: Pokemon) -> List[str]:
        """
        Verifica stats extremos.
        """
        extreme_stats = []
        stats_dict = pokemon.stats.dict()
        
        for stat_name, stat_value in stats_dict.items():
            if stat_name in self.stat_thresholds:
                thresholds = self.stat_thresholds[stat_name]
                if stat_value < thresholds['min'] or stat_value > thresholds['max']:
                    extreme_stats.append(f"{stat_name}={stat_value} (fora do range {thresholds['min']}-{thresholds['max']})")
        
        return extreme_stats
    
    def _check_missing_data(self, pokemon: Pokemon) -> List[str]:
        """
        Verifica dados obrigatórios ausentes.
        """
        missing_data = []
        
        if not pokemon.name or pokemon.name.strip() == '':
            missing_data.append('name')
        
        if pokemon.id <= 0:
            missing_data.append('id')
        
        if not pokemon.types:
            missing_data.append('types')
        
        return missing_data
    
    async def _handle_anomalies(self, pokemon: Pokemon, anomalies: List[Dict[str, Any]]):
        """
        Trata anomalias detectadas.
        """
        try:
            # Agrupar por severidade
            high_severity = [a for a in anomalies if a['severity'] == 'high']
            medium_severity = [a for a in anomalies if a['severity'] == 'medium']
            low_severity = [a for a in anomalies if a['severity'] == 'low']
            
            # Enviar alertas baseados na severidade
            if high_severity:
                await self.alert_system.send_alert(
                    level='critical',
                    title=f"Anomalias críticas detectadas em {pokemon.name}",
                    message=f"Pokémon ID {pokemon.id} ({pokemon.name}) apresenta {len(high_severity)} anomalias críticas",
                    details={'pokemon': pokemon.name, 'anomalies': high_severity}
                )
                self.metrics['alerts_sent'] += 1
            
            if medium_severity:
                await self.alert_system.send_alert(
                    level='warning',
                    title=f"Anomalias detectadas em {pokemon.name}",
                    message=f"Pokémon ID {pokemon.id} ({pokemon.name}) apresenta {len(medium_severity)} anomalias",
                    details={'pokemon': pokemon.name, 'anomalies': medium_severity}
                )
                self.metrics['alerts_sent'] += 1
            
            # Log das anomalias
            logger.warning(f"Anomalias detectadas em {pokemon.name}: {len(anomalies)} total")
            
        except Exception as e:
            logger.error(f"Erro ao tratar anomalias: {str(e)}")
    
    async def get_stream_status(self) -> Dict[str, Any]:
        """
        Retorna status do stream processor.
        """
        uptime = None
        if self.metrics['start_time']:
            uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
        
        return {
            'is_running': self.is_running,
            'processing_interval': self.processing_interval,
            'uptime_seconds': uptime,
            'metrics': self.metrics.copy(),
            'anomaly_rules': self.anomaly_rules.copy(),
            'recent_events_count': len(self.recent_events),
            'buffer_size': self.recent_events.maxlen
        }
    
    async def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna eventos recentes.
        """
        events = list(self.recent_events)
        return events[-limit:] if len(events) > limit else events
    
    async def update_anomaly_rule(self, rule_name: str, enabled: bool) -> bool:
        """
        Atualiza configuração de uma regra de anomalia.
        """
        for rule in self.anomaly_rules:
            if rule['name'] == rule_name:
                rule['enabled'] = enabled
                logger.info(f"Regra {rule_name} {'habilitada' if enabled else 'desabilitada'}")
                return True
        return False
    
    async def simulate_anomaly(self, pokemon_name: str, anomaly_type: str) -> Dict[str, Any]:
        """
        Simula uma anomalia para testes.
        """
        try:
            pokemon = await self.db_service.get_pokemon_by_name(pokemon_name)
            if not pokemon:
                return {'error': f'Pokémon {pokemon_name} não encontrado'}
            
            # Simular anomalia baseada no tipo
            if anomaly_type == 'negative_stats':
                pokemon.stats.hp = -10
            elif anomaly_type == 'invalid_type':
                pokemon.types.append(type('MockType', (), {'name': 'invalid_type', 'url': ''}))
            elif anomaly_type == 'extreme_stats':
                pokemon.stats.attack = 999
            
            # Processar pokémon com anomalia simulada
            await self._process_pokemon_stream(pokemon)
            
            return {
                'success': True,
                'message': f'Anomalia {anomaly_type} simulada para {pokemon_name}',
                'pokemon': pokemon_name,
                'anomaly_type': anomaly_type
            }
            
        except Exception as e:
            logger.error(f"Erro ao simular anomalia: {str(e)}")
            return {'error': str(e)}
