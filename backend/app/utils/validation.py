"""
Utilitários de validação robusta para o sistema CCONTROL-M.

Este módulo implementa funções para validação de dados de entrada,
verificação de formato e sanitização de dados.
"""
import re
import json
from typing import Any, Dict, List, Union, Optional, Pattern, Callable
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from uuid import UUID
import unicodedata

from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Expressões regulares para validação
REGEX_PATTERNS = {
    "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    "cpf": re.compile(r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$"),
    "cnpj": re.compile(r"^\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}$"),
    "phone": re.compile(r"^\(?(?:[14689][1-9]|2[12478]|3[1234578]|5[1345]|7[134579])\)? ?(?:[2-8]|9[1-9])[0-9]{3}(?:-| )?[0-9]{4}$"),
    "cep": re.compile(r"^\d{5}-?\d{3}$"),
    "date": re.compile(r"^(?:19|20)\d\d[- /.](?:0[1-9]|1[012])[- /.](?:0[1-9]|[12][0-9]|3[01])$"),
    "credit_card": re.compile(r"^\d{4}(?:[ -]?\d{4}){3}$"),
    "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.IGNORECASE)
}

# Padrões para detecção de ataques
ATTACK_PATTERNS = {
    "sql_injection": [
        re.compile(r"(\b(select|insert|update|delete|drop|alter|create|truncate|declare)\b|\b(from|where|group by|order by)\b|--|;|\bor\b|\band\b)", re.IGNORECASE),
        re.compile(r"(\%27|\'|\"|\%22)", re.IGNORECASE)
    ],
    "xss": [
        re.compile(r"(<script|javascript:|on\w+\s*=|alert\(|confirm\(|prompt\(|\beval\b|\bexec\b|<iframe|<embed|<object)", re.IGNORECASE),
        re.compile(r"((\%3C)|<)[^\n]+((\%3E)|>)", re.IGNORECASE)
    ],
    "command_injection": [
        re.compile(r"(;|\||`|\\|&|\^)", re.IGNORECASE)
    ],
    "path_traversal": [
        re.compile(r"(\.\.\/|\.\.\\)")
    ]
}


def is_valid_email(email: str) -> bool:
    """
    Verifica se um endereço de e-mail é válido.
    
    Args:
        email: O endereço de e-mail a verificar
        
    Returns:
        Booleano indicando se o endereço é válido
    """
    if not email or not isinstance(email, str):
        return False
        
    return bool(REGEX_PATTERNS["email"].match(email))


def is_valid_cpf(cpf: str) -> bool:
    """
    Verifica se um CPF é válido, incluindo validação de dígitos verificadores.
    
    Args:
        cpf: O número de CPF a verificar (com ou sem pontuação)
        
    Returns:
        Booleano indicando se o CPF é válido
    """
    if not cpf or not isinstance(cpf, str):
        return False
        
    # Remover caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verificar se tem 11 dígitos
    if len(cpf) != 11:
        return False
        
    # Verificar se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        return False
        
    # Calcular dígitos verificadores
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    
    # Verificar dígitos calculados
    return cpf[9] == str(dv1) and cpf[10] == str(dv2)


def is_valid_cnpj(cnpj: str) -> bool:
    """
    Verifica se um CNPJ é válido, incluindo validação de dígitos verificadores.
    
    Args:
        cnpj: O número de CNPJ a verificar (com ou sem pontuação)
        
    Returns:
        Booleano indicando se o CNPJ é válido
    """
    if not cnpj or not isinstance(cnpj, str):
        return False
        
    # Remover caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    # Verificar se tem 14 dígitos
    if len(cnpj) != 14:
        return False
        
    # Verificar se todos os dígitos são iguais
    if len(set(cnpj)) == 1:
        return False
        
    # Verificar dígito verificador 1
    multiplicadores = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(12):
        soma += int(cnpj[i]) * multiplicadores[i]
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    
    # Verificar dígito verificador 2
    multiplicadores = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(13):
        soma += int(cnpj[i]) * multiplicadores[i]
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    
    # Verificar dígitos calculados
    return cnpj[12] == str(dv1) and cnpj[13] == str(dv2)


def is_valid_phone(phone: str) -> bool:
    """
    Verifica se um número de telefone brasileiro é válido.
    
    Args:
        phone: O número de telefone a verificar
        
    Returns:
        Booleano indicando se o telefone é válido
    """
    if not phone or not isinstance(phone, str):
        return False
        
    # Remover caracteres não numéricos
    phone = ''.join(filter(str.isdigit, phone))
    
    # Verificar comprimento (8 a 11 dígitos)
    if len(phone) < 8 or len(phone) > 11:
        return False
        
    # Ajustar para adicionar DDD se necessário
    if len(phone) == 8 or len(phone) == 9:
        return REGEX_PATTERNS["phone"].match(f"11{phone}") is not None
        
    return REGEX_PATTERNS["phone"].match(phone) is not None


def is_valid_date(date_str: str, formats: List[str] = None) -> bool:
    """
    Verifica se uma string representa uma data válida.
    
    Args:
        date_str: A string contendo a data
        formats: Lista de formatos para tentar parsear (padrão: ['%Y-%m-%d', '%d/%m/%Y'])
        
    Returns:
        Booleano indicando se a data é válida
    """
    if not date_str or not isinstance(date_str, str):
        return False
        
    if not formats:
        formats = ['%Y-%m-%d', '%d/%m/%Y']
        
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
            
    return False


def is_valid_decimal(value: Any) -> bool:
    """
    Verifica se um valor pode ser convertido para Decimal.
    
    Args:
        value: O valor a ser verificado
        
    Returns:
        Booleano indicando se o valor é válido
    """
    if value is None:
        return False
        
    try:
        Decimal(str(value).replace(',', '.'))
        return True
    except (InvalidOperation, ValueError, TypeError):
        return False


def is_valid_uuid(uuid_str: str) -> bool:
    """
    Verifica se uma string é um UUID válido.
    
    Args:
        uuid_str: A string contendo o UUID
        
    Returns:
        Booleano indicando se o UUID é válido
    """
    if not uuid_str or not isinstance(uuid_str, str):
        return False
        
    try:
        UUID(uuid_str)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Sanitiza uma string, removendo caracteres potencialmente perigosos.
    
    Args:
        value: A string a ser sanitizada
        max_length: Comprimento máximo permitido (None para sem limite)
        
    Returns:
        String sanitizada
    """
    if not value or not isinstance(value, str):
        return ""
    
    # Normalizar para remover caracteres especiais
    normalized = unicodedata.normalize('NFKD', value)
    sanitized = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # Remover caracteres potencialmente perigosos
    sanitized = re.sub(r'[^\w\s\-.,;:@()[\]/]', '', sanitized)
    
    # Truncar se necessário
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        
    return sanitized


def detect_attack_patterns(value: str) -> List[str]:
    """
    Detecta padrões de ataque em uma string.
    
    Args:
        value: A string a verificar
        
    Returns:
        Lista com os tipos de ataque detectados (vazia se nenhum)
    """
    if not value or not isinstance(value, str):
        return []
        
    attacks = []
    
    for attack_type, patterns in ATTACK_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(value):
                attacks.append(attack_type)
                break  # Não precisamos verificar mais padrões deste tipo
                
    return attacks


def validate_json_structure(json_data: Dict, schema: Dict) -> Dict[str, List[str]]:
    """
    Valida a estrutura de um dicionário JSON contra um esquema.
    
    Args:
        json_data: O dicionário JSON a validar
        schema: O esquema de validação, no formato:
            {
                "campo": {
                    "type": "string|number|boolean|object|array",
                    "required": True|False,
                    "max_length": int,
                    "validators": [callable1, callable2]
                }
            }
            
    Returns:
        Dicionário com erros de validação por campo
    """
    errors = {}
    
    for field, rules in schema.items():
        field_type = rules.get("type", "string")
        required = rules.get("required", False)
        validators = rules.get("validators", [])
        
        # Verificar se campo obrigatório está presente
        if required and (field not in json_data or json_data[field] is None):
            errors[field] = ["Campo obrigatório"]
            continue
            
        # Pular validação de campos ausentes, mas não obrigatórios
        if field not in json_data or json_data[field] is None:
            continue
            
        value = json_data[field]
        
        # Validar tipo
        type_valid = False
        if field_type == "string" and isinstance(value, str):
            type_valid = True
        elif field_type == "number" and (isinstance(value, (int, float, Decimal)) or 
                                        (isinstance(value, str) and is_valid_decimal(value))):
            type_valid = True
        elif field_type == "boolean" and (isinstance(value, bool) or 
                                           value in ('true', 'false', '0', '1')):
            type_valid = True
        elif field_type == "object" and isinstance(value, dict):
            type_valid = True
        elif field_type == "array" and isinstance(value, list):
            type_valid = True
            
        if not type_valid:
            errors[field] = [f"Tipo inválido, esperado: {field_type}"]
            continue
            
        # Aplicar validadores específicos de campo
        field_errors = []
        for validator in validators:
            if not validator(value):
                # Determinar mensagem de erro pelo nome da função
                if validator.__name__ == "is_valid_email":
                    field_errors.append("Email inválido")
                elif validator.__name__ == "is_valid_cpf":
                    field_errors.append("CPF inválido")
                elif validator.__name__ == "is_valid_cnpj":
                    field_errors.append("CNPJ inválido")
                elif validator.__name__ == "is_valid_phone":
                    field_errors.append("Telefone inválido")
                elif validator.__name__ == "is_valid_date":
                    field_errors.append("Data inválida")
                else:
                    field_errors.append("Valor inválido")
                    
        if field_errors:
            errors[field] = field_errors
            
        # Validar tamanho máximo para strings
        if field_type == "string" and "max_length" in rules and len(value) > rules["max_length"]:
            if field not in errors:
                errors[field] = []
            errors[field].append(f"Máximo de {rules['max_length']} caracteres permitidos")
            
        # Validar valores mínimo e máximo para números
        if field_type == "number":
            num_value = Decimal(str(value).replace(',', '.'))
            if "min_value" in rules and num_value < Decimal(str(rules["min_value"])):
                if field not in errors:
                    errors[field] = []
                errors[field].append(f"Valor mínimo permitido: {rules['min_value']}")
                
            if "max_value" in rules and num_value > Decimal(str(rules["max_value"])):
                if field not in errors:
                    errors[field] = []
                errors[field].append(f"Valor máximo permitido: {rules['max_value']}")
                
    return errors


def validate_input(data: Any, validation_rules: List[Callable], error_message: str = None) -> Optional[str]:
    """
    Valida uma entrada utilizando uma lista de funções de validação.
    
    Args:
        data: O dado a ser validado
        validation_rules: Lista de funções de validação que retornam booleano
        error_message: Mensagem de erro personalizada
        
    Returns:
        Mensagem de erro se a validação falhar, None se for válido
    """
    for validator in validation_rules:
        if not validator(data):
            return error_message or "Dados de entrada inválidos"
            
    return None


def has_attack_input(data: Dict) -> bool:
    """
    Verifica se um dicionário contém entradas com padrões de ataque.
    
    Args:
        data: Dicionário a verificar
        
    Returns:
        Booleano indicando se padrões de ataque foram encontrados
    """
    if not data or not isinstance(data, dict):
        return False
        
    def check_value(value):
        if isinstance(value, str):
            return bool(detect_attack_patterns(value))
        elif isinstance(value, dict):
            return has_attack_input(value)
        elif isinstance(value, list):
            return any(check_value(item) for item in value)
        return False
        
    return any(check_value(value) for value in data.values())


def validate_url_params(params: Dict, allowed_params: List[str]) -> bool:
    """
    Verifica se todos os parâmetros de URL são permitidos.
    
    Args:
        params: Dicionário de parâmetros
        allowed_params: Lista de parâmetros permitidos
        
    Returns:
        Booleano indicando se todos os parâmetros são permitidos
    """
    return all(param in allowed_params for param in params.keys()) 