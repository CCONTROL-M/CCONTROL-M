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
        
        # Verificar se as origens são muito permissivas mesmo em ambiente de desenvolvimento
        if "*" in allowed_origins:
            logger.warning("Utilizando origens CORS muito permissivas em ambiente de desenvolvimento.")
    
    # Definir métodos HTTP permitidos
    # Em produção, limitar aos métodos necessários
    if settings.APP_ENV == "production" and (not settings.CORS_ALLOWED_METHODS or "*" in settings.CORS_ALLOWED_METHODS):
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    else:
        allowed_methods = settings.CORS_ALLOWED_METHODS
    
    # Definir cabeçalhos HTTP permitidos
    if (not settings.CORS_ALLOWED_HEADERS or "*" in settings.CORS_ALLOWED_HEADERS) and settings.APP_ENV == "production":
        # Configuração segura para produção
        allowed_headers = [
            "Authorization", 
            "Content-Type", 
            "Accept", 
            "Origin", 
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Client-Version",
            "X-Tenant-ID"
        ]
    else:
        allowed_headers = settings.CORS_ALLOWED_HEADERS
    
    # Definir se deve permitir credenciais (cookies, etc.)
    # Desabilitar em produção se não for explicitamente necessário
    if settings.APP_ENV == "production" and not hasattr(settings, "CORS_ALLOW_CREDENTIALS"):
        allow_credentials = False
        logger.info("CORS credentials desabilitado em produção para maior segurança.")
    else:
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
    
    # Validar URLs de origens permitidas para evitar configurações incorretas
    validated_origins = []
    url_pattern = re.compile(r'^(https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?::\d+)?)')
    
    for origin in allowed_origins:
        if origin == "*":
            validated_origins.append(origin)
            continue
            
        if not url_pattern.match(origin):
            logger.warning(f"Origem CORS inválida ignorada: {origin}")
            continue
            
        validated_origins.append(origin)
    
    # Se não houver origens válidas, definir um fallback seguro
    if not validated_origins:
        if settings.APP_ENV == "production":
            validated_origins = ["https://app.ccontrol-m.com.br"]
            logger.warning("Nenhuma origem CORS válida encontrada. Utilizando fallback seguro.")
        else:
            validated_origins = ["http://localhost:3000"]
            logger.warning("Nenhuma origem CORS válida encontrada. Utilizando localhost como fallback.")
    
    # Configurar middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=validated_origins,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        allow_credentials=allow_credentials,
        expose_headers=exposed_headers,
        max_age=max_age
    )
    
    # Log de configuração CORS
    if settings.APP_ENV == "production":
        logger.info(f"CORS configurado em produção: {len(validated_origins)} origens permitidas")
        logger.debug(f"CORS origens: {validated_origins}")
        logger.debug(f"CORS métodos: {allowed_methods}")
        logger.debug(f"CORS cabeçalhos: {allowed_headers}")
        logger.debug(f"CORS credentials: {allow_credentials}")
    else:
        logger.info(f"CORS configurado em ambiente {settings.APP_ENV}: {len(validated_origins)} origens permitidas")
        if "*" in validated_origins:
            logger.warning("CORS configurado para permitir requisições de qualquer origem (*)! Use apenas em desenvolvimento.") 