"""
Validadores para documentos e outros dados específicos do Brasil.

Este módulo contém funções de validação para uso em modelos Pydantic.
"""
from typing import Optional, Union
from validate_docbr import CPF, CNPJ
import re

# Instâncias dos validadores
_cpf = CPF()
_cnpj = CNPJ()


def validar_cpf(valor: str) -> str:
    """
    Valida um CPF.
    
    Args:
        valor: String contendo o CPF a ser validado
        
    Returns:
        String do CPF formatado (apenas números)
        
    Raises:
        ValueError: Se o CPF for inválido
    """
    # Remover formatação para validação
    valor_limpo = re.sub(r'[^\d]', '', valor)
    
    # Verificar se o CPF é válido
    if not _cpf.validate(valor_limpo):
        raise ValueError("CPF inválido")
    
    return valor_limpo


def validar_cnpj(valor: str) -> str:
    """
    Valida um CNPJ.
    
    Args:
        valor: String contendo o CNPJ a ser validado
        
    Returns:
        String do CNPJ formatado (apenas números)
        
    Raises:
        ValueError: Se o CNPJ for inválido
    """
    # Remover formatação para validação
    valor_limpo = re.sub(r'[^\d]', '', valor)
    
    # Verificar se o CNPJ é válido
    if not _cnpj.validate(valor_limpo):
        raise ValueError("CNPJ inválido")
    
    return valor_limpo


def validar_cpf_cnpj(valor: str) -> str:
    """
    Valida um documento que pode ser CPF ou CNPJ.
    
    Args:
        valor: String contendo o documento a ser validado
        
    Returns:
        String do documento formatado (apenas números)
        
    Raises:
        ValueError: Se o documento não for um CPF ou CNPJ válido
    """
    # Remover formatação para validação
    valor_limpo = re.sub(r'[^\d]', '', valor)
    
    # Verificar se é um CPF (11 dígitos) ou CNPJ (14 dígitos)
    if len(valor_limpo) == 11:
        if not _cpf.validate(valor_limpo):
            raise ValueError("CPF inválido")
    elif len(valor_limpo) == 14:
        if not _cnpj.validate(valor_limpo):
            raise ValueError("CNPJ inválido")
    else:
        raise ValueError("Documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos)")
    
    return valor_limpo


def formatar_cpf(cpf: str) -> str:
    """
    Formata um CPF para exibição (XXX.XXX.XXX-XX).
    
    Args:
        cpf: String contendo o CPF a ser formatado
        
    Returns:
        String do CPF formatado
    """
    # Remover formatação existente primeiro
    cpf_limpo = re.sub(r'[^\d]', '', cpf)
    
    return _cpf.mask(cpf_limpo)


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata um CNPJ para exibição (XX.XXX.XXX/XXXX-XX).
    
    Args:
        cnpj: String contendo o CNPJ a ser formatado
        
    Returns:
        String do CNPJ formatado
    """
    # Remover formatação existente primeiro
    cnpj_limpo = re.sub(r'[^\d]', '', cnpj)
    
    return _cnpj.mask(cnpj_limpo)


def formatar_cpf_cnpj(documento: str) -> str:
    """
    Formata um documento (CPF ou CNPJ) para exibição.
    
    Args:
        documento: String contendo o documento a ser formatado
        
    Returns:
        String do documento formatado
    """
    # Remover formatação existente primeiro
    doc_limpo = re.sub(r'[^\d]', '', documento)
    
    if len(doc_limpo) == 11:
        return _cpf.mask(doc_limpo)
    elif len(doc_limpo) == 14:
        return _cnpj.mask(doc_limpo)
    else:
        return documento  # Retorna o valor original se não for CPF nem CNPJ 