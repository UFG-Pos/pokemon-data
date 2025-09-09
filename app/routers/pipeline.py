from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import shutil
import tempfile

from app.services.database import DatabaseService
from app.services.file_processor import FileProcessorMCP
from app.services.stream_processor import StreamProcessorMCP
from app.services.dashboard_service import DashboardService
from app.services.alert_system import AlertSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])

# Instâncias globais dos serviços (serão inicializadas no startup)
stream_processor: Optional[StreamProcessorMCP] = None
file_processor: Optional[FileProcessorMCP] = None
dashboard_service: Optional[DashboardService] = None
alert_system: Optional[AlertSystem] = None


def get_database_service():
    """Dependency para obter serviço de banco de dados."""
    from app.main import database_service
    return database_service


def get_stream_processor():
    """Dependency para obter stream processor."""
    global stream_processor
    if stream_processor is None:
        from app.main import database_service
        stream_processor = StreamProcessorMCP(database_service)
    return stream_processor


def get_file_processor():
    """Dependency para obter file processor."""
    global file_processor
    if file_processor is None:
        from app.main import database_service
        file_processor = FileProcessorMCP(database_service)
    return file_processor


def get_dashboard_service():
    """Dependency para obter dashboard service."""
    global dashboard_service
    if dashboard_service is None:
        from app.main import database_service
        dashboard_service = DashboardService(database_service)
    return dashboard_service


def get_alert_system():
    """Dependency para obter alert system."""
    global alert_system
    if alert_system is None:
        alert_system = AlertSystem()
    return alert_system


# ==================== ROTAS DE PROCESSAMENTO DE ARQUIVOS ====================

@router.post("/file/export-csv")
async def export_csv(
    filename: Optional[str] = None,
    file_proc: FileProcessorMCP = Depends(get_file_processor)
):
    """
    Exporta dados dos pokémons para arquivo CSV.
    """
    try:
        filepath = await file_proc.export_to_csv(filename)
        return {
            "success": True,
            "message": "Exportação CSV concluída",
            "filepath": filepath
        }
    except Exception as e:
        logger.error(f"Erro na exportação CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/export-json")
async def export_json(
    filename: Optional[str] = None,
    file_proc: FileProcessorMCP = Depends(get_file_processor)
):
    """
    Exporta dados dos pokémons para arquivo JSON.
    """
    try:
        filepath = await file_proc.export_to_json(filename)
        return {
            "success": True,
            "message": "Exportação JSON concluída",
            "filepath": filepath
        }
    except Exception as e:
        logger.error(f"Erro na exportação JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/clean-data")
async def clean_data(
    background_tasks: BackgroundTasks,
    file_proc: FileProcessorMCP = Depends(get_file_processor)
):
    """
    Realiza limpeza e normalização dos dados dos pokémons.
    """
    try:
        result = await file_proc.clean_and_normalize_data()
        return {
            "success": True,
            "message": "Limpeza de dados concluída",
            "result": result
        }
    except Exception as e:
        logger.error(f"Erro na limpeza dos dados: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/aggregations")
async def get_aggregations(
    file_proc: FileProcessorMCP = Depends(get_file_processor)
):
    """
    Retorna agregações e estatísticas dos dados dos pokémons.
    """
    try:
        aggregations = await file_proc.generate_aggregations()
        return {
            "success": True,
            "aggregations": aggregations
        }
    except Exception as e:
        logger.error(f"Erro ao gerar agregações: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/generate-report")
async def generate_report(
    report_type: str = Query("summary", description="Tipo de relatório: summary, detailed, types_analysis"),
    file_proc: FileProcessorMCP = Depends(get_file_processor)
):
    """
    Gera relatório automático dos dados dos pokémons.
    """
    try:
        filepath = await file_proc.generate_report(report_type)
        return {
            "success": True,
            "message": f"Relatório {report_type} gerado",
            "filepath": filepath
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/upload")
async def upload_file(
    file: UploadFile = File(...),
    operation: str = Query("validate", description="Operação: validate ou import"),
    file_proc: FileProcessorMCP = Depends(get_file_processor)
):
    """
    Faz upload e processa arquivo CSV/JSON.
    """
    try:
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Processar arquivo
        result = await file_proc.process_file(tmp_path, operation)
        
        # Limpar arquivo temporário
        Path(tmp_path).unlink()
        
        return {
            "success": True,
            "message": f"Arquivo processado com operação: {operation}",
            "result": result
        }
    except Exception as e:
        logger.error(f"Erro no upload/processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTAS DE STREAM PROCESSING ====================

@router.post("/stream/start")
async def start_stream_processing(
    background_tasks: BackgroundTasks,
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor)
):
    """
    Inicia o processamento em tempo real.
    """
    try:
        if stream_proc.is_running:
            return {
                "success": False,
                "message": "Stream processor já está rodando"
            }
        
        # Iniciar em background
        background_tasks.add_task(stream_proc.start_stream_processing)
        
        return {
            "success": True,
            "message": "Stream processor iniciado"
        }
    except Exception as e:
        logger.error(f"Erro ao iniciar stream processor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/stop")
async def stop_stream_processing(
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor)
):
    """
    Para o processamento em tempo real.
    """
    try:
        await stream_proc.stop_stream_processing()
        return {
            "success": True,
            "message": "Stream processor parado"
        }
    except Exception as e:
        logger.error(f"Erro ao parar stream processor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/status")
async def get_stream_status(
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor)
):
    """
    Retorna status do stream processor.
    """
    try:
        status = await stream_proc.get_stream_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Erro ao obter status do stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/events")
async def get_recent_events(
    limit: int = Query(50, description="Número de eventos recentes"),
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor)
):
    """
    Retorna eventos recentes do stream processor.
    """
    try:
        events = await stream_proc.get_recent_events(limit)
        return {
            "success": True,
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        logger.error(f"Erro ao obter eventos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/anomaly-rule")
async def update_anomaly_rule(
    rule_name: str,
    enabled: bool,
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor)
):
    """
    Atualiza configuração de regra de anomalia.
    """
    try:
        success = await stream_proc.update_anomaly_rule(rule_name, enabled)
        if success:
            return {
                "success": True,
                "message": f"Regra {rule_name} {'habilitada' if enabled else 'desabilitada'}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Regra {rule_name} não encontrada")
    except Exception as e:
        logger.error(f"Erro ao atualizar regra: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/simulate-anomaly")
async def simulate_anomaly(
    pokemon_name: str,
    anomaly_type: str = Query(..., description="Tipo: negative_stats, invalid_type, extreme_stats"),
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor)
):
    """
    Simula uma anomalia para testes.
    """
    try:
        result = await stream_proc.simulate_anomaly(pokemon_name, anomaly_type)
        return {
            "success": "error" not in result,
            "result": result
        }
    except Exception as e:
        logger.error(f"Erro ao simular anomalia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTAS DE DASHBOARD ====================

@router.get("/dashboard/data")
async def get_dashboard_data(
    refresh_cache: bool = Query(False, description="Forçar atualização do cache"),
    dashboard_svc: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna dados completos para o dashboard principal.
    """
    try:
        data = await dashboard_svc.get_dashboard_data(refresh_cache)
        return {
            "success": True,
            "dashboard": data
        }
    except Exception as e:
        logger.error(f"Erro ao obter dados do dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/html", response_class=HTMLResponse)
async def get_dashboard_html(
    dashboard_svc: DashboardService = Depends(get_dashboard_service)
):
    """
    Retorna dashboard em formato HTML para visualização.
    """
    try:
        html_file = await dashboard_svc.get_dashboard_html()
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard HTML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/report")
async def generate_scheduled_report(
    report_type: str = Query("daily", description="Tipo: daily, weekly, monthly"),
    dashboard_svc: DashboardService = Depends(get_dashboard_service)
):
    """
    Gera relatório programado.
    """
    try:
        filepath = await dashboard_svc.generate_scheduled_report(report_type)
        return {
            "success": True,
            "message": f"Relatório {report_type} gerado",
            "filepath": filepath
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório programado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/clear-cache")
async def clear_dashboard_cache(
    dashboard_svc: DashboardService = Depends(get_dashboard_service)
):
    """
    Limpa cache do dashboard.
    """
    try:
        await dashboard_svc.clear_cache()
        return {
            "success": True,
            "message": "Cache do dashboard limpo"
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTAS DE ALERTAS ====================

@router.post("/alerts/send")
async def send_alert(
    level: str,
    title: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Envia um alerta manual.
    """
    try:
        success = await alert_sys.send_alert(level, title, message, details)
        return {
            "success": success,
            "message": "Alerta enviado" if success else "Falha ao enviar alerta"
        }
    except Exception as e:
        logger.error(f"Erro ao enviar alerta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/history")
async def get_alert_history(
    limit: int = Query(50, description="Número de alertas"),
    level: Optional[str] = Query(None, description="Filtrar por nível"),
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Retorna histórico de alertas.
    """
    try:
        since = None
        if level:
            # Se especificou nível, buscar últimas 24h
            from datetime import datetime, timedelta
            since = datetime.utcnow() - timedelta(hours=24)

        history = await alert_sys.get_alert_history(limit, level, since)
        return {
            "success": True,
            "alerts": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Erro ao obter histórico de alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/metrics")
async def get_alert_metrics(
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Retorna métricas do sistema de alertas.
    """
    try:
        metrics = await alert_sys.get_alert_metrics()
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Erro ao obter métricas de alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/configure-channel")
async def configure_alert_channel(
    channel: str,
    enabled: bool,
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Configura canal de alerta.
    """
    try:
        success = await alert_sys.configure_channel(channel, enabled)
        if success:
            return {
                "success": True,
                "message": f"Canal {channel} {'habilitado' if enabled else 'desabilitado'}"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Canal inválido: {channel}")
    except Exception as e:
        logger.error(f"Erro ao configurar canal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/configure-rule")
async def configure_alert_rule(
    rule_name: str,
    config: Dict[str, Any],
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Configura regra de alerta.
    """
    try:
        success = await alert_sys.configure_rule(rule_name, config)
        if success:
            return {
                "success": True,
                "message": f"Regra {rule_name} atualizada"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Regra inválida: {rule_name}")
    except Exception as e:
        logger.error(f"Erro ao configurar regra: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/test")
async def test_alert(
    level: str = Query("info", description="Nível do alerta de teste"),
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Envia alerta de teste.
    """
    try:
        result = await alert_sys.test_alert(level)
        return {
            "success": result["success"],
            "result": result
        }
    except Exception as e:
        logger.error(f"Erro no teste de alerta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/clear-history")
async def clear_alert_history(
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Limpa histórico de alertas.
    """
    try:
        count = await alert_sys.clear_alert_history()
        return {
            "success": True,
            "message": f"Histórico limpo: {count} alertas removidos"
        }
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/export")
async def export_alerts(
    filename: Optional[str] = None,
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Exporta histórico de alertas.
    """
    try:
        filepath = await alert_sys.export_alerts(filename)
        return {
            "success": True,
            "message": "Alertas exportados",
            "filepath": filepath
        }
    except Exception as e:
        logger.error(f"Erro ao exportar alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTAS DE DOWNLOAD ====================

@router.get("/download/{file_type}/{filename}")
async def download_file(
    file_type: str,
    filename: str
):
    """
    Download de arquivos gerados (relatórios, exportações, etc).
    """
    try:
        # Mapear tipos de arquivo para diretórios
        type_dirs = {
            "exports": "data/exports",
            "reports": "data/reports",
            "dashboards": "data/dashboards",
            "alerts": "data/alerts"
        }

        if file_type not in type_dirs:
            raise HTTPException(status_code=400, detail=f"Tipo de arquivo inválido: {file_type}")

        file_path = Path(type_dirs[file_type]) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTAS DE STATUS GERAL ====================

@router.get("/status")
async def get_pipeline_status(
    stream_proc: StreamProcessorMCP = Depends(get_stream_processor),
    alert_sys: AlertSystem = Depends(get_alert_system)
):
    """
    Retorna status geral da pipeline.
    """
    try:
        stream_status = await stream_proc.get_stream_status()
        alert_metrics = await alert_sys.get_alert_metrics()

        return {
            "success": True,
            "pipeline_status": {
                "stream_processor": stream_status,
                "alert_system": alert_metrics,
                "services": {
                    "file_processor": "available",
                    "dashboard_service": "available",
                    "database": "connected"
                }
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter status da pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
