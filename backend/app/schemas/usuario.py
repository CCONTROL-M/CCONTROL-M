"""
Schemas para manipulação de usuários.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, RootModel


class UsuarioBase(BaseModel):
    """Schema base para usuários."""
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(...)
    ativo: Optional[bool] = Field(True, description="Indica se o usuário está ativo")


class UsuarioLogin(BaseModel):
    """Schema para login de usuários."""
    email: EmailStr
    senha: str


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuários."""
    senha: str = Field(..., min_length=6, max_length=100)
    id_empresa: Optional[UUID] = None
    admin: Optional[bool] = False


class UsuarioUpdate(BaseModel):
    """Schema para atualização de usuários."""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(None, min_length=6, max_length=100)
    ativo: Optional[bool] = None
    admin: Optional[bool] = None
    
    class Config:
        from_attributes = True


class UsuarioInDB(UsuarioBase):
    """Schema para representação interna do usuário no banco de dados."""
    id: UUID
    id_empresa: UUID
    admin: bool = False
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UsuarioResponse(UsuarioBase):
    """Schema para resposta de usuários."""
    id: UUID
    id_empresa: UUID
    admin: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Usuario(UsuarioResponse):
    """
    Alias para UsuarioResponse.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class UsuarioList(RootModel):
    """Schema para listar usuários."""
    root: List[Usuario] 