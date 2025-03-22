"""
Configuração de logs para o sistema CCONTROL-M.

Implementa uma configuração segura e escalável para logs
com tratamento adequado de dados sensíveis.
"""
import logging
import os
import sys
import json
import re
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Dict, Any, Optional, Union, List

from app.config.settings import settings

# Criar diretório de logs se não existir
LOG_DIR = settings.LOG_DIR if hasattr(settings, "LOG_DIR") else "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Lista de campos sensíveis a serem filtrados dos logs
SENSITIVE_FIELDS = settings.SENSITIVE_FIELDS if hasattr(settings, "SENSITIVE_FIELDS") else [
    "password", "senha", "token", "secret", "api_key", "apikey",
    "credit_card", "cartao_credito", "cartao", "cvv", 
    "cpf", "cnpj", "rg", "passport"
]

# Compilar padrões de regex para dados sensíveis
SENSITIVE_PATTERNS = [
    re.compile(r"(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)"),           # Email
    re.compile(r"(\b\d{3}[.-]?\d{3}[.-]?\d{3}[.-]?\d{2}\b)"),                      # CPF
    re.compile(r"(\b\d{2}[.-]?\d{3}[.-]?\d{3}[/]?[.-]?\d{4}[.-]?\d{2}\b)"),         # CNPJ
    re.compile(r"(\b\d{13,16}\b)"),                                                # Possível cartão de crédito
    re.compile(r"(bearer\s+[a-zA-Z0-9\-_.]+)"),                                    # Bearer token
    re.compile(r"(eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+)"),         # JWT
    re.compile(r"(\b(?:\d[ -]*?){13,16}\b)"),                                      # Cartão de crédito sem formatação
]


class SensitiveDataFilter(logging.Filter):
    """
    Filtro para remover dados sensíveis dos logs.
    """
    
    def __init__(self, sensitive_fields=None, patterns=None):
        super().__init__()
        self.sensitive_fields = sensitive_fields or SENSITIVE_FIELDS
        self.patterns = patterns or SENSITIVE_PATTERNS
    
    def filter(self, record):
        """
        Filtra cada registro de log para remover dados sensíveis.
        
        Args:
            record: O registro de log a ser processado
            
        Returns:
            Booleano indicando se o registro deve ser incluído no log
        """
        if isinstance(record.msg, dict):
            record.msg = self._filter_dict(record.msg)
        elif isinstance(record.msg, str):
            record.msg = self._filter_string(record.msg)
            
        if hasattr(record, "args") and record.args:
            if isinstance(record.args, dict):
                record.args = self._filter_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self._filter_string(arg) if isinstance(arg, str) 
                    else self._filter_dict(arg) if isinstance(arg, dict)
                    else arg
                    for arg in record.args
                )
                
        return True
    
    def _filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtra dados sensíveis de um dicionário recursivamente.
        
        Args:
            data: Dicionário a ser filtrado
            
        Returns:
            Dicionário com dados sensíveis redactados
        """
        if not isinstance(data, dict):
            return data
            
        filtered = {}
        for key, value in data.items():
            # Verificar se a chave é sensível
            key_lower = key.lower()
            if any(field.lower() in key_lower for field in self.sensitive_fields):
                filtered[key] = "**REDACTED**"
            elif isinstance(value, dict):
                filtered[key] = self._filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    self._filter_dict(item) if isinstance(item, dict)
                    else self._filter_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                filtered[key] = self._filter_string(value)
            else:
                filtered[key] = value
                
        return filtered
    
    def _filter_string(self, text: str) -> str:
        """
        Filtra dados sensíveis de uma string.
        
        Args:
            text: String a ser filtrada
            
        Returns:
            String com dados sensíveis redactados
        """
        if not isinstance(text, str):
            return text
            
        # Filtrar padrões sensíveis
        for pattern in self.patterns:
            text = pattern.sub("**REDACTED**", text)
            
        return text


class JsonFormatter(logging.Formatter):
    """
    Formatador de logs em formato JSON estruturado.
    """
    
    def __init__(self, include_hostname=True):
        super().__init__()
        self.include_hostname = include_hostname
        self.hostname = os.environ.get('HOSTNAME', 'unknown')
    
    def format(self, record):
        """
        Formata o registro de log como JSON.
        
        Args:
            record: O registro de log a ser formatado
            
        Returns:
            String JSON formatada
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'name': record.name,
            'module': record.module,
            'line': record.lineno,
        }
        
        # Adicionar hostname em ambientes containerizados
        if self.include_hostname:
            log_data['hostname'] = self.hostname
            
        # Adicionar informações do aplicativo
        log_data['app'] = settings.APP_NAME
        log_data['env'] = settings.APP_ENV
        
        # Adicionar a mensagem de log
        if isinstance(record.msg, dict):
            log_data['message'] = record.msg
        else:
            log_data['message'] = record.getMessage()
            
        # Adicionar exceção, se houver
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
            
        # Adicionar extras
        if hasattr(record, 'extras'):
            log_data.update(record.extras)
            
        # Serializar como JSON
        return json.dumps(log_data)


def setup_logging():
    """
    Configura o sistema de logging com suporte a diferentes ambientes.
    """
    # Configurações baseadas no ambiente
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configuração raiz do logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remover handlers existentes para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configurar formatador JSON
    json_formatter = JsonFormatter()
    
    # Adicionar handler de console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(log_level)
    
    # Adicionar handler de arquivo com rotação diária
    file_handler = TimedRotatingFileHandler(
        filename=f"{LOG_DIR}/app.log",
        when="midnight",
        interval=1,
        backupCount=30,  # Manter logs por 30 dias
        encoding="utf-8"
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(log_level)
    
    # Adicionar handler de arquivo para erros
    error_handler = RotatingFileHandler(
        filename=f"{LOG_DIR}/error.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10,
        encoding="utf-8"
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Adicionar filtro de dados sensíveis a todos os handlers
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)
    file_handler.addFilter(sensitive_filter)
    error_handler.addFilter(sensitive_filter)
    
    # Adicionar handlers ao logger raiz
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configurar comportamento de outros loggers de bibliotecas
    # Reduzir verbosidade de logs de bibliotecas comuns
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log de inicialização
    logging.info(f"Logging configurado para o ambiente {settings.APP_ENV} no nível {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para um módulo.
    
    Args:
        name: Nome do módulo (geralmente __name__)
        
    Returns:
        Instância do logger configurada
    """
    return logging.getLogger(name)


def log_with_context(logger, level: str, message: str, **extra) -> None:
    """
    Registra uma mensagem com contexto adicional.
    
    Args:
        logger: Instância do logger a ser usada
        level: Nível de log (debug, info, warning, error, critical)
        message: Mensagem a ser registrada
        **extra: Campos de contexto adicionais
    """
    log_method = getattr(logger, level.lower())
    
    if extra:
        extra_dict = {"extras": extra}
        if isinstance(message, dict):
            message.update({"context": extra})
            log_method(message)
        else:
            logger_message = {
                "message": message,
                "context": extra
            }
            log_method(logger_message)
    else:
        log_method(message)


# Inicializar o sistema de logging ao importar o módulo
setup_logging() 