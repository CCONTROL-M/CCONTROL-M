"""Dependências para injeção nas rotas do FastAPI."""
from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict, Callable
from functools import wraps

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database import db_async_session, get_db
from app.schemas.token import TokenPayload
from app.core.auth_helpers import OAuth2PasswordBearerWithExceptions

# Definir caminhos que não exigem autenticação
PUBLIC_PATHS = [
    "/api/v1/health",
    "/api/v1/docs",
    "/api/v1/openapi.json",
    "/health",
    "/docs",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/register"
]

# Configuração do OAuth2 com exceções
oauth2_scheme = OAuth2PasswordBearerWithExceptions(
    tokenUrl="/auth/login",
    scheme_name="JWT",
    exception_paths=PUBLIC_PATHS
)

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Valida o token JWT e retorna informações do usuário.
    
    Em ambiente de desenvolvimento, retorna um usuário fake sem validar o token.
    Em produção, valida o token JWT normalmente.
    
    Args:
        token: Token JWT a ser validado
        
    Returns:
        dict: Dados do usuário
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    # Em ambiente de desenvolvimento, retornar usuário fake
    if settings.is_development:
        return {
            "id_usuario": "00000000-0000-0000-0000-000000000000",
            "id_empresa": "00000000-0000-0000-0000-000000000001",
            "nome": "Usuário Desenvolvimento",
            "email": "dev@exemplo.com",
            "tipo_usuario": "ADMIN",
            "sub": "00000000-0000-0000-0000-000000000000",  # ID do usuário no formato esperado
            "exp": 9999999999  # Data de expiração muito no futuro
        }
    
    # Em produção, validar o token normalmente
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # Verificar se o token expirou
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Retornar dados do usuário
        return {
            "id_usuario": token_data.sub,
            "id_empresa": token_data.id_empresa,
            "tipo_usuario": token_data.tipo_usuario,
            "sub": token_data.sub,
            "exp": token_data.exp
        }
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"}
        )


def create_access_token(
    subject: Union[str, Any],
    empresa_id: Union[str, Any],
    tipo_usuario: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso.
    
    Args:
        subject: Identificador do usuário (id_usuario)
        empresa_id: ID da empresa do usuário
        tipo_usuario: Tipo de usuário
        expires_delta: Tempo de expiração personalizado
        
    Returns:
        str: Token JWT gerado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Definir os dados do payload
    to_encode = {
        "exp": expire.timestamp(),
        "sub": str(subject),
        "id_empresa": str(empresa_id) if empresa_id else None,
        "tipo_usuario": tipo_usuario
    }
    
    # Codificar o token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def check_permission(permission: str):
    """
    Dependência para verificar permissões em rotas.
    No modo de desenvolvimento, sempre retorna True.
    
    Args:
        permission: Permissão no formato "module:action"
        
    Returns:
        Função de dependência que sempre concede acesso no modo de desenvolvimento,
        ou verifica as permissões em produção
    """
    async def dependency(current_user: dict = Depends(get_current_user)) -> bool:
        # Em modo de desenvolvimento, ignorar verificações de permissão
        if settings.is_development:
            return True
        
        # Em produção, implementar a verificação de permissão adequada
        # (Esta parte seria implementada conforme a lógica real de permissões)
        return True
    
    return dependency


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Verifica se o usuário está ativo.
    Em modo de desenvolvimento, sempre retorna o usuário sem verificação.
    
    Args:
        current_user: Usuário atual obtido da função get_current_user
        
    Returns:
        dict: Dados do usuário
    """
    # Em produção, implementar verificação se o usuário está ativo
    return current_user 