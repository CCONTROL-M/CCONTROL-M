"""Schemas para autenticação e tokens."""
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, EmailStr


class Token(BaseModel):
    """Schema de resposta de token de acesso."""
    
    access_token: str
    token_type: str
    expires_in: int
    user_id: UUID
    empresa_id: UUID
    nome: str
    email: str
    tipo_usuario: str
    telas_permitidas: Optional[dict] = None


class TokenData(BaseModel):
    """Schema para dados contidos no token JWT."""
    id_usuario: Optional[UUID] = None
    email: Optional[str] = None
    id_empresa: Optional[UUID] = None
    admin: Optional[bool] = False
    exp: Optional[int] = None


class TokenPayload(BaseModel):
    """Payload do token JWT."""
    
    sub: str = Field(..., description="Subject (user_id)")
    empresa_id: UUID
    tipo_usuario: str
    exp: int = Field(..., description="Expiration timestamp")
    jti: str = Field(..., description="JWT ID")


class TokenRefresh(BaseModel):
    """Requisição para renovar token."""
    
    refresh_token: str


class PasswordReset(BaseModel):
    """Requisição para reset de senha."""
    
    email: EmailStr
    
    @field_validator('email')
    def email_must_not_be_empty(cls, v):
        """Valida que o email não está vazio."""
        if not v:
            raise ValueError('Email não pode estar vazio')
        return v.lower()


class PasswordChange(BaseModel):
    """Requisição para alteração de senha."""
    
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    def password_must_be_strong(cls, v):
        """Valida que a senha é forte."""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        return v 