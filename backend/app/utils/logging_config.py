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
import uuid
import traceback
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
    "cpf", "cnpj", "rg", "passport", "authorization"
]

# Definir padrões adicionais de dados sensíveis específicos
ADDITIONAL_PATTERNS = {
    r'(?i)"telefone"\s*:\s*"[^"]*"': '"telefone":"(XX) XXXXX-XXXX"',
    r'(?i)"celular"\s*:\s*"[^"]*"': '"celular":"(XX) XXXXX-XXXX"',
    r'(?i)"endereco"\s*:\s*({[^}]*})': '"endereco":"[ENDEREÇO PROTEGIDO]"',
    r'(?i)"rg"\s*:\s*"[^"]*"': '"rg":"XX.XXX.XXX-X"',
}

# Padrões de mascaramento para CPF/CNPJ 
CPF_PATTERN = re.compile(r'(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})')
CNPJ_PATTERN = re.compile(r'(\d{2})\.?(\d{3})\.?(\d{3})\/?(\d{4})-?(\d{2})')

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

# Obter nível de log do ambiente (padrão: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class SensitiveDataFilter(logging.Filter):
    """
    Filtro para remover dados sensíveis dos logs.
    """
    
    def __init__(self, sensitive_fields=None, patterns=None, mask_char="*"):
        super().__init__()
        self.sensitive_fields = sensitive_fields or SENSITIVE_FIELDS
        self.patterns = patterns or SENSITIVE_PATTERNS
        self.mask_char = mask_char
    
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
         
        # Mascarar CPF (mantendo apenas primeiros e últimos dígitos)
        text = CPF_PATTERN.sub(r'\1.XXX.XXX-\4', text)
        
        # Mascarar CNPJ (mantendo apenas primeiros e últimos dígitos)
        text = CNPJ_PATTERN.sub(r'\1.XXX.XXX/XXXX-\5', text)
            
        # Filtrar padrões sensíveis
        for pattern in self.patterns:
            text = pattern.sub("**REDACTED**", text)
        
        # Aplicar padrões adicionais específicos    
        for pattern, replacement in ADDITIONAL_PATTERNS.items():
            text = re.sub(pattern, replacement, text)
            
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
        
        # Adicionar request_id se disponível
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        # Adicionar a mensagem de log
        if isinstance(record.msg, dict):
            log_data['message'] = record.msg
        else:
            log_data['message'] = record.getMessage()
            
        # Adicionar exceção, se houver
        if record.exc_info:
            exception_type = record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
            exception_value = str(record.exc_info[1]) if record.exc_info[1] else "No message"
            
            log_data['exception'] = {
                'type': exception_type,
                'message': exception_value,
                'traceback': self.formatException(record.exc_info)
            }
            
        # Adicionar extras
        if hasattr(record, 'extras'):
            log_data.update(record.extras)
            
        # Serializar como JSON
        return json.dumps(log_data)


def setup_logging():
    """
    Configura o logging para a aplicação.
    """
    # Configurar nível de log baseado na variável de ambiente ou configuração
    log_level = os.getenv("LOG_LEVEL", settings.LOG_LEVEL).upper()
    log_level_num = getattr(logging, log_level, logging.INFO)
    
    # Criar formatos de log
    simple_format = '%(asctime)s - %(levelname)s - [%(request_id)s] - %(message)s'
    detailed_format = '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(pathname)s:%(lineno)d - %(message)s'
    
    # Configuração básica para logs no console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_num)
    console_formatter = logging.Formatter(simple_format)
    console_handler.setFormatter(console_formatter)
    
    # Configuração para logs de aplicação em arquivo
    app_log_file = os.path.join(LOG_DIR, "app.log")
    app_handler = RotatingFileHandler(
        app_log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    app_handler.setLevel(log_level_num)
    app_formatter = logging.Formatter(detailed_format)
    app_handler.setFormatter(app_formatter)
    
    # Configuração para logs de erro em arquivo separado
    error_log_file = os.path.join(LOG_DIR, "error.log")
    error_handler = RotatingFileHandler(
        error_log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(detailed_format)
    error_handler.setFormatter(error_formatter)
    
    # Configuração para logs em formato JSON
    json_log_file = os.path.join(LOG_DIR, "json.log")
    json_handler = RotatingFileHandler(
        json_log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    json_handler.setLevel(log_level_num)
    json_formatter = JsonFormatter()
    json_handler.setFormatter(json_formatter)
    
    # Adicionar filtro para remover dados sensíveis
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)
    app_handler.addFilter(sensitive_filter)
    error_handler.addFilter(sensitive_filter)
    json_handler.addFilter(sensitive_filter)
    
    # Configurar o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_num)
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Adicionar handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(json_handler)
    
    # Configurar outros loggers específicos
    logging.getLogger("uvicorn").setLevel(log_level_num)
    logging.getLogger("sqlalchemy").setLevel(
        logging.WARNING if log_level_num < logging.WARNING else log_level_num
    )
    
    # Suprimir logs de bibliotecas ruidosas em produção
    if settings.APP_ENV == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Adiciona um filtro de Request-ID ao logger se ainda não tiver
    request_id_filter = next(
        (f for f in logger.filters if isinstance(f, RequestIDFilter)), 
        None
    )
    
    if not request_id_filter:
        logger.addFilter(RequestIDFilter())
    
    return logger


class RequestIDFilter(logging.Filter):
    """Filtro para garantir que request_id esteja sempre presente."""
    
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'no-request-id'
        return True


def log_with_context(logger, level: str, message: str, request_id: str = None, **extra) -> None:
    """
    Registra uma mensagem de log com contexto adicional.
    
    Args:
        logger: Logger para registrar a mensagem
        level: Nível de log (debug, info, warning, error, critical)
        message: Mensagem de log
        request_id: ID da requisição (opcional)
        **extra: Dados adicionais para incluir no log
    """
    if not hasattr(logging, level.lower()):
        level = "info"
    
    # Usar um UUID aleatório se nenhum request_id for fornecido
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    # Criar um dicionário de extras com o request_id
    log_extras = {'request_id': request_id}
    
    # Adicionar extras adicionais
    if extra:
        log_extras.update(extra)
    
    # Registrar a mensagem com o nível apropriado
    log_method = getattr(logger, level.lower())
    
    # Adicionar os extras como atributos
    extra_record = logging.LogRecord(
        name=logger.name,
        level=getattr(logging, level.upper(), logging.INFO),
        pathname='',
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    
    for key, value in log_extras.items():
        setattr(extra_record, key, value)
    
    if 'exc_info' in extra:
        extra_record.exc_info = extra.pop('exc_info')
    
    log_method(message, extra=log_extras)


def get_request_id_from_request(request) -> str:
    """
    Obtém o ID da requisição a partir do objeto de requisição.
    Verifica o cabeçalho X-Request-ID e gera um novo se não existir.

    Args:
        request: Objeto de requisição FastAPI

    Returns:
        ID da requisição
    """
    if hasattr(request.state, 'request_id'):
        return request.state.request_id
    
    # Verificar o cabeçalho X-Request-ID
    request_id = request.headers.get('X-Request-ID')
    
    # Gerar um novo UUID se não existir
    if not request_id:
        request_id = str(uuid.uuid4())
        
    return request_id


# Inicializar o sistema de logging ao importar o módulo
setup_logging() 