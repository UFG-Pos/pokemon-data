import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import base64
from collections import Counter

from app.services.database import DatabaseService
from app.services.file_processor import FileProcessorMCP
from app.services.stream_processor import StreamProcessorMCP
from app.services.alert_system import AlertSystem

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Serviço para geração de dashboards e relatórios visuais.
    """
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.file_processor = FileProcessorMCP(db_service)
        self.reports_dir = Path("data/dashboards")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache para dados do dashboard
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.last_cache_update = {}
    
    async def get_dashboard_data(self, refresh_cache: bool = False) -> Dict[str, Any]:
        """
        Retorna dados completos para o dashboard principal.
        """
        try:
            cache_key = "main_dashboard"
            
            # Verificar cache
            if not refresh_cache and self._is_cache_valid(cache_key):
                logger.info("Retornando dados do dashboard do cache")
                return self.cache[cache_key]
            
            logger.info("Gerando dados do dashboard")
            
            # Buscar dados básicos
            pokemons, total = await self.db_service.list_pokemons(skip=0, limit=10000)
            
            if not pokemons:
                return {"error": "Nenhum pokémon encontrado"}
            
            # Gerar estatísticas
            dashboard_data = {
                "summary": await self._generate_summary_stats(pokemons, total),
                "type_analysis": await self._generate_type_analysis(pokemons),
                "stats_analysis": await self._generate_stats_analysis(pokemons),
                "top_rankings": await self._generate_top_rankings(pokemons),
                "recent_activity": await self._generate_recent_activity(pokemons),
                "data_quality": await self._generate_data_quality_metrics(pokemons),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Atualizar cache
            self.cache[cache_key] = dashboard_data
            self.last_cache_update[cache_key] = datetime.utcnow()
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados do dashboard: {str(e)}")
            raise
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Verifica se o cache ainda é válido.
        """
        if cache_key not in self.cache or cache_key not in self.last_cache_update:
            return False
        
        cache_age = (datetime.utcnow() - self.last_cache_update[cache_key]).total_seconds()
        return cache_age < self.cache_ttl
    
    async def _generate_summary_stats(self, pokemons: List, total: int) -> Dict[str, Any]:
        """
        Gera estatísticas resumidas.
        """
        # Contagem por geração (baseado no ID)
        generation_counts = {
            "Gen 1 (1-151)": len([p for p in pokemons if 1 <= p.id <= 151]),
            "Gen 2 (152-251)": len([p for p in pokemons if 152 <= p.id <= 251]),
            "Gen 3 (252-386)": len([p for p in pokemons if 252 <= p.id <= 386]),
            "Gen 4 (387-493)": len([p for p in pokemons if 387 <= p.id <= 493]),
            "Gen 5 (494-649)": len([p for p in pokemons if 494 <= p.id <= 649]),
            "Outros": len([p for p in pokemons if p.id > 649 or p.id < 1])
        }
        
        # Estatísticas de experiência
        exp_values = [p.base_experience for p in pokemons if p.base_experience is not None]
        avg_experience = sum(exp_values) / len(exp_values) if exp_values else 0
        
        # Pokémons únicos por tipo
        unique_types = set()
        for pokemon in pokemons:
            for ptype in pokemon.types:
                unique_types.add(ptype.name)
        
        return {
            "total_pokemons": total,
            "unique_types": len(unique_types),
            "generation_distribution": generation_counts,
            "average_base_experience": round(avg_experience, 2),
            "data_completeness": {
                "with_base_experience": len(exp_values),
                "without_base_experience": total - len(exp_values)
            }
        }
    
    async def _generate_type_analysis(self, pokemons: List) -> Dict[str, Any]:
        """
        Gera análise detalhada por tipos.
        """
        type_stats = {}
        type_combinations = Counter()
        
        for pokemon in pokemons:
            # Combinações de tipos
            type_names = [t.name for t in pokemon.types]
            type_combo = " / ".join(sorted(type_names))
            type_combinations[type_combo] += 1
            
            # Estatísticas por tipo individual
            for ptype in pokemon.types:
                type_name = ptype.name
                if type_name not in type_stats:
                    type_stats[type_name] = {
                        'count': 0,
                        'total_stats': {'hp': 0, 'attack': 0, 'defense': 0, 'special_attack': 0, 'special_defense': 0, 'speed': 0},
                        'pokemons': []
                    }
                
                type_stats[type_name]['count'] += 1
                type_stats[type_name]['pokemons'].append({
                    'name': pokemon.name,
                    'id': pokemon.id
                })
                
                # Somar stats
                stats_dict = pokemon.stats.dict()
                for stat_name, stat_value in stats_dict.items():
                    if stat_name in type_stats[type_name]['total_stats']:
                        type_stats[type_name]['total_stats'][stat_name] += stat_value
        
        # Calcular médias
        for type_name, data in type_stats.items():
            count = data['count']
            data['avg_stats'] = {
                stat: round(total / count, 2)
                for stat, total in data['total_stats'].items()
            }
            del data['total_stats']  # Remover para economizar espaço
            
            # Manter apenas top 5 pokémons por tipo
            data['pokemons'] = data['pokemons'][:5]
        
        return {
            "type_distribution": dict(Counter(type_stats.keys())),
            "type_combinations": dict(type_combinations.most_common(10)),
            "type_stats": type_stats,
            "most_common_type": max(type_stats.items(), key=lambda x: x[1]['count'])[0] if type_stats else None,
            "rarest_types": [name for name, data in type_stats.items() if data['count'] == 1]
        }
    
    async def _generate_stats_analysis(self, pokemons: List) -> Dict[str, Any]:
        """
        Gera análise detalhada das estatísticas.
        """
        stats_data = {
            'hp': [p.stats.hp for p in pokemons],
            'attack': [p.stats.attack for p in pokemons],
            'defense': [p.stats.defense for p in pokemons],
            'special_attack': [p.stats.special_attack for p in pokemons],
            'special_defense': [p.stats.special_defense for p in pokemons],
            'speed': [p.stats.speed for p in pokemons]
        }
        
        analysis = {}
        for stat_name, values in stats_data.items():
            sorted_values = sorted(values)
            n = len(values)
            
            analysis[stat_name] = {
                'min': min(values),
                'max': max(values),
                'mean': round(sum(values) / n, 2),
                'median': sorted_values[n // 2],
                'q1': sorted_values[n // 4],
                'q3': sorted_values[3 * n // 4],
                'std_dev': round((sum((x - sum(values)/n) ** 2 for x in values) / n) ** 0.5, 2)
            }
        
        # Calcular total de stats por pokémon
        total_stats = []
        for pokemon in pokemons:
            total = (pokemon.stats.hp + pokemon.stats.attack + pokemon.stats.defense + 
                    pokemon.stats.special_attack + pokemon.stats.special_defense + pokemon.stats.speed)
            total_stats.append({'name': pokemon.name, 'total': total, 'id': pokemon.id})
        
        total_stats.sort(key=lambda x: x['total'], reverse=True)
        
        return {
            'individual_stats': analysis,
            'total_stats_ranking': total_stats[:20],  # Top 20
            'stat_correlations': await self._calculate_stat_correlations(pokemons),
            'stat_distribution_ranges': {
                'very_low': {'min': 0, 'max': 30},
                'low': {'min': 31, 'max': 60},
                'medium': {'min': 61, 'max': 90},
                'high': {'min': 91, 'max': 120},
                'very_high': {'min': 121, 'max': 255}
            }
        }
    
    async def _calculate_stat_correlations(self, pokemons: List) -> Dict[str, float]:
        """
        Calcula correlações simples entre stats.
        """
        # Correlação simples entre ataque e defesa
        attack_values = [p.stats.attack for p in pokemons]
        defense_values = [p.stats.defense for p in pokemons]
        
        # Correlação de Pearson simplificada
        n = len(attack_values)
        if n == 0:
            return {}
        
        mean_attack = sum(attack_values) / n
        mean_defense = sum(defense_values) / n
        
        numerator = sum((attack_values[i] - mean_attack) * (defense_values[i] - mean_defense) for i in range(n))
        denominator = (sum((x - mean_attack) ** 2 for x in attack_values) * 
                      sum((x - mean_defense) ** 2 for x in defense_values)) ** 0.5
        
        attack_defense_corr = numerator / denominator if denominator != 0 else 0
        
        return {
            'attack_defense': round(attack_defense_corr, 3),
            'note': 'Correlação entre -1 (negativa) e 1 (positiva)'
        }
    
    async def _generate_top_rankings(self, pokemons: List) -> Dict[str, Any]:
        """
        Gera rankings dos melhores pokémons.
        """
        rankings = {}
        
        # Top por cada stat
        stats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
        for stat in stats:
            sorted_pokemons = sorted(pokemons, key=lambda p: getattr(p.stats, stat), reverse=True)
            rankings[f'top_{stat}'] = [
                {
                    'name': p.name,
                    'id': p.id,
                    'value': getattr(p.stats, stat),
                    'types': [t.name for t in p.types]
                }
                for p in sorted_pokemons[:10]
            ]
        
        # Top por experiência base
        exp_pokemons = [p for p in pokemons if p.base_experience is not None]
        exp_sorted = sorted(exp_pokemons, key=lambda p: p.base_experience, reverse=True)
        rankings['top_experience'] = [
            {
                'name': p.name,
                'id': p.id,
                'base_experience': p.base_experience,
                'types': [t.name for t in p.types]
            }
            for p in exp_sorted[:10]
        ]
        
        return rankings
    
    async def _generate_recent_activity(self, pokemons: List) -> Dict[str, Any]:
        """
        Gera dados de atividade recente.
        """
        # Pokémons adicionados recentemente (últimas 24h)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_pokemons = [
            p for p in pokemons 
            if p.created_at >= cutoff_time
        ]
        
        # Pokémons atualizados recentemente
        updated_pokemons = [
            p for p in pokemons 
            if p.updated_at >= cutoff_time and p.updated_at != p.created_at
        ]
        
        return {
            'recent_additions': {
                'count': len(recent_pokemons),
                'pokemons': [
                    {
                        'name': p.name,
                        'id': p.id,
                        'created_at': p.created_at.isoformat(),
                        'types': [t.name for t in p.types]
                    }
                    for p in recent_pokemons[:10]
                ]
            },
            'recent_updates': {
                'count': len(updated_pokemons),
                'pokemons': [
                    {
                        'name': p.name,
                        'id': p.id,
                        'updated_at': p.updated_at.isoformat(),
                        'types': [t.name for t in p.types]
                    }
                    for p in updated_pokemons[:10]
                ]
            }
        }
    
    async def _generate_data_quality_metrics(self, pokemons: List) -> Dict[str, Any]:
        """
        Gera métricas de qualidade dos dados.
        """
        total = len(pokemons)
        
        # Verificar completude dos dados
        missing_experience = len([p for p in pokemons if p.base_experience is None])
        missing_types = len([p for p in pokemons if not p.types])
        missing_abilities = len([p for p in pokemons if not p.abilities])
        
        # Verificar anomalias
        negative_stats = 0
        zero_stats = 0
        extreme_stats = 0
        
        for pokemon in pokemons:
            stats_dict = pokemon.stats.dict()
            for stat_value in stats_dict.values():
                if stat_value < 0:
                    negative_stats += 1
                elif stat_value == 0:
                    zero_stats += 1
                elif stat_value > 200:
                    extreme_stats += 1
        
        # Duplicatas (por nome)
        names = [p.name for p in pokemons]
        duplicates = len(names) - len(set(names))
        
        quality_score = max(0, 100 - (
            (missing_experience / total * 10) +
            (missing_types / total * 20) +
            (negative_stats / total * 30) +
            (duplicates / total * 25)
        ))
        
        return {
            'quality_score': round(quality_score, 2),
            'total_records': total,
            'completeness': {
                'missing_experience': missing_experience,
                'missing_types': missing_types,
                'missing_abilities': missing_abilities
            },
            'anomalies': {
                'negative_stats': negative_stats,
                'zero_stats': zero_stats,
                'extreme_stats': extreme_stats,
                'duplicates': duplicates
            },
            'recommendations': await self._generate_quality_recommendations(
                missing_experience, missing_types, negative_stats, duplicates, total
            )
        }
    
    async def _generate_quality_recommendations(
        self, missing_exp: int, missing_types: int, negative_stats: int, duplicates: int, total: int
    ) -> List[str]:
        """
        Gera recomendações para melhorar a qualidade dos dados.
        """
        recommendations = []
        
        if missing_exp / total > 0.1:
            recommendations.append("Considere buscar dados de experiência base para pokémons sem essa informação")
        
        if missing_types / total > 0.05:
            recommendations.append("Verifique pokémons sem tipos definidos - isso pode indicar erro na importação")
        
        if negative_stats > 0:
            recommendations.append("Corrija stats negativos encontrados nos dados")
        
        if duplicates > 0:
            recommendations.append("Remova ou consolide pokémons duplicados")
        
        if not recommendations:
            recommendations.append("Qualidade dos dados está boa! Continue monitorando.")
        
        return recommendations

    async def generate_scheduled_report(self, report_type: str = "daily") -> str:
        """
        Gera relatório programado.
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            if report_type == "daily":
                return await self._generate_daily_report(timestamp)
            elif report_type == "weekly":
                return await self._generate_weekly_report(timestamp)
            elif report_type == "monthly":
                return await self._generate_monthly_report(timestamp)
            else:
                raise ValueError(f"Tipo de relatório não suportado: {report_type}")

        except Exception as e:
            logger.error(f"Erro ao gerar relatório programado: {str(e)}")
            raise

    async def _generate_daily_report(self, timestamp: str) -> str:
        """
        Gera relatório diário.
        """
        dashboard_data = await self.get_dashboard_data(refresh_cache=True)

        # Dados específicos do dia
        today = datetime.utcnow().date()
        cutoff_time = datetime.combine(today, datetime.min.time())

        pokemons, _ = await self.db_service.list_pokemons(skip=0, limit=10000)
        daily_additions = [
            p for p in pokemons
            if p.created_at.date() == today
        ]

        report_data = {
            "report_type": "daily",
            "date": today.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_pokemons": dashboard_data["summary"]["total_pokemons"],
                "daily_additions": len(daily_additions),
                "new_pokemons": [
                    {"name": p.name, "id": p.id, "types": [t.name for t in p.types]}
                    for p in daily_additions
                ]
            },
            "top_stats": {
                "strongest_attack": dashboard_data["top_rankings"]["top_attack"][0] if dashboard_data["top_rankings"]["top_attack"] else None,
                "highest_hp": dashboard_data["top_rankings"]["top_hp"][0] if dashboard_data["top_rankings"]["top_hp"] else None,
                "fastest": dashboard_data["top_rankings"]["top_speed"][0] if dashboard_data["top_rankings"]["top_speed"] else None
            },
            "data_quality": dashboard_data["data_quality"],
            "type_distribution": dashboard_data["type_analysis"]["type_distribution"]
        }

        filename = f"daily_report_{timestamp}.json"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório diário gerado: {filepath}")
        return str(filepath)

    async def _generate_weekly_report(self, timestamp: str) -> str:
        """
        Gera relatório semanal.
        """
        dashboard_data = await self.get_dashboard_data(refresh_cache=True)

        # Dados da semana
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        pokemons, _ = await self.db_service.list_pokemons(skip=0, limit=10000)
        weekly_additions = [
            p for p in pokemons
            if week_start <= p.created_at.date() <= week_end
        ]

        # Análise de tendências
        daily_counts = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            daily_counts[day.isoformat()] = len([
                p for p in weekly_additions
                if p.created_at.date() == day
            ])

        report_data = {
            "report_type": "weekly",
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_pokemons": dashboard_data["summary"]["total_pokemons"],
                "weekly_additions": len(weekly_additions),
                "daily_breakdown": daily_counts,
                "average_daily_additions": round(len(weekly_additions) / 7, 2)
            },
            "trends": {
                "most_active_day": max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None,
                "type_trends": await self._analyze_type_trends(weekly_additions)
            },
            "full_dashboard": dashboard_data
        }

        filename = f"weekly_report_{timestamp}.json"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório semanal gerado: {filepath}")
        return str(filepath)

    async def _generate_monthly_report(self, timestamp: str) -> str:
        """
        Gera relatório mensal.
        """
        dashboard_data = await self.get_dashboard_data(refresh_cache=True)

        # Dados do mês
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        pokemons, _ = await self.db_service.list_pokemons(skip=0, limit=10000)
        monthly_additions = [
            p for p in pokemons
            if month_start <= p.created_at.date() <= month_end
        ]

        # Análise mensal detalhada
        weekly_breakdown = {}
        current_week_start = month_start
        week_num = 1

        while current_week_start <= month_end:
            week_end = min(current_week_start + timedelta(days=6), month_end)
            week_additions = [
                p for p in monthly_additions
                if current_week_start <= p.created_at.date() <= week_end
            ]
            weekly_breakdown[f"week_{week_num}"] = {
                "start": current_week_start.isoformat(),
                "end": week_end.isoformat(),
                "additions": len(week_additions)
            }
            current_week_start += timedelta(days=7)
            week_num += 1

        report_data = {
            "report_type": "monthly",
            "month": f"{today.year}-{today.month:02d}",
            "month_start": month_start.isoformat(),
            "month_end": month_end.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_pokemons": dashboard_data["summary"]["total_pokemons"],
                "monthly_additions": len(monthly_additions),
                "weekly_breakdown": weekly_breakdown,
                "growth_rate": await self._calculate_growth_rate(monthly_additions, month_start, month_end)
            },
            "comprehensive_analysis": {
                "type_analysis": dashboard_data["type_analysis"],
                "stats_analysis": dashboard_data["stats_analysis"],
                "data_quality": dashboard_data["data_quality"]
            },
            "achievements": await self._generate_monthly_achievements(dashboard_data, monthly_additions)
        }

        filename = f"monthly_report_{timestamp}.json"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório mensal gerado: {filepath}")
        return str(filepath)

    async def _analyze_type_trends(self, pokemons: List) -> Dict[str, Any]:
        """
        Analisa tendências de tipos nos pokémons adicionados.
        """
        if not pokemons:
            return {"message": "Nenhum pokémon para análise"}

        type_counts = Counter()
        for pokemon in pokemons:
            for ptype in pokemon.types:
                type_counts[ptype.name] += 1

        return {
            "most_added_types": dict(type_counts.most_common(5)),
            "total_unique_types": len(type_counts),
            "average_types_per_pokemon": round(sum(type_counts.values()) / len(pokemons), 2)
        }

    async def _calculate_growth_rate(self, monthly_additions: List, month_start, month_end) -> Dict[str, Any]:
        """
        Calcula taxa de crescimento mensal.
        """
        days_in_month = (month_end - month_start).days + 1
        daily_average = len(monthly_additions) / days_in_month

        # Simular crescimento (em um sistema real, compararia com mês anterior)
        projected_monthly = daily_average * 30

        return {
            "daily_average": round(daily_average, 2),
            "projected_monthly": round(projected_monthly, 2),
            "actual_monthly": len(monthly_additions),
            "days_analyzed": days_in_month
        }

    async def _generate_monthly_achievements(self, dashboard_data: Dict, monthly_additions: List) -> List[Dict[str, str]]:
        """
        Gera conquistas/marcos do mês.
        """
        achievements = []

        total_pokemons = dashboard_data["summary"]["total_pokemons"]

        # Marcos de quantidade
        if total_pokemons >= 1000:
            achievements.append({
                "title": "Colecionador Master",
                "description": f"Atingiu {total_pokemons} pokémons na coleção!"
            })
        elif total_pokemons >= 500:
            achievements.append({
                "title": "Colecionador Avançado",
                "description": f"Coleção cresceu para {total_pokemons} pokémons!"
            })
        elif total_pokemons >= 150:
            achievements.append({
                "title": "Pokédex Completa",
                "description": "Superou os 150 pokémons originais!"
            })

        # Qualidade dos dados
        quality_score = dashboard_data["data_quality"]["quality_score"]
        if quality_score >= 95:
            achievements.append({
                "title": "Dados Perfeitos",
                "description": f"Qualidade dos dados em {quality_score}%!"
            })
        elif quality_score >= 85:
            achievements.append({
                "title": "Alta Qualidade",
                "description": f"Mantendo qualidade alta: {quality_score}%"
            })

        # Diversidade de tipos
        unique_types = dashboard_data["summary"]["unique_types"]
        if unique_types >= 18:
            achievements.append({
                "title": "Diversidade Completa",
                "description": "Todos os tipos de pokémon representados!"
            })

        # Atividade mensal
        if len(monthly_additions) >= 50:
            achievements.append({
                "title": "Mês Produtivo",
                "description": f"Adicionou {len(monthly_additions)} pokémons este mês!"
            })

        return achievements

    async def get_dashboard_html(self) -> str:
        """
        Gera HTML simples para visualização do dashboard.
        """
        dashboard_data = await self.get_dashboard_data()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pokemon Dashboard</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #333; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
                .stat-item {{ background: #e3f2fd; padding: 15px; border-radius: 5px; text-align: center; }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #1976d2; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
                .top-list {{ list-style: none; padding: 0; }}
                .top-list li {{ padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; }}
                .quality-score {{ font-size: 1.5em; font-weight: bold; }}
                .quality-good {{ color: #4caf50; }}
                .quality-medium {{ color: #ff9800; }}
                .quality-poor {{ color: #f44336; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <h1 class="header">🎮 Pokemon Dashboard</h1>
                    <p class="header">Gerado em: {dashboard_data['generated_at']}</p>
                </div>

                <div class="card">
                    <h2>📊 Resumo Geral</h2>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">{dashboard_data['summary']['total_pokemons']}</div>
                            <div class="stat-label">Total de Pokémons</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{dashboard_data['summary']['unique_types']}</div>
                            <div class="stat-label">Tipos Únicos</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{dashboard_data['summary']['average_base_experience']}</div>
                            <div class="stat-label">Experiência Média</div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>🏆 Top Rankings</h2>
                    <div class="stats-grid">
                        <div>
                            <h3>💪 Maior Ataque</h3>
                            <ul class="top-list">
                                {''.join([f'<li>{p["name"]} - {p["value"]}</li>' for p in dashboard_data["top_rankings"]["top_attack"][:5]])}
                            </ul>
                        </div>
                        <div>
                            <h3>🛡️ Maior Defesa</h3>
                            <ul class="top-list">
                                {''.join([f'<li>{p["name"]} - {p["value"]}</li>' for p in dashboard_data["top_rankings"]["top_defense"][:5]])}
                            </ul>
                        </div>
                        <div>
                            <h3>⚡ Maior Velocidade</h3>
                            <ul class="top-list">
                                {''.join([f'<li>{p["name"]} - {p["value"]}</li>' for p in dashboard_data["top_rankings"]["top_speed"][:5]])}
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h2>📈 Qualidade dos Dados</h2>
                    <div class="quality-score {'quality-good' if dashboard_data['data_quality']['quality_score'] >= 85 else 'quality-medium' if dashboard_data['data_quality']['quality_score'] >= 70 else 'quality-poor'}">
                        Score: {dashboard_data['data_quality']['quality_score']}%
                    </div>
                    <h3>Recomendações:</h3>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in dashboard_data['data_quality']['recommendations']])}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """

        # Salvar HTML
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        html_file = self.reports_dir / f"dashboard_{timestamp}.html"

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Dashboard HTML gerado: {html_file}")
        return str(html_file)

    async def clear_cache(self):
        """
        Limpa cache do dashboard.
        """
        self.cache.clear()
        self.last_cache_update.clear()
        logger.info("Cache do dashboard limpo")
