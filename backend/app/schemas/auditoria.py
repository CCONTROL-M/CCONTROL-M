"""Schemas para validação de dados de auditoria."""
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field


class AuditoriaBase(BaseModel):
    """Schema base para registros de auditoria."""
    entity_type: str = Field(..., description="Tipo de entidade auditada")
    entity_id: int = Field(..., description="ID da entidade auditada")
    action_type: str = Field(..., description="Tipo de ação (create, update, delete)")
    user_id: int = Field(..., description="ID do usuário que realizou a ação")
    empresa_id: int = Field(..., description="ID da empresa")
    timestamp: datetime = Field(default_factory=datetime.now, description="Data e hora da ação")


class AuditoriaCreate(AuditoriaBase):
    """Schema para criação de registros de auditoria."""
    data_before: Optional[Dict[str, Any]] = Field(None, description="Dados antes da alteração")
    data_after: Optional[Dict[str, Any]] = Field(None, description="Dados após a alteração")
    details: Optional[str] = Field(None, description="Detalhes adicionais da ação")


class AuditoriaSchema(AuditoriaBase):
    """Schema para retorno de registros de auditoria."""

    id: UUID
    data_hora: datetime

    class Config:
        """Configurações do schema."""

        from_attributes = True


class PaginatedAuditoriaResponse(BaseModel):
    """Schema para resposta paginada de registros de auditoria."""

    items: List[AuditoriaSchema]
    total: int


class AuditoriaResponse(AuditoriaBase):
    """Schema para resposta de registros de auditoria."""
    id: int = Field(..., description="ID do registro de auditoria")
    data_before: Optional[Dict[str, Any]] = Field(None, description="Dados antes da alteração")
    data_after: Optional[Dict[str, Any]] = Field(None, description="Dados após a alteração")
    details: Optional[str] = Field(None, description="Detalhes adicionais da ação")
    username: Optional[str] = Field(None, description="Nome do usuário que realizou a ação")
    entity_name: Optional[str] = Field(None, description="Nome da entidade auditada")
    
    class Config:
        from_attributes = True


class AuditoriaList(BaseModel):
    """Schema para listar registros de auditoria com paginação."""
    items: List[AuditoriaResponse] = Field([], description="Lista de registros de auditoria")
    total: int = Field(0, description="Total de registros encontrados")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    pages: int = Field(1, description="Total de páginas")
    
    class Config:
        from_attributes = True 