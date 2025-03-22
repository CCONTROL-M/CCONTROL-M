"""Middleware de logging para o sistema CCONTROL-M."""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import logging

from app.utils.logging_config import get_logger, log_with_context

# Configurar logger
logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para registrar informações sobre cada requisição.
    
    Gera logs para o início e fim de cada requisição, incluindo:
    - Path
    - Método HTTP
    - ID de correlação
    - Duração
    - Código de status
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição, registrando logs no início e no fim.
        
        Args:
            request: Requisição HTTP
            call_next: Próximo handler na cadeia de middlewares
            
        Returns:
            Response: Resposta HTTP
        """
        # Gerar ID de correlação
        correlation_id = str(uuid.uuid4())
        
        # Iniciar temporizador
        start_time = time.time()
        
        # Registrar o início da requisição
        log_with_context(
            logger,
            "info",
            f"Iniciando requisição {request.method} {request.url.path}",
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method
        )
        
        # Processar a requisição
        try:
            response = await call_next(request)
            
            # Calcular duração
            process_time = time.time() - start_time
            
            # Registrar o fim da requisição
            log_with_context(
                logger,
                "info",
                f"Concluindo requisição {request.method} {request.url.path}",
                correlation_id=correlation_id,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=f"{process_time:.4f}s"
            )
            
            return response
        except Exception as e:
            # Calcular duração em caso de erro
            process_time = time.time() - start_time
            
            # Registrar erro
            log_with_context(
                logger,
                "error",
                f"Erro na requisição {request.method} {request.url.path}: {str(e)}",
                correlation_id=correlation_id,
                path=request.url.path,
                method=request.method,
                duration=f"{process_time:.4f}s",
                error=str(e)
            )
            
            # Re-lançar exceção para ser tratada pelos manipuladores de erro
            raise 