"""
Middleware de logging para o sistema CCONTROL-M.

Implementa o registro de logs para todas as requisições HTTP
com formato padronizado e enriquecido para facilitar análise.
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Optional, Callable

from app.utils.logging_config import get_logger, get_request_id_from_request
from app.config.settings import settings

# Configurar logger
logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para registrar logs detalhados de cada requisição HTTP.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição, registrando logs antes e depois da execução.
        
        Args:
            request: Requisição HTTP
            call_next: Próximo handler na cadeia de middlewares
            
        Returns:
            Response: Resposta HTTP
        """
        # Obter ou gerar um ID de requisição
        request_id = get_request_id_from_request(request)
        
        # Armazenar o request_id na requisição para uso em outros componentes
        request.state.request_id = request_id
        
        # Adicionar o request_id ao cabeçalho da requisição para propagação
        # (caso esteja lidando com chamadas entre serviços)
        headers = dict(request.headers)
        if "X-Request-ID" not in headers:
            headers["X-Request-ID"] = request_id
        
        # Registrar início da requisição
        start_time = time.time()
        
        # Capturar informações da requisição
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        content_length = request.headers.get("content-length", "0")
        
        # Log de início da requisição
        if settings.APP_ENV == "development" or path not in settings.AUDIT_IGNORE_PATHS:
            logger.info(
                f"Requisição iniciada: {method} {path}",
                extra={
                    "request_id": request_id,
                    "client_ip": client_host,
                    "method": method,
                    "path": path,
                    "user_agent": user_agent,
                    "content_length": content_length,
                    "event": "request_started"
                }
            )
        
        # Objeto para armazenar informações da resposta
        response_data = {
            "status_code": 500,  # Valor padrão em caso de erro
            "duration_ms": 0
        }
        
        try:
            # Processar a requisição
            response = await call_next(request)
            
            # Capturar informações da resposta
            response_data["status_code"] = response.status_code
            response_data["duration_ms"] = round((time.time() - start_time) * 1000, 2)
            
            # Adicionar request_id à resposta
            response.headers["X-Request-ID"] = request_id
            
            # Log de resposta apenas para ambientes não-prod ou status de erro
            is_error = response.status_code >= 400
            should_log = (
                is_error or 
                settings.APP_ENV == "development" or 
                path not in settings.AUDIT_IGNORE_PATHS
            )
            
            if should_log:
                log_level = "error" if is_error else "info"
                logger.log(
                    logging.ERROR if is_error else logging.INFO,
                    f"Requisição completada: {method} {path} {response.status_code}",
                    extra={
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "duration_ms": response_data["duration_ms"],
                        "client_ip": client_host,
                        "method": method,
                        "path": path,
                        "user_agent": user_agent,
                        "event": "request_completed"
                    }
                )
                
            return response
        except Exception as e:
            # Calcular duração em caso de exceção
            response_data["duration_ms"] = round((time.time() - start_time) * 1000, 2)
            
            # Registrar o erro
            logger.error(
                f"Erro na requisição: {method} {path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                    "duration_ms": response_data["duration_ms"],
                    "client_ip": client_host,
                    "method": method,
                    "path": path,
                    "user_agent": user_agent,
                    "event": "request_failed"
                },
                exc_info=True
            )
            
            # Reenviar a exceção para ser tratada pelos handlers de exceção
            raise 