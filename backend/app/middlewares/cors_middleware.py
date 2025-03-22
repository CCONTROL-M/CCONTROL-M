from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import re

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
    # Configuração simplificada para ambiente de desenvolvimento
    if settings.APP_ENV != "production":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
            expose_headers=[
                "Content-Length", 
                "Content-Type", 
                "X-RateLimit-Limit", 
                "X-RateLimit-Remaining", 
                "X-RateLimit-Reset",
                "X-Request-ID"
            ],
            max_age=600  # 10 minutos
        )
        logger.info("CORS configurado em modo permissivo para ambiente de desenvolvimento")
        return
    
    # Determina as origens permitidas com base nas configurações
    # Em produção, deve ser uma lista específica de domínios
    if settings.APP_ENV == "production":
        # Garantir que as origens sejam específicas em produção
        if "*" in settings.CORS_ALLOWED_ORIGINS or not settings.CORS_ALLOWED_ORIGINS:
            logger.warning("Configuração CORS permissiva detectada em produção. Utilizando origens seguras padrão.")
            # Configuração de fallback segura para produção
            allowed_origins = [
                "https://app.ccontrol-m.com.br",
                "https://ccontrol-m.com.br",
                "https://api.ccontrol-m.com.br"
            ]
        else:
            # Verificar se todas as origens em produção usam HTTPS
            insecure_origins = [origin for origin in settings.CORS_ALLOWED_ORIGINS 
                              if origin.startswith("http://") and not origin.startswith("http://localhost")]
            
            if insecure_origins:
                logger.warning(f"Origens CORS inseguras detectadas em produção: {insecure_origins}")
                # Filtrar origens inseguras, permitindo apenas localhost com HTTP
                allowed_origins = [
                    origin for origin in settings.CORS_ALLOWED_ORIGINS
                    if origin.startswith("https://") or origin.startswith("http://localhost")
                ]
            else:
                allowed_origins = settings.CORS_ALLOWED_ORIGINS
    else:
        # Para desenvolvimento e teste, pode ser mais permissivo
        allowed_origins = settings.CORS_ALLOWED_ORIGINS
        
    # Definir métodos HTTP permitidos
    allowed_methods = settings.CORS_ALLOWED_METHODS
    
    # Definir cabeçalhos HTTP permitidos
    allowed_headers = settings.CORS_ALLOWED_HEADERS
    
    # Definir se deve permitir credenciais (cookies, etc.)
    allow_credentials = settings.CORS_ALLOW_CREDENTIALS
    
    # Definir cabeçalhos expostos à aplicação no navegador
    exposed_headers = [
        "Content-Length", 
        "Content-Type", 
        "X-RateLimit-Limit", 
        "X-RateLimit-Remaining", 
        "X-RateLimit-Reset",
        "X-Request-ID"
    ]
    
    # Definir tempo máximo de cache das verificações preflight
    # Em produção, usar um tempo maior para melhorar a performance
    if settings.APP_ENV == "production":
        max_age = 3600  # 1 hora
    else:
        max_age = 600  # 10 minutos
    
    # Configurar middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_methods=settings.CORS_ALLOWED_METHODS,
        allow_headers=settings.CORS_ALLOWED_HEADERS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        expose_headers=exposed_headers,
        max_age=max_age
    )
    
    # Log de configuração CORS
    logger.info(f"CORS configurado em ambiente {settings.APP_ENV}")
    logger.debug(f"CORS origens: {settings.CORS_ALLOWED_ORIGINS}")
    logger.debug(f"CORS métodos: {settings.CORS_ALLOWED_METHODS}")
    logger.debug(f"CORS cabeçalhos: {settings.CORS_ALLOWED_HEADERS}")
    logger.debug(f"CORS credentials: {settings.CORS_ALLOW_CREDENTIALS}") 