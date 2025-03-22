"""Schema para validação e serialização de logs do sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .pagination import PaginatedResponse


class LogSistemaBase(BaseModel):
    """Schema base para logs do sistema."""
    acao: str
    descricao: str
    dados: Optional[Dict[str, Any]] = None


class LogSistemaCreate(LogSistemaBase):
    """Schema para criação de logs do sistema."""
    id_empresa: Optional[UUID] = None
    id_usuario: Optional[UUID] = None


class LogSistemaInDB(LogSistemaBase):
    """Schema para representação de logs do sistema no banco de dados."""
    id_log: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogSistema(LogSistemaInDB):
    """Schema para representação de logs do sistema nas respostas da API."""
    
    class Config:
        orm_mode = True


class LogSistemaList(PaginatedResponse):
    """Schema para listagem paginada de logs do sistema."""
    items: List[LogSistema]
    total: int 