"""Schemas para permissões no sistema."""
from uuid import UUID
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class PermissaoBase(BaseModel):
    """Schema base para permissões."""
    recurso: str = Field(..., description="Nome do recurso")
    acoes: List[str] = Field(..., description="Lista de ações permitidas")
    descricao: Optional[str] = Field(None, description="Descrição da permissão")


class PermissaoCreate(PermissaoBase):
    """Schema para criação de permissões."""
    id_usuario: UUID = Field(..., description="ID do usuário")
    id_empresa: UUID = Field(..., description="ID da empresa")


class PermissaoUpdate(BaseModel):
    """Schema para atualização de permissões."""
    recurso: Optional[str] = Field(None, description="Nome do recurso")
    acoes: Optional[List[str]] = Field(None, description="Lista de ações permitidas")
    descricao: Optional[str] = Field(None, description="Descrição da permissão")


class Permissao(PermissaoBase):
    """Schema para retorno de permissões."""
    id_permissao: UUID = Field(..., description="ID da permissão")
    id_usuario: UUID = Field(..., description="ID do usuário")
    id_empresa: UUID = Field(..., description="ID da empresa")

    class Config:
        """Configurações do schema."""
        from_attributes = True 