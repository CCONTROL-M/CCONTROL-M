"""Funções de validação para diversos tipos de dados do sistema."""
import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError


def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF.
    
    Args:
        cpf: String contendo o CPF a ser validado
        
    Returns:
        bool: True se CPF válido, False caso contrário
    """
    # Remover caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verificar se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Verificar primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False
    
    # Verificar segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[10]):
        return False
    
    return True


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida um CNPJ.
    
    Args:
        cnpj: String contendo o CNPJ a ser validado
        
    Returns:
        bool: True se CNPJ válido, False caso contrário
    """
    # Remover caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verificar se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verificar se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Verificar primeiro dígito verificador
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(12):
        soma += int(cnpj[i]) * pesos[i]
    resto = soma % 11
    if resto < 2:
        dv1 = 0
    else:
        dv1 = 11 - resto
    if dv1 != int(cnpj[12]):
        return False
    
    # Verificar segundo dígito verificador
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(13):
        soma += int(cnpj[i]) * pesos[i]
    resto = soma % 11
    if resto < 2:
        dv2 = 0
    else:
        dv2 = 11 - resto
    if dv2 != int(cnpj[13]):
        return False
    
    return True


def validar_cpf_cnpj(documento: str) -> bool:
    """
    Valida um CPF ou CNPJ.
    
    Args:
        documento: String contendo o CPF ou CNPJ a ser validado
        
    Returns:
        bool: True se documento válido, False caso contrário
    """
    # Remover caracteres não numéricos
    documento = re.sub(r'[^0-9]', '', documento)
    
    # Verificar se é CPF ou CNPJ pelo tamanho
    if len(documento) == 11:
        return validar_cpf(documento)
    elif len(documento) == 14:
        return validar_cnpj(documento)
    
    return False


def validar_email(email: str) -> bool:
    """
    Valida um endereço de email usando expressão regular.
    
    Args:
        email: String contendo o email a ser validado
        
    Returns:
        bool: True se email válido, False caso contrário
    """
    # Expressão regular para validação de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))


def validar_telefone(telefone: str) -> bool:
    """
    Valida um número de telefone brasileiro.
    
    Args:
        telefone: String contendo o telefone a ser validado
        
    Returns:
        bool: True se telefone válido, False caso contrário
    """
    # Remover caracteres não numéricos
    telefone = re.sub(r'[^0-9]', '', telefone)
    
    # Verificar se tem entre 10 e 11 dígitos (DDD + número)
    return len(telefone) >= 10 and len(telefone) <= 11


def formatar_cpf(cpf: str) -> str:
    """
    Formata um CPF para o padrão XXX.XXX.XXX-XX.
    
    Args:
        cpf: String contendo o CPF a ser formatado
        
    Returns:
        str: CPF formatado
    """
    # Remover caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verificar se tem 11 dígitos
    if len(cpf) != 11:
        return cpf
    
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata um CNPJ para o padrão XX.XXX.XXX/XXXX-XX.
    
    Args:
        cnpj: String contendo o CNPJ a ser formatado
        
    Returns:
        str: CNPJ formatado
    """
    # Remover caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verificar se tem 14 dígitos
    if len(cnpj) != 14:
        return cnpj
    
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def validar_cnpj_fornecedor(cnpj: str) -> bool:
    """
    Valida um CNPJ de fornecedor.
    
    Args:
        cnpj: String contendo o CNPJ a ser validado
        
    Returns:
        bool: True se CNPJ válido, False caso contrário
    """
    # Remover caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verificar se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verificar se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Verificar primeiro dígito verificador
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(12):
        soma += int(cnpj[i]) * pesos[i]
    resto = soma % 11
    if resto < 2:
        dv1 = 0
    else:
        dv1 = 11 - resto
    if dv1 != int(cnpj[12]):
        return False
    
    # Verificar segundo dígito verificador
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = 0
    for i in range(13):
        soma += int(cnpj[i]) * pesos[i]
    resto = soma % 11
    if resto < 2:
        dv2 = 0
    else:
        dv2 = 11 - resto
    if dv2 != int(cnpj[13]):
        return False
    
    return True


def validar_email_fornecedor(email: str) -> bool:
    """
    Valida um email de fornecedor.
    
    Args:
        email: String contendo o email a ser validado
        
    Returns:
        bool: True se email válido, False caso contrário
    """
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def formatar_cpf_cnpj(documento: str) -> str:
    """
    Formata um CPF ou CNPJ para o padrão adequado.
    
    Args:
        documento: String contendo o CPF ou CNPJ a ser formatado
        
    Returns:
        str: Documento formatado
    """
    # Remover caracteres não numéricos
    documento = re.sub(r'[^0-9]', '', documento)
    
    # Verificar se é CPF ou CNPJ pelo tamanho
    if len(documento) == 11:
        return formatar_cpf(documento)
    elif len(documento) == 14:
        return formatar_cnpj(documento)
    
    return documento 