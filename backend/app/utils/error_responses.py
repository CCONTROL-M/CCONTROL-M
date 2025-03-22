"""
Utilitário para gerar respostas de erro padronizadas.

Este módulo fornece funções para criar respostas de erro padronizadas
seguindo o catálogo de erros do CCONTROL-M, garantindo consistência
nas mensagens de erro retornadas pela API.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Modelo para respostas de erro padronizadas."""
    status_code: int
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


class ErrorDetail:
    """
    Catálogo de códigos de erro da aplicação.
    
    Agrupa os códigos de erro por categoria para facilitar a referência.
    """
    
    # Autenticação e Autorização
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_INSUFFICIENT_PERM = "AUTH_INSUFFICIENT_PERM"
    AUTH_ACCOUNT_LOCKED = "AUTH_ACCOUNT_LOCKED"
    AUTH_ACCOUNT_INACTIVE = "AUTH_ACCOUNT_INACTIVE"
    
    # Validação de Dados
    VAL_REQUIRED_FIELD = "VAL_REQUIRED_FIELD"
    VAL_INVALID_FORMAT = "VAL_INVALID_FORMAT"
    VAL_INVALID_LENGTH = "VAL_INVALID_LENGTH"
    VAL_INVALID_VALUE = "VAL_INVALID_VALUE"
    VAL_INVALID_DATE = "VAL_INVALID_DATE"
    VAL_INVALID_DOCUMENT = "VAL_INVALID_DOCUMENT"
    
    # Recursos
    RES_NOT_FOUND = "RES_NOT_FOUND"
    RES_ALREADY_EXISTS = "RES_ALREADY_EXISTS"
    RES_LOCKED = "RES_LOCKED"
    RES_RELATED_EXISTS = "RES_RELATED_EXISTS"
    RES_INVALID_STATUS = "RES_INVALID_STATUS"
    RES_VERSION_CONFLICT = "RES_VERSION_CONFLICT"
    
    # Negócio
    BIZ_INSUFFICIENT_STOCK = "BIZ_INSUFFICIENT_STOCK"
    BIZ_INVALID_PAYMENT = "BIZ_INVALID_PAYMENT"
    BIZ_ORDER_COMPLETED = "BIZ_ORDER_COMPLETED"
    BIZ_CREDIT_LIMIT = "BIZ_CREDIT_LIMIT"
    BIZ_INVALID_OPERATION = "BIZ_INVALID_OPERATION"
    BIZ_INVALID_DISCOUNT = "BIZ_INVALID_DISCOUNT"
    
    # Sistema
    SYS_DATABASE_ERROR = "SYS_DATABASE_ERROR"
    SYS_INTEGRATION_ERROR = "SYS_INTEGRATION_ERROR"
    SYS_MAINTENANCE = "SYS_MAINTENANCE"
    SYS_RATE_LIMITED = "SYS_RATE_LIMITED"
    SYS_RESOURCE_EXHAUSTED = "SYS_RESOURCE_EXHAUSTED"
    SYS_INTERNAL_ERROR = "SYS_INTERNAL_ERROR"


# Mapeamento de códigos de erro HTTP para descrições
HTTP_STATUS_DESCRIPTIONS = {
    status.HTTP_400_BAD_REQUEST: "Requisição inválida",
    status.HTTP_401_UNAUTHORIZED: "Não autorizado",
    status.HTTP_403_FORBIDDEN: "Acesso negado",
    status.HTTP_404_NOT_FOUND: "Recurso não encontrado",
    status.HTTP_409_CONFLICT: "Conflito",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "Erro de validação",
    status.HTTP_429_TOO_MANY_REQUESTS: "Muitas requisições",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Erro interno do servidor",
    status.HTTP_503_SERVICE_UNAVAILABLE: "Serviço indisponível",
}


def create_error_response(
    status_code: int, 
    error_code: str, 
    message: Optional[str] = None, 
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Cria uma resposta de erro padronizada.
    
    Args:
        status_code: Código HTTP do erro
        error_code: Código de erro específico da aplicação
        message: Mensagem descritiva do erro (opcional, usa descrição padrão se não fornecida)
        details: Detalhes adicionais sobre o erro (opcional)
        
    Returns:
        JSONResponse padronizada com os detalhes do erro
    """
    if message is None:
        message = HTTP_STATUS_DESCRIPTIONS.get(
            status_code, "Erro na requisição"
        )
    
    error_content = {
        "status_code": status_code,
        "message": message,
        "error_code": error_code,
    }
    
    if details:
        error_content["details"] = details
        
    return JSONResponse(
        status_code=status_code,
        content=error_content
    )


def create_http_exception(
    status_code: int, 
    error_code: str, 
    message: Optional[str] = None, 
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Cria uma exceção HTTP padronizada para ser lançada.
    
    Args:
        status_code: Código HTTP do erro
        error_code: Código de erro específico da aplicação
        message: Mensagem descritiva do erro (opcional, usa descrição padrão se não fornecida)
        details: Detalhes adicionais sobre o erro (opcional)
        
    Returns:
        HTTPException configurada com a mensagem e os detalhes de erro
    """
    if message is None:
        message = HTTP_STATUS_DESCRIPTIONS.get(
            status_code, "Erro na requisição"
        )
    
    error_content = {
        "status_code": status_code,
        "message": message,
        "error_code": error_code,
    }
    
    if details:
        error_content["details"] = details
        
    return HTTPException(
        status_code=status_code,
        detail=error_content
    )


# Funções de conveniência para erros comuns

def resource_not_found(
    resource_type: str, 
    resource_id: Union[str, int, UUID], 
    additional_details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Cria uma exceção para recurso não encontrado.
    
    Args:
        resource_type: Tipo de recurso (ex: 'cliente', 'produto')
        resource_id: ID do recurso não encontrado
        additional_details: Detalhes adicionais sobre o erro (opcional)
        
    Returns:
        HTTPException configurada com código 404 e detalhes do recurso
    """
    details = {
        "resource_type": resource_type,
        "resource_id": str(resource_id)
    }
    
    if additional_details:
        details.update(additional_details)
        
    return create_http_exception(
        status.HTTP_404_NOT_FOUND,
        ErrorDetail.RES_NOT_FOUND,
        f"{resource_type.capitalize()} não encontrado com ID: {resource_id}",
        details
    )


def validation_error(
    errors: Dict[str, List[str]]
) -> HTTPException:
    """
    Cria uma exceção para erro de validação de dados.
    
    Args:
        errors: Dicionário com campo e lista de erros
        
    Returns:
        HTTPException configurada com código 422 e detalhes dos erros de validação
    """
    return create_http_exception(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorDetail.VAL_INVALID_FORMAT,
        "Erro de validação nos dados enviados",
        {"fields": errors}
    )


def insufficient_permissions(
    required_permission: str,
    resource: Optional[str] = None
) -> HTTPException:
    """
    Cria uma exceção para permissões insuficientes.
    
    Args:
        required_permission: Permissão necessária (ex: 'criar', 'editar')
        resource: Recurso que exige a permissão (ex: 'clientes', 'vendas')
        
    Returns:
        HTTPException configurada com código 403 e detalhes da permissão
    """
    details = {"required_permission": required_permission}
    
    if resource:
        details["resource"] = resource
        message = f"Permissão insuficiente para {required_permission} em {resource}"
    else:
        message = f"Permissão insuficiente: {required_permission}"
        
    return create_http_exception(
        status.HTTP_403_FORBIDDEN,
        ErrorDetail.AUTH_INSUFFICIENT_PERM,
        message,
        details
    )


def resource_already_exists(
    resource_type: str,
    identifier: Dict[str, Any]
) -> HTTPException:
    """
    Cria uma exceção para recurso já existente.
    
    Args:
        resource_type: Tipo de recurso (ex: 'cliente', 'produto')
        identifier: Identificadores únicos que causaram o conflito
        
    Returns:
        HTTPException configurada com código 409 e detalhes do conflito
    """
    return create_http_exception(
        status.HTTP_409_CONFLICT,
        ErrorDetail.RES_ALREADY_EXISTS,
        f"{resource_type.capitalize()} já existe com os dados fornecidos",
        {"conflict_fields": identifier}
    ) 