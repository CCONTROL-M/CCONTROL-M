"""Dependências para injeção nas rotas do FastAPI."""
from datetime import datetime, timedelta
from typing import Optional, Union, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database import get_db
from app.schemas.token import TokenPayload
from app.repositories.usuario_repository import UsuarioRepository

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> TokenPayload:
    """
    Valida o token JWT e retorna os dados do usuário atual.
    
    Args:
        token: Token JWT de autenticação
        db: Sessão do banco de dados
        
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
    usuario_repo = UsuarioRepository()
    user = usuario_repo.get_by_field(db, "id_usuario", token_data.sub)
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