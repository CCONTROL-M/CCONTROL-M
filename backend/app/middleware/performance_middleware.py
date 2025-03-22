"""Middleware de monitoramento de performance para o sistema CCONTROL-M."""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import logging

from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# Limite de tempo para considerar uma requisição lenta (em segundos)
SLOW_REQUEST_THRESHOLD = 1.0


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware para monitorar a performance das requisições.
    
    Identifica requisições lentas que excedem um limite de tempo
    configurado e as registra para diagnóstico.
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
        # Iniciar temporizador
        start_time = time.time()
        
        # Processar a requisição
        response = await call_next(request)
        
        # Calcular duração
        process_time = time.time() - start_time
        
        # Verificar se a requisição foi lenta
        if process_time > SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Requisição lenta detectada: {request.method} {request.url.path} "
                f"levou {process_time:.4f}s (limite: {SLOW_REQUEST_THRESHOLD}s)",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "duration": f"{process_time:.4f}s",
                    "status_code": response.status_code
                }
            )
        
        # Adicionar header com tempo de processamento (apenas em ambiente de desenvolvimento)
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        
        return response 