from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.config.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso com os dados fornecidos.
    
    Args:
        data: Dados a serem codificados no token (não incluir informações sensíveis)
        expires_delta: Tempo de expiração do token (opcional)
    
    Returns:
        Token JWT codificado como string
    """
    to_encode = data.copy()
    
    # Define o tempo de expiração do token
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona a data de expiração e emissão
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(data.get("id", ""))
    })
    
    # Codifica o token usando o algoritmo especificado
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde à senha hashed.
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Senha hashed para comparação
    
    Returns:
        True se a senha corresponder, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Cria um hash seguro para uma senha em texto plano.
    
    Args:
        password: Senha em texto plano
    
    Returns:
        Senha hashed
    """
    return pwd_context.hash(password)


def get_token_data(token: str) -> Dict[str, Any]:
    """
    Decodifica e valida um token JWT.
    
    Args:
        token: Token JWT a ser validado e decodificado
    
    Returns:
        Dados decodificados do token
    
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        # Decodifica o token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verifica se a data de expiração está presente e válida
        if "exp" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sem data de expiração",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na validação do token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extrai e valida o token de autenticação da requisição, retornando os dados do usuário.
    
    Args:
        request: Objeto Request da requisição
    
    Returns:
        Dados do usuário ou None se o token for inválido ou inexistente
    """
    # Extrair o token da requisição
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    
    # Verificar se o formato do token é válido
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None
    
    try:
        # Decodificar e validar o token
        token_data = get_token_data(token)
        
        # Extrair dados do usuário
        user_data = {
            "id": token_data.get("id"),
            "email": token_data.get("email"),
            "empresa_id": token_data.get("empresa_id"),
            "superuser": token_data.get("is_superuser", False),
            "is_admin": token_data.get("is_admin", False),
            "roles": token_data.get("roles", []),
            "permissions": token_data.get("permissions", [])
        }
        
        return user_data
    except HTTPException:
        # Retornar None em caso de erro na validação do token
        return None
    except Exception:
        # Capturar outras exceções e retornar None
        return None


async def get_current_active_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Middleware para obter o usuário atual a partir do token JWT.
    
    Args:
        token: Token JWT obtido da requisição
    
    Returns:
        Dados do usuário autenticado
    
    Raises:
        HTTPException: Se o token for inválido, expirado ou o usuário estiver desativado
    """
    try:
        payload = get_token_data(token)
        
        # Verificar se o usuário está presente no token
        if not payload.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: ID de usuário ausente",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verificar se o usuário está ativo (pode ser expandido)
        if payload.get("disabled", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário desativado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        ) 