import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    LOG = "log"
    FILE = "file"
    EMAIL = "email"  # Para implementação futura
    WEBHOOK = "webhook"  # Para implementação futura


class AlertSystem:
    """
    Sistema de alertas para anomalias detectadas no processamento de dados.
    """
    
    def __init__(self):
        self.alerts_dir = Path("data/alerts")
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        
        self.alert_history = deque(maxlen=1000)
        self.alert_channels = {
            AlertChannel.LOG: True,
            AlertChannel.FILE: True,
            AlertChannel.EMAIL: False,
            AlertChannel.WEBHOOK: False
        }
        
        self.alert_rules = {
            'rate_limit': {
                'enabled': True,
                'max_alerts_per_minute': 10,
                'window_minutes': 1
            },
            'duplicate_suppression': {
                'enabled': True,
                'window_minutes': 5
            }
        }
        
        self.metrics = {
            'total_alerts': 0,
            'alerts_by_level': {
                AlertLevel.INFO: 0,
                AlertLevel.WARNING: 0,
                AlertLevel.CRITICAL: 0
            },
            'suppressed_alerts': 0,
            'rate_limited_alerts': 0
        }
    
    async def send_alert(
        self, 
        level: str, 
        title: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envia um alerta através dos canais configurados.
        """
        try:
            alert_level = AlertLevel(level)
            
            alert = {
                'id': self._generate_alert_id(),
                'timestamp': datetime.utcnow().isoformat(),
                'level': alert_level,
                'title': title,
                'message': message,
                'details': details or {},
                'channels_sent': []
            }
            
            # Verificar regras de supressão
            if self._should_suppress_alert(alert):
                self.metrics['suppressed_alerts'] += 1
                logger.debug(f"Alerta suprimido: {title}")
                return False
            
            # Verificar rate limiting
            if self._is_rate_limited():
                self.metrics['rate_limited_alerts'] += 1
                logger.debug(f"Alerta limitado por taxa: {title}")
                return False
            
            # Enviar através dos canais habilitados
            success = await self._send_through_channels(alert)
            
            if success:
                self.alert_history.append(alert)
                self.metrics['total_alerts'] += 1
                self.metrics['alerts_by_level'][alert_level] += 1
                logger.info(f"Alerta enviado: {title} [{alert_level}]")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {str(e)}")
            return False
    
    def _generate_alert_id(self) -> str:
        """
        Gera ID único para o alerta.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        return f"alert_{timestamp}"
    
    def _should_suppress_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Verifica se o alerta deve ser suprimido (duplicata recente).
        """
        if not self.alert_rules['duplicate_suppression']['enabled']:
            return False
        
        window_minutes = self.alert_rules['duplicate_suppression']['window_minutes']
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Verificar alertas similares recentes
        for recent_alert in self.alert_history:
            alert_time = datetime.fromisoformat(recent_alert['timestamp'])
            if alert_time >= cutoff_time:
                if (recent_alert['title'] == alert['title'] and 
                    recent_alert['level'] == alert['level']):
                    return True
        
        return False
    
    def _is_rate_limited(self) -> bool:
        """
        Verifica se está sendo limitado por taxa de alertas.
        """
        if not self.alert_rules['rate_limit']['enabled']:
            return False
        
        max_alerts = self.alert_rules['rate_limit']['max_alerts_per_minute']
        window_minutes = self.alert_rules['rate_limit']['window_minutes']
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        # Contar alertas recentes
        recent_count = sum(
            1 for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        )
        
        return recent_count >= max_alerts
    
    async def _send_through_channels(self, alert: Dict[str, Any]) -> bool:
        """
        Envia alerta através dos canais habilitados.
        """
        success = False
        
        # Canal de log
        if self.alert_channels[AlertChannel.LOG]:
            await self._send_to_log(alert)
            alert['channels_sent'].append(AlertChannel.LOG)
            success = True
        
        # Canal de arquivo
        if self.alert_channels[AlertChannel.FILE]:
            await self._send_to_file(alert)
            alert['channels_sent'].append(AlertChannel.FILE)
            success = True
        
        # Canais futuros (email, webhook)
        if self.alert_channels[AlertChannel.EMAIL]:
            # TODO: Implementar envio por email
            pass
        
        if self.alert_channels[AlertChannel.WEBHOOK]:
            # TODO: Implementar envio por webhook
            pass
        
        return success
    
    async def _send_to_log(self, alert: Dict[str, Any]):
        """
        Envia alerta para o log.
        """
        level = alert['level']
        title = alert['title']
        message = alert['message']
        
        if level == AlertLevel.CRITICAL:
            logger.critical(f"🚨 ALERTA CRÍTICO: {title} - {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"⚠️  ALERTA: {title} - {message}")
        else:
            logger.info(f"ℹ️  INFO: {title} - {message}")
    
    async def _send_to_file(self, alert: Dict[str, Any]):
        """
        Salva alerta em arquivo.
        """
        try:
            # Arquivo diário de alertas
            date_str = datetime.utcnow().strftime("%Y%m%d")
            alert_file = self.alerts_dir / f"alerts_{date_str}.jsonl"
            
            # Adicionar ao arquivo (formato JSONL)
            with open(alert_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Erro ao salvar alerta em arquivo: {str(e)}")
    
    async def get_alert_history(
        self, 
        limit: int = 50, 
        level: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna histórico de alertas.
        """
        alerts = list(self.alert_history)
        
        # Filtrar por nível se especificado
        if level:
            alerts = [a for a in alerts if a['level'] == level]
        
        # Filtrar por data se especificado
        if since:
            alerts = [
                a for a in alerts 
                if datetime.fromisoformat(a['timestamp']) >= since
            ]
        
        # Ordenar por timestamp (mais recentes primeiro)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return alerts[:limit]
    
    async def get_alert_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas do sistema de alertas.
        """
        # Calcular métricas adicionais
        recent_alerts = await self.get_alert_history(
            limit=1000, 
            since=datetime.utcnow() - timedelta(hours=24)
        )
        
        hourly_distribution = {}
        for alert in recent_alerts:
            hour = datetime.fromisoformat(alert['timestamp']).hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        return {
            'total_alerts': self.metrics['total_alerts'],
            'alerts_by_level': dict(self.metrics['alerts_by_level']),
            'suppressed_alerts': self.metrics['suppressed_alerts'],
            'rate_limited_alerts': self.metrics['rate_limited_alerts'],
            'recent_24h': len(recent_alerts),
            'hourly_distribution_24h': hourly_distribution,
            'alert_channels': dict(self.alert_channels),
            'alert_rules': self.alert_rules.copy(),
            'buffer_usage': f"{len(self.alert_history)}/{self.alert_history.maxlen}"
        }
    
    async def configure_channel(self, channel: str, enabled: bool) -> bool:
        """
        Configura canal de alerta.
        """
        try:
            channel_enum = AlertChannel(channel)
            self.alert_channels[channel_enum] = enabled
            logger.info(f"Canal {channel} {'habilitado' if enabled else 'desabilitado'}")
            return True
        except ValueError:
            logger.error(f"Canal inválido: {channel}")
            return False
    
    async def configure_rule(self, rule_name: str, config: Dict[str, Any]) -> bool:
        """
        Configura regra de alerta.
        """
        if rule_name in self.alert_rules:
            self.alert_rules[rule_name].update(config)
            logger.info(f"Regra {rule_name} atualizada: {config}")
            return True
        else:
            logger.error(f"Regra inválida: {rule_name}")
            return False
    
    async def test_alert(self, level: str = "info") -> Dict[str, Any]:
        """
        Envia alerta de teste.
        """
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        
        success = await self.send_alert(
            level=level,
            title=f"Teste de Alerta - {timestamp}",
            message=f"Este é um alerta de teste enviado em {timestamp}",
            details={
                'test': True,
                'timestamp': timestamp,
                'level': level
            }
        )
        
        return {
            'success': success,
            'message': f"Alerta de teste {'enviado' if success else 'falhou'}",
            'level': level,
            'timestamp': timestamp
        }
    
    async def clear_alert_history(self) -> int:
        """
        Limpa histórico de alertas.
        """
        count = len(self.alert_history)
        self.alert_history.clear()
        
        # Reset métricas
        self.metrics = {
            'total_alerts': 0,
            'alerts_by_level': {
                AlertLevel.INFO: 0,
                AlertLevel.WARNING: 0,
                AlertLevel.CRITICAL: 0
            },
            'suppressed_alerts': 0,
            'rate_limited_alerts': 0
        }
        
        logger.info(f"Histórico de alertas limpo: {count} alertas removidos")
        return count
    
    async def export_alerts(self, filename: Optional[str] = None) -> str:
        """
        Exporta histórico de alertas para arquivo.
        """
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"alert_export_{timestamp}.json"
        
        filepath = self.alerts_dir / filename
        
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_alerts': len(self.alert_history),
            'metrics': self.metrics.copy(),
            'alerts': list(self.alert_history)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Alertas exportados para: {filepath}")
        return str(filepath)
