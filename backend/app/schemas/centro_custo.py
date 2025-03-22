"""Schema para validação e serialização de centros de custo no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .pagination import PaginatedResponse


class CentroCustoBase(BaseModel):
    """Schema base para centros de custo."""
    nome: str
    descricao: Optional[str] = None


class CentroCustoCreate(CentroCustoBase):
    """Schema para criação de centros de custo."""
    id_empresa: UUID


class CentroCustoUpdate(BaseModel):
    """Schema para atualização parcial de centros de custo."""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


class CentroCustoInDB(CentroCustoBase):
    """Schema para representação de centros de custo no banco de dados."""
    id_centro: UUID
    id_empresa: UUID
    ativo: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CentroCusto(CentroCustoInDB):
    """Schema para representação de centros de custo nas respostas da API."""
    
    class Config:
        from_attributes = True


class CentroCustoList(PaginatedResponse):
    """Schema para listagem paginada de centros de custo."""
    items: List[CentroCusto] 