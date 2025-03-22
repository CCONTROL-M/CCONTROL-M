"""Schema para validação e serialização de permissões de usuário no sistema CCONTROL-M."""
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PermissaoUsuarioBase(BaseModel):
    """Schema base para permissões de usuário."""
    id_usuario: UUID = Field(..., description="ID do usuário associado à permissão")
    recurso: str = Field(..., description="Nome do recurso (ex: 'clientes', 'vendas')")
    acoes: List[str] = Field(..., description="Lista de ações permitidas (ex: ['criar', 'editar', 'listar', 'deletar'])")

class PermissaoUsuarioCreate(PermissaoUsuarioBase):
    """Schema para criação de permissões de usuário."""
    pass

class PermissaoUsuarioUpdate(BaseModel):
    """Schema para atualização de permissões de usuário."""
    recurso: Optional[str] = Field(None, description="Nome do recurso")
    acoes: Optional[List[str]] = Field(None, description="Lista de ações permitidas")

class PermissaoUsuarioInDB(PermissaoUsuarioBase):
    """Schema para representação de permissões de usuário no banco de dados."""
    id: UUID = Field(..., description="ID único da permissão")
    created_at: datetime = Field(..., description="Data de criação da permissão")

class PermissaoUsuario(PermissaoUsuarioInDB):
    """Schema completo para permissões de usuário."""
    pass

class PermissaoUsuarioList(BaseModel):
    """Schema para lista paginada de permissões de usuário."""
    items: List[PermissaoUsuario]
    total: int
    page: int
    size: int
    pages: int 