import os
import csv
import json
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import asyncio
from collections import Counter

from app.models.pokemon import Pokemon
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class FileProcessorMCP:
    """
    MCP File Processor para processamento de arquivos CSV/JSON com dados de pokémons.
    Realiza exportação, transformação, limpeza e agregações dos dados.
    """
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.output_dir = Path("data/exports")
        self.reports_dir = Path("data/reports")
        self.temp_dir = Path("data/temp")
        
        # Criar diretórios se não existirem
        for directory in [self.output_dir, self.reports_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def export_to_csv(self, filename: Optional[str] = None) -> str:
        """
        Exporta dados dos pokémons para arquivo CSV.
        """
        try:
            logger.info("Iniciando exportação para CSV")
            
            # Buscar todos os pokémons
            pokemons, total = await self.db_service.list_pokemons(skip=0, limit=10000)
            
            if not pokemons:
                raise ValueError("Nenhum pokémon encontrado para exportar")
            
            # Gerar nome do arquivo se não fornecido
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pokemons_export_{timestamp}.csv"
            
            filepath = self.output_dir / filename
            
            # Preparar dados para CSV
            csv_data = []
            for pokemon in pokemons:
                row = {
                    'id': pokemon.id,
                    'name': pokemon.name,
                    'height': pokemon.height,
                    'weight': pokemon.weight,
                    'base_experience': pokemon.base_experience,
                    'types': ','.join([t.name for t in pokemon.types]),
                    'abilities': ','.join([a.name for a in pokemon.abilities]),
                    'hp': pokemon.stats.hp,
                    'attack': pokemon.stats.attack,
                    'defense': pokemon.stats.defense,
                    'special_attack': pokemon.stats.special_attack,
                    'special_defense': pokemon.stats.special_defense,
                    'speed': pokemon.stats.speed,
                    'created_at': pokemon.created_at.isoformat(),
                    'updated_at': pokemon.updated_at.isoformat()
                }
                csv_data.append(row)
            
            # Escrever CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            logger.info(f"Exportação CSV concluída: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro na exportação CSV: {str(e)}")
            raise
    
    async def export_to_json(self, filename: Optional[str] = None) -> str:
        """
        Exporta dados dos pokémons para arquivo JSON.
        """
        try:
            logger.info("Iniciando exportação para JSON")
            
            # Buscar todos os pokémons
            pokemons, total = await self.db_service.list_pokemons(skip=0, limit=10000)
            
            if not pokemons:
                raise ValueError("Nenhum pokémon encontrado para exportar")
            
            # Gerar nome do arquivo se não fornecido
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pokemons_export_{timestamp}.json"
            
            filepath = self.output_dir / filename
            
            # Converter para dicionários serializáveis
            json_data = []
            for pokemon in pokemons:
                pokemon_dict = pokemon.dict()
                # Converter datetime para string
                pokemon_dict['created_at'] = pokemon.created_at.isoformat()
                pokemon_dict['updated_at'] = pokemon.updated_at.isoformat()
                json_data.append(pokemon_dict)
            
            # Escrever JSON
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump({
                    'export_timestamp': datetime.now().isoformat(),
                    'total_pokemons': len(json_data),
                    'data': json_data
                }, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Exportação JSON concluída: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro na exportação JSON: {str(e)}")
            raise
    
    async def clean_and_normalize_data(self) -> Dict[str, Any]:
        """
        Realiza limpeza e normalização dos dados dos pokémons.
        """
        try:
            logger.info("Iniciando limpeza e normalização dos dados")
            
            # Buscar todos os pokémons
            pokemons, total = await self.db_service.list_pokemons(skip=0, limit=10000)
            
            if not pokemons:
                return {"message": "Nenhum pokémon encontrado", "processed": 0}
            
            processed_count = 0
            issues_found = []
            
            for pokemon in pokemons:
                original_name = pokemon.name
                needs_update = False
                
                # Normalizar nome (lowercase, sem espaços extras)
                normalized_name = pokemon.name.strip().lower()
                if normalized_name != pokemon.name:
                    pokemon.name = normalized_name
                    needs_update = True
                
                # Validar e corrigir stats negativos
                stats_dict = pokemon.stats.dict()
                for stat_name, stat_value in stats_dict.items():
                    if stat_value < 0:
                        issues_found.append(f"Stat negativo encontrado em {original_name}: {stat_name}={stat_value}")
                        setattr(pokemon.stats, stat_name, 0)
                        needs_update = True
                
                # Validar tipos conhecidos
                valid_types = {
                    'normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting',
                    'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost',
                    'dragon', 'dark', 'steel', 'fairy'
                }
                
                for pokemon_type in pokemon.types:
                    if pokemon_type.name not in valid_types:
                        issues_found.append(f"Tipo inválido encontrado em {original_name}: {pokemon_type.name}")
                
                # Atualizar no banco se necessário
                if needs_update:
                    pokemon.updated_at = datetime.utcnow()
                    await self.db_service.save_pokemon(pokemon.dict())
                    processed_count += 1
            
            result = {
                "message": "Limpeza e normalização concluída",
                "total_pokemons": total,
                "processed": processed_count,
                "issues_found": len(issues_found),
                "issues": issues_found[:10]  # Primeiros 10 problemas
            }
            
            logger.info(f"Limpeza concluída: {processed_count} pokémons processados")
            return result
            
        except Exception as e:
            logger.error(f"Erro na limpeza dos dados: {str(e)}")
            raise
    
    async def generate_aggregations(self) -> Dict[str, Any]:
        """
        Gera agregações e estatísticas dos dados dos pokémons.
        """
        try:
            logger.info("Gerando agregações dos dados")
            
            # Buscar todos os pokémons
            pokemons, total = await self.db_service.list_pokemons(skip=0, limit=10000)
            
            if not pokemons:
                return {"message": "Nenhum pokémon encontrado", "aggregations": {}}
            
            # Contagem por tipo
            type_counts = Counter()
            for pokemon in pokemons:
                for pokemon_type in pokemon.types:
                    type_counts[pokemon_type.name] += 1
            
            # Estatísticas de stats
            stats_data = {
                'hp': [p.stats.hp for p in pokemons],
                'attack': [p.stats.attack for p in pokemons],
                'defense': [p.stats.defense for p in pokemons],
                'special_attack': [p.stats.special_attack for p in pokemons],
                'special_defense': [p.stats.special_defense for p in pokemons],
                'speed': [p.stats.speed for p in pokemons]
            }
            
            stats_summary = {}
            for stat_name, values in stats_data.items():
                stats_summary[stat_name] = {
                    'mean': round(sum(values) / len(values), 2),
                    'min': min(values),
                    'max': max(values),
                    'median': sorted(values)[len(values) // 2]
                }
            
            # Top pokémons por stat
            top_attack = sorted(pokemons, key=lambda p: p.stats.attack, reverse=True)[:5]
            top_defense = sorted(pokemons, key=lambda p: p.stats.defense, reverse=True)[:5]
            top_speed = sorted(pokemons, key=lambda p: p.stats.speed, reverse=True)[:5]
            
            aggregations = {
                "total_pokemons": total,
                "type_distribution": dict(type_counts.most_common()),
                "stats_summary": stats_summary,
                "top_attack": [{"name": p.name, "attack": p.stats.attack} for p in top_attack],
                "top_defense": [{"name": p.name, "defense": p.stats.defense} for p in top_defense],
                "top_speed": [{"name": p.name, "speed": p.stats.speed} for p in top_speed],
                "generation_timestamp": datetime.now().isoformat()
            }
            
            logger.info("Agregações geradas com sucesso")
            return aggregations

        except Exception as e:
            logger.error(f"Erro na geração de agregações: {str(e)}")
            raise

    async def generate_report(self, report_type: str = "summary") -> str:
        """
        Gera relatório automático dos dados dos pokémons.
        """
        try:
            logger.info(f"Gerando relatório: {report_type}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if report_type == "summary":
                return await self._generate_summary_report(timestamp)
            elif report_type == "detailed":
                return await self._generate_detailed_report(timestamp)
            elif report_type == "types_analysis":
                return await self._generate_types_analysis_report(timestamp)
            else:
                raise ValueError(f"Tipo de relatório não suportado: {report_type}")

        except Exception as e:
            logger.error(f"Erro na geração do relatório: {str(e)}")
            raise

    async def _generate_summary_report(self, timestamp: str) -> str:
        """
        Gera relatório resumido.
        """
        aggregations = await self.generate_aggregations()

        filename = f"pokemon_summary_report_{timestamp}.json"
        filepath = self.reports_dir / filename

        report_data = {
            "report_type": "summary",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_pokemons": aggregations["total_pokemons"],
                "unique_types": len(aggregations["type_distribution"]),
                "most_common_type": max(aggregations["type_distribution"].items(), key=lambda x: x[1]),
                "average_stats": {
                    stat: data["mean"]
                    for stat, data in aggregations["stats_summary"].items()
                },
                "strongest_pokemon": aggregations["top_attack"][0] if aggregations["top_attack"] else None,
                "fastest_pokemon": aggregations["top_speed"][0] if aggregations["top_speed"] else None
            },
            "full_aggregations": aggregations
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório resumido gerado: {filepath}")
        return str(filepath)

    async def _generate_detailed_report(self, timestamp: str) -> str:
        """
        Gera relatório detalhado em CSV.
        """
        # Exportar dados completos
        csv_path = await self.export_to_csv(f"detailed_report_{timestamp}.csv")

        # Gerar agregações
        aggregations = await self.generate_aggregations()

        # Salvar agregações separadamente
        agg_filename = f"detailed_aggregations_{timestamp}.json"
        agg_filepath = self.reports_dir / agg_filename

        with open(agg_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "report_type": "detailed",
                "generated_at": datetime.now().isoformat(),
                "data_file": csv_path,
                "aggregations": aggregations
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório detalhado gerado: {agg_filepath}")
        return str(agg_filepath)

    async def _generate_types_analysis_report(self, timestamp: str) -> str:
        """
        Gera relatório de análise por tipos.
        """
        pokemons, total = await self.db_service.list_pokemons(skip=0, limit=10000)

        # Análise por tipo
        type_analysis = {}
        for pokemon in pokemons:
            for pokemon_type in pokemon.types:
                type_name = pokemon_type.name
                if type_name not in type_analysis:
                    type_analysis[type_name] = {
                        'count': 0,
                        'pokemons': [],
                        'avg_stats': {'hp': 0, 'attack': 0, 'defense': 0, 'special_attack': 0, 'special_defense': 0, 'speed': 0},
                        'total_stats': {'hp': 0, 'attack': 0, 'defense': 0, 'special_attack': 0, 'special_defense': 0, 'speed': 0}
                    }

                type_analysis[type_name]['count'] += 1
                type_analysis[type_name]['pokemons'].append({
                    'name': pokemon.name,
                    'id': pokemon.id,
                    'stats': pokemon.stats.dict()
                })

                # Somar stats para calcular média
                stats_dict = pokemon.stats.dict()
                for stat_name, stat_value in stats_dict.items():
                    type_analysis[type_name]['total_stats'][stat_name] += stat_value

        # Calcular médias
        for type_name, data in type_analysis.items():
            count = data['count']
            for stat_name in data['avg_stats'].keys():
                data['avg_stats'][stat_name] = round(data['total_stats'][stat_name] / count, 2)
            del data['total_stats']  # Remover totais para economizar espaço

        filename = f"types_analysis_report_{timestamp}.json"
        filepath = self.reports_dir / filename

        report_data = {
            "report_type": "types_analysis",
            "generated_at": datetime.now().isoformat(),
            "total_pokemons": total,
            "total_types": len(type_analysis),
            "type_analysis": type_analysis
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Relatório de análise por tipos gerado: {filepath}")
        return str(filepath)

    async def process_file(self, file_path: str, operation: str = "validate") -> Dict[str, Any]:
        """
        Processa arquivo CSV/JSON importado.
        """
        try:
            logger.info(f"Processando arquivo: {file_path}")

            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

            if file_path.suffix.lower() == '.csv':
                return await self._process_csv_file(file_path, operation)
            elif file_path.suffix.lower() == '.json':
                return await self._process_json_file(file_path, operation)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {file_path.suffix}")

        except Exception as e:
            logger.error(f"Erro no processamento do arquivo: {str(e)}")
            raise

    async def _process_csv_file(self, file_path: Path, operation: str) -> Dict[str, Any]:
        """
        Processa arquivo CSV.
        """
        df = pd.read_csv(file_path)

        if operation == "validate":
            return self._validate_dataframe(df, "CSV")
        elif operation == "import":
            return await self._import_from_dataframe(df)
        else:
            raise ValueError(f"Operação não suportada: {operation}")

    async def _process_json_file(self, file_path: Path, operation: str) -> Dict[str, Any]:
        """
        Processa arquivo JSON.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Converter para DataFrame se for lista de pokémons
        if isinstance(data, dict) and 'data' in data:
            df = pd.DataFrame(data['data'])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            raise ValueError("Formato JSON não reconhecido")

        if operation == "validate":
            return self._validate_dataframe(df, "JSON")
        elif operation == "import":
            return await self._import_from_dataframe(df)
        else:
            raise ValueError(f"Operação não suportada: {operation}")

    def _validate_dataframe(self, df: pd.DataFrame, file_type: str) -> Dict[str, Any]:
        """
        Valida DataFrame com dados de pokémons.
        """
        required_columns = ['id', 'name', 'height', 'weight']
        missing_columns = [col for col in required_columns if col not in df.columns]

        validation_result = {
            "file_type": file_type,
            "total_rows": len(df),
            "columns": list(df.columns),
            "missing_required_columns": missing_columns,
            "is_valid": len(missing_columns) == 0,
            "issues": []
        }

        if not validation_result["is_valid"]:
            validation_result["issues"].append(f"Colunas obrigatórias ausentes: {missing_columns}")

        # Verificar dados inválidos
        if 'id' in df.columns:
            invalid_ids = df[df['id'].isna() | (df['id'] <= 0)]
            if not invalid_ids.empty:
                validation_result["issues"].append(f"IDs inválidos encontrados: {len(invalid_ids)} registros")

        if 'name' in df.columns:
            empty_names = df[df['name'].isna() | (df['name'] == '')]
            if not empty_names.empty:
                validation_result["issues"].append(f"Nomes vazios encontrados: {len(empty_names)} registros")

        return validation_result

    async def _import_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Importa dados do DataFrame para o banco de dados.
        """
        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Converter linha para formato de pokémon
                pokemon_data = {
                    'id': int(row['id']),
                    'name': str(row['name']).lower().strip(),
                    'height': int(row.get('height', 0)),
                    'weight': int(row.get('weight', 0)),
                    'base_experience': int(row.get('base_experience', 0)) if pd.notna(row.get('base_experience')) else None,
                    'types': [{'name': t.strip(), 'url': ''} for t in str(row.get('types', '')).split(',') if t.strip()],
                    'abilities': [{'name': a.strip(), 'url': '', 'is_hidden': False} for a in str(row.get('abilities', '')).split(',') if a.strip()],
                    'stats': {
                        'hp': int(row.get('hp', 0)),
                        'attack': int(row.get('attack', 0)),
                        'defense': int(row.get('defense', 0)),
                        'special-attack': int(row.get('special_attack', 0)),
                        'special-defense': int(row.get('special_defense', 0)),
                        'speed': int(row.get('speed', 0))
                    },
                    'sprites': {
                        'front_default': None,
                        'front_shiny': None,
                        'back_default': None,
                        'back_shiny': None
                    }
                }

                await self.db_service.save_pokemon(pokemon_data)
                imported_count += 1

            except Exception as e:
                errors.append(f"Linha {index + 1}: {str(e)}")

        return {
            "imported_count": imported_count,
            "total_rows": len(df),
            "errors": errors[:10],  # Primeiros 10 erros
            "success_rate": round((imported_count / len(df)) * 100, 2) if len(df) > 0 else 0
        }
