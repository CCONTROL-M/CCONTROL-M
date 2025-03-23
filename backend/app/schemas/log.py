"""Schemas para logs do sistema."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class LogSistemaBase(BaseModel):
    """Schema base para logs do sistema."""
    acao: str = Field(..., description="Ação realizada")
    tabela: str = Field(..., description="Tabela afetada")
    id_registro: str = Field(..., description="ID do registro afetado")
    id_usuario: UUID = Field(..., description="ID do usuário que realizou a ação")
    id_empresa: UUID = Field(..., description="ID da empresa")
    detalhes: str = Field(..., description="Detalhes da ação")


class LogSistemaCreate(LogSistemaBase):
    """Schema para criação de logs do sistema."""
    pass


class LogSistema(LogSistemaBase):
    """Schema para retorno de logs do sistema."""
    id: UUID = Field(..., description="ID do log")
    data_hora: datetime = Field(..., description="Data e hora do log")

    class Config:
        """Configurações do schema."""
        from_attributes = True 