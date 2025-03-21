"""Router de autenticação para o sistema CCONTROL-M."""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database import get_db
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioLogin, Usuario
from app.schemas.token import Token
from app.dependencies import create_access_token
from app.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Endpoint para login usando OAuth2 com JWT.
    
    Args:
        db: Sessão do banco de dados
        form_data: Dados do formulário OAuth2
        
    Returns:
        Token: Token de acesso JWT
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    usuario_repo = UsuarioRepository()
    usuario = usuario_repo.get_by_field(db, "email", form_data.username.lower())
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=usuario.id_usuario,
        empresa_id=usuario.id_empresa,
        tipo_usuario=usuario.tipo_usuario,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": usuario.id_usuario,
        "empresa_id": usuario.id_empresa,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo_usuario": usuario.tipo_usuario,
        "telas_permitidas": usuario.telas_permitidas
    }


@router.post("/login-json", response_model=Token)
def login_json(
    login_data: UsuarioLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Endpoint alternativo para login usando JSON.
    
    Args:
        login_data: Dados de login em formato JSON
        db: Sessão do banco de dados
        
    Returns:
        Token: Token de acesso JWT
    """
    # Criar form_data a partir do JSON
    form_data = OAuth2PasswordRequestForm(
        username=login_data.email,
        password=login_data.senha,
        scope="",
        client_id=None,
        client_secret=None
    )
    return login(db=db, form_data=form_data) 