"""Schemas para operações com usuários."""
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import BaseSchema, TimestampMixin


class UsuarioBase(BaseSchema):
    """Atributos base compartilhados por todos os schemas de usuário."""
    
    nome: str
    email: EmailStr
    tipo_usuario: str
    telas_permitidas: Optional[Dict[str, Any]] = None


class UsuarioCreate(UsuarioBase):
    """Atributos para criar um novo usuário."""
    
    id_empresa: UUID
    senha: str
    
    @field_validator('senha')
    def senha_must_be_strong(cls, v):
        """Valida que a senha é forte."""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        return v


class UsuarioUpdate(BaseSchema):
    """Atributos que podem ser atualizados em um usuário."""
    
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    tipo_usuario: Optional[str] = None
    telas_permitidas: Optional[Dict[str, Any]] = None
    senha: Optional[str] = None
    
    @field_validator('senha')
    def senha_must_be_strong(cls, v):
        """Valida que a senha é forte, se fornecida."""
        if v is not None and len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        return v


class UsuarioInDB(UsuarioBase, TimestampMixin):
    """Atributos de um usuário armazenado no banco de dados."""
    
    id_usuario: UUID
    id_empresa: UUID
    senha_hash: str


class Usuario(UsuarioBase, TimestampMixin):
    """Atributos de um usuário retornado para o cliente."""
    
    id_usuario: UUID
    id_empresa: UUID


class UsuarioList(BaseSchema):
    """Schema para listar usuários."""
    
    id_usuario: UUID
    nome: str
    email: EmailStr
    tipo_usuario: str
    created_at: Optional[str] = None


class UsuarioLogin(BaseSchema):
    """Schema para login de usuário."""
    
    email: EmailStr
    senha: str 