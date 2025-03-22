"""Dependências para injeção nas rotas do FastAPI."""
from datetime import datetime, timedelta
from typing import Optional, Union, Any, Dict, Callable
from functools import wraps

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.config.settings import settings
from app.database import db_async_session
from app.schemas.token import TokenPayload
from app.repositories.usuario_repository import UsuarioRepository

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> TokenPayload:
    """
    Valida o token JWT e retorna os dados do usuário atual.
    
    Args:
        token: Token JWT de autenticação
        
    Returns:
        TokenPayload: Dados do payload do token
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        # Decodificar o token JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar se o token está expirado
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se o usuário existe no banco de dados
    async with db_async_session() as session:
        usuario_repo = UsuarioRepository(session)
        user = await usuario_repo.get_by_id(token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )
    
    return token_data


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
        "sub": str(subject),
        "empresa_id": str(empresa_id),
        "tipo_usuario": tipo_usuario,
        "exp": expire.timestamp(),
        "jti": f"{datetime.utcnow().timestamp()}"
    }
    
    # Codificar o token JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def check_permission(permission: str):
    """
    Verifica se o usuário tem permissão para acessar um recurso específico.
    
    Args:
        permission: Nome da permissão necessária
    
    Returns:
        Callable: Função de dependência que verifica a permissão
    
    Usage:
        @router.get("/items/", dependencies=[Depends(check_permission("read:items"))])
    """
    async def dependency(current_user: TokenPayload = Depends(get_current_user)) -> bool:
        # Verificar se o usuário está autenticado
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Se o usuário for administrador, tem todas as permissões
        if current_user.tipo_usuario == "ADMIN":
            return True
            
        # Verificar permissões do usuário no novo sistema de permissões
        if ":" in permission:
            from app.repositories.permissao_usuario_repository import PermissaoUsuarioRepository
            
            recurso, acao = permission.split(":", 1)
            
            # Verificar permissão específica no repositório
            permissao_repo = PermissaoUsuarioRepository()
            has_permission = await permissao_repo.check_user_permission(
                user_id=current_user.sub,
                recurso=recurso,
                acao=acao,
                tenant_id=current_user.empresa_id
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Sem permissão para '{acao}' no recurso '{recurso}'"
                )
        
        return True
        
    return dependency 