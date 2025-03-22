"""
Middleware de monitoramento de performance para o sistema CCONTROL-M.

Implementa monitoramento de desempenho das requisições e coleta
métricas para análise e observabilidade.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import logging
import re
import threading
from collections import defaultdict
from typing import Dict, List, Optional

from app.utils.logging_config import get_logger
from app.config.metrics import (
    update_request_count, 
    update_request_latency,
    update_request_in_progress,
    update_request_size,
    update_response_size,
    update_error_count,
    PerfMetrics
)

# Configurar logger
logger = get_logger(__name__)

# Limite de tempo para considerar uma requisição lenta (em segundos)
SLOW_REQUEST_THRESHOLD = 1.0

# Lock para acesso seguro a contadores (evita race conditions)
metrics_lock = threading.Lock()

# Contadores globais para métricas em memória
perf_metrics = PerfMetrics()

# Padrão para extrair rota base (para agrupar métricas)
# Exemplo: /api/v1/usuarios/123 -> /api/v1/usuarios/{id}
ROUTE_PATTERN = re.compile(r'/([^/]+)/([^/]+)(?:/[^/]+)*$')


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware para monitorar a performance das requisições.
    
    Identifica requisições lentas que excedem um limite de tempo
    configurado e coleta métricas para monitoramento.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição, monitorando seu tempo de execução.
        
        Args:
            request: Requisição HTTP
            call_next: Próximo handler na cadeia de middlewares
            
        Returns:
            Response: Resposta HTTP
        """
        # Extrair rota base para agrupamento de métricas
        route = self._get_route_template(request.url.path)
        
        # Incrementar contador de requisições em andamento
        update_request_in_progress(route, request.method, 1)
        
        # Iniciar temporizador
        start_time = time.time()
        
        # Capturar tamanho da requisição
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            update_request_size(route, request.method, int(content_length))
        
        try:
            # Processar a requisição
            response = await call_next(request)
            
            # Calcular duração
            process_time = time.time() - start_time
            
            # Atualizar métricas
            update_request_count(route, request.method, response.status_code)
            update_request_latency(route, request.method, process_time)
            
            # Capturar tamanho da resposta
            resp_size = response.headers.get("content-length")
            if resp_size and resp_size.isdigit():
                update_response_size(route, request.method, int(resp_size))
            
            # Verificar se a requisição foi lenta
            if process_time > SLOW_REQUEST_THRESHOLD:
                # Incrementar contador de requisições lentas
                with metrics_lock:
                    perf_metrics.slow_requests_total += 1
                    perf_metrics.slow_requests_by_route[route] += 1
                
                logger.warning(
                    f"Requisição lenta detectada: {request.method} {request.url.path} "
                    f"levou {process_time:.4f}s (limite: {SLOW_REQUEST_THRESHOLD}s)",
                    extra={
                        "path": request.url.path,
                        "route": route,
                        "method": request.method,
                        "duration": f"{process_time:.4f}s",
                        "status_code": response.status_code,
                        "request_id": getattr(request.state, "request_id", "unknown")
                    }
                )
            
            # Adicionar header com tempo de processamento
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            
            return response
            
        except Exception as exc:
            # Calcular duração em caso de erro
            process_time = time.time() - start_time
            
            # Atualizar métricas de erro
            update_error_count(route, request.method, type(exc).__name__)
            
            # Registrar erro de performance
            logger.error(
                f"Erro de performance: {request.method} {request.url.path} "
                f"falhou após {process_time:.4f}s: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "route": route,
                    "method": request.method,
                    "duration": f"{process_time:.4f}s",
                    "exception": str(exc),
                    "exception_type": type(exc).__name__,
                    "request_id": getattr(request.state, "request_id", "unknown")
                },
                exc_info=True
            )
            
            # Re-lançar a exceção
            raise
        finally:
            # Decrementar contador de requisições em andamento
            update_request_in_progress(route, request.method, -1)
    
    def _get_route_template(self, path: str) -> str:
        """
        Converte um caminho específico em um template de rota para agrupar métricas.
        
        Exemplo: /api/v1/usuarios/123 -> /api/v1/usuarios/{id}
        
        Args:
            path: Caminho da URL
            
        Returns:
            String com o template da rota
        """
        # Verificar rotas de API
        if '/api/v1/' in path:
            # Dividir o caminho
            parts = path.split('/')
            
            # Construir template (substituindo IDs numéricos e UUIDs por {id})
            result = []
            for i, part in enumerate(parts):
                if i < 3:  # Manter /api/v1 intacto
                    result.append(part)
                elif i == 3:  # Nome do recurso
                    result.append(part)
                elif part and (part.isdigit() or (len(part) > 8 and '-' in part)):
                    # Substituir números e UUIDs por {id}
                    result.append('{id}')
                elif part:
                    result.append(part)
                    
            return '/'.join(result)
        
        return path 