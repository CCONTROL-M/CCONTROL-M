"""
Schemas para manipulação de centros de custo.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, RootModel


class CentroCustoBase(BaseModel):
    """Schema base para centros de custo."""
    descricao: str = Field(..., min_length=2, max_length=100, examples=["Marketing"])
    ativo: Optional[bool] = Field(True, description="Indica se o centro de custo está ativo")


class CentroCustoCreate(CentroCustoBase):
    """Schema para criação de centros de custo."""
    pass


class CentroCustoUpdate(BaseModel):
    """Schema para atualização de centros de custo."""
    descricao: Optional[str] = Field(None, min_length=2, max_length=100, examples=["Marketing"])
    ativo: Optional[bool] = Field(None, description="Indica se o centro de custo está ativo")
    
    class Config:
        from_attributes = True


class CentroCustoResponse(CentroCustoBase):
    """Schema para resposta de centros de custo."""
    id_centro_custo: UUID
    id_empresa: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CentroCustoInDB(CentroCustoResponse):
    """
    Schema para representação interna do centro de custo no banco de dados.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class CentroCusto(CentroCustoResponse):
    """
    Alias para CentroCustoResponse.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class CentroCustoList(RootModel):
    """Schema para listar centros de custo."""
    root: List[CentroCusto] 