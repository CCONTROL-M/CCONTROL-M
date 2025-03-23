from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

from app.config.settings import settings
from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Configura o middleware CORS com configurações seguras.
    
    Args:
        app: Instância do FastAPI
    """
    # Configurar origens permitidas com base no ambiente
    allowed_origins = settings.CORS_ALLOWED_ORIGINS
    
    # Adicionar configuração mais permissiva em ambiente de desenvolvimento
    if settings.APP_ENV == "development":
        # Adicionar mais origens para facilitar o desenvolvimento
        allowed_origins = ["*"]
        logger.warning("CORS configurado em modo de desenvolvimento - Todas as origens permitidas")
    # Em produção, garantir que as origens sejam seguras
    elif settings.APP_ENV == "production":
        # Verificar se a configuração é permissiva demais para produção
        if "*" in allowed_origins or not allowed_origins:
            logger.warning("Configuração CORS permissiva detectada em produção. Usando origens seguras padrão.")
            # Configuração de fallback segura para produção
            allowed_origins = [
                "https://app.ccontrol-m.com.br",
                "https://ccontrol-m.com.br",
                "https://api.ccontrol-m.com.br"
            ]
        else:
            # Filtrar origens inseguras, permitindo apenas localhost com HTTP
            insecure_origins = [
                origin for origin in allowed_origins 
                if origin.startswith("http://") and not origin.startswith("http://localhost")
            ]
            
            if insecure_origins:
                logger.warning(f"Origens CORS inseguras detectadas em produção: {insecure_origins}")
                allowed_origins = [
                    origin for origin in allowed_origins
                    if origin.startswith("https://") or origin.startswith("http://localhost")
                ]
    
    # Definir tempo de cache preflight com base no ambiente
    max_age = 3600 if settings.APP_ENV == "production" else 600  # 1 hora / 10 minutos
    
    # Configurar e adicionar middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOWED_METHODS,
        allow_headers=settings.CORS_ALLOWED_HEADERS,
        expose_headers=[
            "Content-Length", 
            "Content-Type", 
            "X-RateLimit-Limit", 
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset",
            "X-Request-ID"
        ],
        max_age=max_age
    )
    
    # Log de configuração CORS
    logger.info(f"CORS configurado em ambiente {settings.APP_ENV}")
    logger.info(f"CORS origens permitidas: {allowed_origins}")
    logger.info(f"CORS métodos permitidos: {settings.CORS_ALLOWED_METHODS}") 