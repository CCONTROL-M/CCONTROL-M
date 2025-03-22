"""
Dependências para validação robusta de dados em endpoints.
"""
from fastapi import Request, HTTPException, status, Depends
from typing import Callable, Any, Dict, Type, Optional
from pydantic import BaseModel, ValidationError
import inspect
import functools
import json
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

def validate_request_body(model: Type[BaseModel]) -> Callable:
    """
    Dependência para validação robusta do corpo da requisição.
    
    Args:
        model: Classe do modelo Pydantic para validação
        
    Returns:
        Dependência para uso com FastAPI
    """
    async def dependency(request: Request) -> BaseModel:
        try:
            # Extrair corpo como JSON
            body = await request.json()
            
            # Validar o corpo com o modelo Pydantic
            validated_data = model(**body)
            
            # Adicionar os dados validados ao state da requisição
            request.state.validated_data = validated_data
            
            return validated_data
        except json.JSONDecodeError:
            logger.warning(f"JSON inválido na requisição: {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON inválido no corpo da requisição"
            )
        except ValidationError as e:
            # Registrar o erro de validação
            logger.warning(f"Erro de validação: {str(e)}")
            
            # Extrair e formatar os erros para uma resposta amigável
            errors = e.errors()
            formatted_errors = []
            
            for error in errors:
                loc = ".".join(str(x) for x in error["loc"])
                formatted_errors.append({
                    "field": loc,
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            # Retornar resposta detalhada do erro
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erro de validação de dados",
                    "errors": formatted_errors
                }
            )
    
    return dependency

def validate_query_params(model: Type[BaseModel]) -> Callable:
    """
    Dependência para validação robusta dos parâmetros de consulta.
    
    Args:
        model: Classe do modelo Pydantic para validação
        
    Returns:
        Dependência para uso com FastAPI
    """
    async def dependency(request: Request) -> BaseModel:
        try:
            # Extrair parâmetros de consulta como dicionário
            query_params = dict(request.query_params)
            
            # Validar os parâmetros com o modelo Pydantic
            validated_data = model(**query_params)
            
            # Adicionar os dados validados ao state da requisição
            request.state.validated_query = validated_data
            
            return validated_data
        except ValidationError as e:
            # Registrar o erro de validação
            logger.warning(f"Erro de validação nos parâmetros de consulta: {str(e)}")
            
            # Extrair e formatar os erros para uma resposta amigável
            errors = e.errors()
            formatted_errors = []
            
            for error in errors:
                loc = ".".join(str(x) for x in error["loc"])
                formatted_errors.append({
                    "field": loc,
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            # Retornar resposta detalhada do erro
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erro de validação nos parâmetros de consulta",
                    "errors": formatted_errors
                }
            )
    
    return dependency

def validate_path_params(model: Type[BaseModel]) -> Callable:
    """
    Dependência para validação robusta dos parâmetros de caminho.
    
    Args:
        model: Classe do modelo Pydantic para validação
        
    Returns:
        Dependência para uso com FastAPI
    """
    async def dependency(request: Request) -> BaseModel:
        try:
            # Extrair parâmetros de caminho como dicionário
            path_params = dict(request.path_params)
            
            # Validar os parâmetros com o modelo Pydantic
            validated_data = model(**path_params)
            
            # Adicionar os dados validados ao state da requisição
            request.state.validated_path = validated_data
            
            return validated_data
        except ValidationError as e:
            # Registrar o erro de validação
            logger.warning(f"Erro de validação nos parâmetros de caminho: {str(e)}")
            
            # Extrair e formatar os erros para uma resposta amigável
            errors = e.errors()
            formatted_errors = []
            
            for error in errors:
                loc = ".".join(str(x) for x in error["loc"])
                formatted_errors.append({
                    "field": loc,
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            # Retornar resposta detalhada do erro
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Erro de validação nos parâmetros de caminho",
                    "errors": formatted_errors
                }
            )
    
    return dependency

def robust_validation(
    body_model: Optional[Type[BaseModel]] = None,
    query_model: Optional[Type[BaseModel]] = None,
    path_model: Optional[Type[BaseModel]] = None
) -> Callable:
    """
    Decorator para aplicar validação robusta aos parâmetros da requisição.
    
    Args:
        body_model: Modelo para validação do corpo da requisição
        query_model: Modelo para validação dos parâmetros de consulta
        path_model: Modelo para validação dos parâmetros de caminho
        
    Returns:
        Decorator para aplicar às funções de endpoint
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), 
                           kwargs.get('request'))
            
            if not request:
                for name, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                # Se não encontrar a requisição, apenas executa a função original
                return await func(*args, **kwargs)
            
            # Aplicar validações conforme necessário
            if body_model:
                body_validator = validate_request_body(body_model)
                validated_body = await body_validator(request)
                kwargs['validated_body'] = validated_body
            
            if query_model:
                query_validator = validate_query_params(query_model)
                validated_query = await query_validator(request)
                kwargs['validated_query'] = validated_query
            
            if path_model:
                path_validator = validate_path_params(path_model)
                validated_path = await path_validator(request)
                kwargs['validated_path'] = validated_path
            
            # Executar a função original
            return await func(*args, **kwargs)
        
        # Atualize as assinaturas para documentação
        sig = inspect.signature(func)
        parameters = list(sig.parameters.values())
        
        # Adicione os parâmetros validados à assinatura
        for name, model in [
            ('validated_body', body_model),
            ('validated_query', query_model),
            ('validated_path', path_model)
        ]:
            if model:
                param = inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation=model,
                    default=Depends()
                )
                parameters.append(param)
        
        # Atualize a assinatura da função wrapper
        wrapper.__signature__ = sig.replace(parameters=parameters)
        
        return wrapper
    
    return decorator 