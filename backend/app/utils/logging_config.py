"""
Configuração do sistema de logs para o CCONTROL-M.

Este módulo configura o sistema de logs para o aplicativo, incluindo formatação,
handlers e filtros. Ele foi simplificado para evitar dependências circulares e
garantir que request_id esteja sempre disponível.
"""
import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

# Configuração básica do logger
class RequestIDFilter(logging.Filter):
    """Filtro para adicionar o request_id aos logs."""
    
    def filter(self, record):
        # Sempre garantir que o record tenha um request_id
        if not hasattr(record, 'request_id'):
            record.request_id = 'no-request-id'
        return True


def setup_logging(debug: bool = False) -> None:
    """
    Configura o sistema de logs com formatadores e handlers.
    
    Args:
        debug: Se True, habilita logs de debug
    """
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Nível base de logging
    root_level = logging.DEBUG if debug else logging.INFO
    
    # Garantir que o logger raiz esteja configurado corretamente
    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)
    
    # Adicionar o filtro de request_id ao logger raiz
    root_logger.addFilter(RequestIDFilter())
    
    # Formato básico com request_id
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(request_id)s] - %(name)s - %(message)s'
    )
    
    # Configurar handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(root_level)
    
    # Configurar handler para arquivo
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/ccontrol-{today}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(root_level)
    
    # Remover handlers existentes e adicionar os novos
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    loggers = {
        "uvicorn": logging.WARNING,
        "uvicorn.access": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "alembic": logging.INFO,
        "app": root_level,
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = True


def log_with_context(logger, level: str, message: str, request_id: Optional[str] = None, **kwargs) -> None:
    """
    Função utilitária para gerar logs com contexto.
    
    Args:
        logger: Logger para registrar a mensagem
        level: Nível do log (debug, info, warning, error, critical)
        message: Mensagem a ser registrada
        request_id: ID da requisição (opcional)
        **kwargs: Dados adicionais para incluir no contexto
    """
    if request_id is None:
        request_id = 'no-request-id'
    
    extra = {'request_id': request_id}
    extra.update(kwargs)
    
    if level == 'debug':
        logger.debug(message, extra=extra)
    elif level == 'info':
        logger.info(message, extra=extra)
    elif level == 'warning':
        logger.warning(message, extra=extra)
    elif level == 'error':
        logger.error(message, extra=extra)
    elif level == 'critical':
        logger.critical(message, extra=extra)
    else:
        logger.info(message, extra=extra)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado com o nome específico.
    
    Args:
        name: Nome do logger, geralmente __name__ do módulo
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Adicionar o filtro de request_id se ainda não tiver
    has_filter = False
    for filter_obj in logger.filters:
        if isinstance(filter_obj, RequestIDFilter):
            has_filter = True
            break
            
    if not has_filter:
        logger.addFilter(RequestIDFilter())
    
    return logger 