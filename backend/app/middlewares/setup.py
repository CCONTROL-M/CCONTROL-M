"""
Módulo de configuração centralizada de middlewares.
Este arquivo configura todos os middlewares necessários para a aplicação.
"""
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from app.middlewares.cors_middleware import setup_cors_middleware
from app.middlewares.rate_limiter import create_rate_limiter_middleware
from app.middlewares.audit_middleware import create_audit_middleware
from app.middlewares.validation_middleware import create_validation_middleware
from app.middlewares.logging_middleware import RequestLoggingMiddleware
from app.middlewares.security_middleware import create_security_middleware
from app.middlewares.performance_middleware import PerformanceMiddleware

from app.config.settings import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def configure_middlewares(app: FastAPI) -> None:
    """
    Configura todos os middlewares da aplicação.
    
    Args:
        app: Instância do FastAPI
    """
    # Configurar middleware CORS (com configurações seguras)
    setup_cors_middleware(app)
    logger.info("Middleware CORS configurado")
    
    # Adicionar middleware de segurança integrado
    app.middleware("http")(create_security_middleware())
    logger.info("Middleware de segurança integrado ativado")
    
    # Adicionar middleware de logging
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("Middleware de logging ativado")
    
    # Adicionar middleware de performance
    app.add_middleware(PerformanceMiddleware)
    logger.info("Middleware de performance ativado")
    
    # Adicionar middleware de limitação de taxa se habilitado
    if settings.RATE_LIMIT_ENABLED:
        app.middleware("http")(create_rate_limiter_middleware())
        logger.info(f"Middleware de limitação de taxa ativado: {settings.RATE_LIMIT_REQUESTS} requisições por {settings.RATE_LIMIT_WINDOW}s")
    
    # Adicionar middleware de compressão Gzip
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("Middleware de compressão Gzip ativado")
    
    # Adicionar middleware de auditoria se habilitado
    if settings.ENABLE_AUDIT_LOG:
        app.middleware("http")(create_audit_middleware())
        logger.info("Middleware de auditoria ativado")
    
    # Adicionar middleware de validação e segurança
    app.middleware("http")(create_validation_middleware())
    logger.info("Middleware de validação e segurança ativado")
    
    logger.info("Todos os middlewares configurados com sucesso") 