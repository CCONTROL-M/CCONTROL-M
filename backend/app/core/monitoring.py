"""
Sistema de monitoramento integrado para o backend CCONTROL-M.

Este módulo implementa métricas para monitoramento da API,
incluindo contadores de requisições, tempos de resposta e erros.
"""
import time
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, Gauge, Summary
from contextlib import contextmanager
from typing import Callable, List, Dict, Any, Optional
import psutil
import os
from fastapi.routing import APIRoute

from app.utils.logging_config import get_logger
from app.config.metrics import get_metrics_prometheus, get_metrics_dict, reset_metrics

# Configurar logger
logger = get_logger(__name__)

# Métricas Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total de requisições HTTP recebidas',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'Tempo de resposta das requisições HTTP',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
)

ERROR_COUNT = Counter(
    'http_request_errors_total', 
    'Total de erros HTTP',
    ['method', 'endpoint', 'status_code', 'error_type']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active', 
    'Requisições HTTP ativas',
    ['method']
)

DB_QUERY_TIME = Summary(
    'db_query_duration_seconds', 
    'Tempo de execução de consultas ao banco de dados',
    ['operation', 'table']
)

SYSTEM_MEMORY = Gauge(
    'system_memory_usage_bytes', 
    'Uso de memória do sistema'
)

SYSTEM_CPU = Gauge(
    'system_cpu_usage_percent', 
    'Uso de CPU do sistema'
)

API_OPERATION_COUNT = Counter(
    'api_operation_total', 
    'Total de operações por recurso da API',
    ['resource', 'operation']
)

API_SENSITIVE_OPERATIONS = Counter(
    'api_sensitive_operation_total', 
    'Total de operações sensíveis na API',
    ['user_id', 'resource_type', 'action']
)

# Exportar as funções do módulo metrics para manter compatibilidade
__all__ = ['get_metrics_prometheus', 'get_metrics_dict', 'reset_metrics']


class PrometheusMiddleware:
    """Middleware para capturar métricas Prometheus em requisições FastAPI."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path
        
        # Ignorar rota de métricas para evitar autoreferência
        if path == "/metrics":
            return await call_next(request)
        
        # Normalizar path para evitar explosão de cardinalidade
        # Remove IDs e parâmetros dinâmicos para melhor agrupamento
        path = self._normalize_path(path, request)
        
        # Incrementar contador de requisições ativas
        ACTIVE_REQUESTS.labels(method=method).inc()
        
        # Medir tempo de resposta
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Registrar métricas após completar a requisição
            status_code = response.status_code
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method, 
                endpoint=path, 
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method, 
                endpoint=path
            ).observe(duration)
            
            # Se for erro (4xx ou 5xx), registrar como erro
            if 400 <= status_code < 600:
                error_type = "client_error" if status_code < 500 else "server_error"
                ERROR_COUNT.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code,
                    error_type=error_type
                ).inc()
            
            # Registrar operação da API
            self._register_api_operation(path, method)
            
            return response
            
        except Exception as e:
            # Registrar erro não tratado
            duration = time.time() - start_time
            
            REQUEST_LATENCY.labels(
                method=method, 
                endpoint=path
            ).observe(duration)
            
            ERROR_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=500,
                error_type="exception"
            ).inc()
            
            logger.error(f"Erro ao processar requisição: {str(e)}")
            raise
            
        finally:
            # Sempre decrementar contador de requisições ativas
            ACTIVE_REQUESTS.labels(method=method).dec()
    
    def _normalize_path(self, path: str, request: Request) -> str:
        """
        Normaliza o caminho para evitar explosão de cardinalidade.
        
        Args:
            path: Caminho da URL
            request: Objeto Request
            
        Returns:
            Caminho normalizado
        """
        # Remover versão da API do caminho para métricas
        path = path.replace("/api/v1", "")
        
        # Mapear caminhos comuns com IDs para um formato padrão
        parts = path.split("/")
        normalized_parts = []
        
        for i, part in enumerate(parts):
            # Se não for o último item e o próximo parece ser um ID
            if i < len(parts) - 1 and parts[i+1].isdigit():
                normalized_parts.append(part)
                normalized_parts.append("{id}")
                # Pular o próximo item (o ID)
                i += 1
            else:
                normalized_parts.append(part)
        
        return "/".join(normalized_parts)
    
    def _register_api_operation(self, path: str, method: str) -> None:
        """
        Registra uma operação de API nas métricas.
        
        Args:
            path: Caminho normalizado
            method: Método HTTP
        """
        # Identificar recurso e operação
        parts = path.strip("/").split("/")
        if not parts:
            return
            
        resource = parts[0] if parts else "unknown"
        
        # Mapear método HTTP para operação
        operation_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "partial_update",
            "DELETE": "delete"
        }
        
        operation = operation_map.get(method, "other")
        
        # Se houver um ID no caminho, é uma operação em um item específico
        if len(parts) > 1 and parts[1] == "{id}":
            if method == "GET":
                operation = "get_item"
            elif method == "PUT" or method == "PATCH":
                operation = "update_item"
            elif method == "DELETE":
                operation = "delete_item"
        
        API_OPERATION_COUNT.labels(
            resource=resource,
            operation=operation
        ).inc()


@contextmanager
def db_operation_timer(operation: str, table: str):
    """
    Contexto para medir tempo de operações com banco de dados.
    
    Args:
        operation: Tipo de operação (insert, update, delete, select, etc)
        table: Nome da tabela ou entidade
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        DB_QUERY_TIME.labels(
            operation=operation,
            table=table
        ).observe(duration)


def register_sensitive_operation(user_id: int, resource_type: str, action: str) -> None:
    """
    Registra uma operação sensível nas métricas.
    
    Args:
        user_id: ID do usuário
        resource_type: Tipo de recurso (cliente, usuario, etc)
        action: Tipo de ação (criar, atualizar, excluir, etc)
    """
    API_SENSITIVE_OPERATIONS.labels(
        user_id=str(user_id),
        resource_type=resource_type,
        action=action
    ).inc()


def monitor_system_resources() -> None:
    """Atualiza métricas de recursos do sistema."""
    # Memória
    memory = psutil.virtual_memory()
    SYSTEM_MEMORY.set(memory.used)
    
    # CPU
    cpu_percent = psutil.cpu_percent()
    SYSTEM_CPU.set(cpu_percent)


async def metrics_endpoint() -> Response:
    """
    Endpoint para expor métricas Prometheus.
    
    Returns:
        Resposta com as métricas no formato Prometheus
    """
    # Atualizar métricas de sistema antes de gerar resposta
    monitor_system_resources()
    
    # Gerar métricas
    metrics = get_metrics_prometheus()
    
    # Retornar como response
    return Response(
        content=metrics,
        media_type="text/plain; version=0.0.4"
    )


def setup_monitoring(app: FastAPI) -> None:
    """
    Configura o sistema de monitoramento para uma aplicação FastAPI.
    
    Args:
        app: Instância da aplicação FastAPI
    """
    logger.info("Configurando sistema de monitoramento Prometheus")
    
    # Adicionar middleware para capturar métricas
    app.add_middleware(PrometheusMiddleware)
    
    # Adicionar endpoint de métricas
    app.add_route("/metrics", metrics_endpoint)
    
    logger.info("Sistema de monitoramento configurado. Endpoint: /metrics") 