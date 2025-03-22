"""
Manipuladores de exceção para a API CCONTROL-M.

Este módulo define manipuladores de exceção globais para padronizar
as respostas de erro em toda a aplicação.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from typing import Dict, List, Union

from app.utils.error_responses import (
    create_error_response,
    ErrorDetail
)
from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manipula exceções de validação do FastAPI.
    
    Transforma erros de validação do Pydantic em respostas de erro padronizadas.
    """
    # Estruturar erros por campo
    error_details: Dict[str, List[str]] = {}
    
    for error in exc.errors():
        # Extrair o campo com erro (último elemento do caminho)
        field = error["loc"][-1] if error["loc"] else "body"
        message = error["msg"]
        
        if field not in error_details:
            error_details[field] = []
            
        error_details[field].append(message)
    
    # Logar o erro
    logger.warning(
        f"Erro de validação: {error_details}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=ErrorDetail.VAL_INVALID_FORMAT,
        message="Erro de validação nos dados enviados",
        details={"fields": error_details}
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Manipula erros de integridade do banco de dados.
    
    Transforma erros de integridade (como violação de chave única) em respostas
    de erro padronizadas.
    """
    # Extrair detalhes do erro
    error_details = str(exc)
    constraint = None
    
    # Tentar extrair o nome da constraint violada
    if "unique constraint" in error_details.lower():
        constraint = error_details.split("constraint")[-1].strip()
    
    # Logar o erro
    logger.error(
        f"Erro de integridade no banco de dados: {error_details}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    return create_error_response(
        status_code=status.HTTP_409_CONFLICT,
        error_code=ErrorDetail.RES_ALREADY_EXISTS,
        message="Erro de integridade nos dados",
        details={
            "reason": "Registro duplicado ou violação de regras de integridade",
            "constraint": constraint
        }
    )


async def database_error_handler(request: Request, exc: DatabaseError):
    """
    Manipula erros gerais do banco de dados.
    
    Transforma erros de banco de dados em respostas de erro padronizadas,
    evitando expor detalhes técnicos.
    """
    # Logar o erro completo para diagnóstico
    logger.error(
        f"Erro de banco de dados: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=ErrorDetail.SYS_DATABASE_ERROR,
        message="Erro interno no banco de dados",
        details={"id": request.state.request_id if hasattr(request.state, "request_id") else None}
    )


def configure_exception_handlers(app):
    """
    Configura manipuladores de exceção globais para a aplicação.
    
    Args:
        app: Instância da aplicação FastAPI
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler) 