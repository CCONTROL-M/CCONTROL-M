import re
import logging
from typing import Dict, List, Any, Pattern, Match

class SensitiveDataFilter(logging.Filter):
    """
    Filtro para mascarar dados sensíveis nos logs.
    """
    
    def __init__(self, patterns: Dict[str, str] = None):
        """
        Inicializa o filtro com padrões de dados sensíveis para mascarar.
        
        Args:
            patterns: Dicionário com padrões regex e seus substitutos
        """
        super().__init__()
        
        # Padrões padrão se nenhum for fornecido
        default_patterns = {
            r'(?i)"password"\s*:\s*"[^"]*"': '"password":"********"',
            r'(?i)"senha"\s*:\s*"[^"]*"': '"senha":"********"',
            r'(?i)"token"\s*:\s*"[^"]*"': '"token":"********"',
            r'(?i)"refresh_token"\s*:\s*"[^"]*"': '"refresh_token":"********"',
            r'(?i)"api_key"\s*:\s*"[^"]*"': '"api_key":"********"',
            r'(?i)"credit_card"\s*:\s*"[^"]*"': '"credit_card":"********"',
            r'(?i)"cartao_credito"\s*:\s*"[^"]*"': '"cartao_credito":"********"',
            r'(?i)"cpf"\s*:\s*"[^"]*"': '"cpf":"***.***.***-**"',
            r'(?i)"cnpj"\s*:\s*"[^"]*"': '"cnpj":"**.***.***/****-**"',
            r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b': '***.***.***-**', # CPF
            r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b': '**.***.***/****-**', # CNPJ
            r'\b(?:\d[ -]*?){13,16}\b': '****-****-****-****', # Cartão de crédito
            r'Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*': 'Bearer *****', # JWT Token
            r'(?i)password=([^&\s]+)': 'password=********',
            r'(?i)senha=([^&\s]+)': 'senha=********',
            r'(?i)token=([^&\s]+)': 'token=********',
            r'(?i)authorization:\s*Bearer\s+([A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*)': 'Authorization: Bearer *****',
        }
        
        # Usar padrões padrão ou combinar com os fornecidos
        self.patterns = default_patterns
        if patterns:
            self.patterns.update(patterns)
            
        # Compilar os padrões regex para melhor performance
        self.compiled_patterns = {
            re.compile(pattern): replacement
            for pattern, replacement in self.patterns.items()
        }
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtra o registro de log, mascarando dados sensíveis.
        
        Args:
            record: Registro de log a ser filtrado
            
        Returns:
            bool: Sempre True para manter o registro no log, mas com dados sensíveis mascarados
        """
        if isinstance(record.msg, str):
            # Aplicar substituições para cada padrão
            for pattern, replacement in self.compiled_patterns.items():
                record.msg = pattern.sub(replacement, record.msg)
                
        # Verificar se há args e processar
        if record.args:
            record.args = self._filter_args(record.args)
            
        # Verificar se há exceção e processar
        if record.exc_info:
            if isinstance(record.exc_info[1], Exception) and hasattr(record.exc_info[1], 'args'):
                # Filtrar argumentos da exceção se forem strings
                exc_args = list(record.exc_info[1].args)
                for i, arg in enumerate(exc_args):
                    if isinstance(arg, str):
                        for pattern, replacement in self.compiled_patterns.items():
                            exc_args[i] = pattern.sub(replacement, arg)
                
                # Substituir argumentos da exceção
                record.exc_info[1].args = tuple(exc_args)
                
        return True
    
    def _filter_args(self, args: Any) -> Any:
        """
        Filtra recursivamente os argumentos do registro de log.
        
        Args:
            args: Argumentos a serem filtrados
            
        Returns:
            Any: Argumentos filtrados
        """
        if isinstance(args, str):
            # Para strings, aplicar todas as substituições
            result = args
            for pattern, replacement in self.compiled_patterns.items():
                result = pattern.sub(replacement, result)
            return result
            
        elif isinstance(args, dict):
            # Para dicionários, processar cada valor
            return {k: self._filter_args(v) for k, v in args.items()}
            
        elif isinstance(args, (list, tuple)):
            # Para listas e tuplas, processar cada item
            return type(args)(self._filter_args(arg) for arg in args)
            
        elif hasattr(args, '__dict__'):
            # Para objetos, processar atributos
            for attr_name, attr_value in vars(args).items():
                if isinstance(attr_value, str):
                    setattr(args, attr_name, self._filter_args(attr_value))
            return args
            
        # Para outros tipos, retornar sem alterações
        return args 