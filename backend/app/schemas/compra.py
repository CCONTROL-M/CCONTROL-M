"""Esquemas de validação para compras."""
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.schemas.fornecedor import FornecedorBasico
from app.schemas.produto import ProdutoBasico


class ItemCompraBase(BaseModel):
    """Esquema base para item de compra."""
    
    id_produto: Optional[UUID] = None
    descricao: str
    quantidade: float = Field(gt=0)
    valor_unitario: float = Field(ge=0)
    valor_total: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator("valor_total", mode="before")
    @classmethod
    def calcular_valor_total(cls, v: Optional[float], values: Dict[str, Any]) -> float:
        """Calcular o valor total do item."""
        if "quantidade" in values and "valor_unitario" in values:
            return values["quantidade"] * values["valor_unitario"]
        return v if v is not None else 0


class ItemCompraCreate(ItemCompraBase):
    """Esquema para criação de item de compra."""
    pass


class ItemCompra(ItemCompraBase):
    """Esquema completo para item de compra."""
    
    id_item_compra: UUID
    id_compra: UUID
    produto: Optional[ProdutoBasico] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


class CompraBase(BaseModel):
    """Esquema base para compra."""
    
    id_empresa: UUID
    id_fornecedor: Optional[UUID] = None
    numero_compra: Optional[str] = None
    descricao: str
    data_compra: date
    valor_total: float = Field(ge=0)
    status: str = Field(default="pendente")
    observacao: Optional[str] = None
    itens_compra: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class CompraCreate(CompraBase):
    """Esquema para criação de compra."""
    
    itens: Optional[List[ItemCompraCreate]] = None


class CompraUpdate(BaseModel):
    """Esquema para atualização de compra."""
    
    id_empresa: UUID
    id_fornecedor: Optional[UUID] = None
    numero_compra: Optional[str] = None
    descricao: Optional[str] = None
    data_compra: Optional[date] = None
    valor_total: Optional[float] = None
    status: Optional[str] = None
    observacao: Optional[str] = None
    itens_compra: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class Compra(CompraBase):
    """Esquema completo para compra."""
    
    id_compra: UUID
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    fornecedor: Optional[FornecedorBasico] = None


class CompraDetalhes(Compra):
    """Esquema com detalhes completos de uma compra."""
    
    itens: List[ItemCompra] = []
    

class CompraSimples(BaseModel):
    """Esquema simplificado para compra."""
    
    id_compra: UUID
    id_empresa: UUID
    id_fornecedor: Optional[UUID] = None
    numero_compra: Optional[str] = None
    descricao: str
    data_compra: date
    valor_total: float
    status: str
    
    model_config = ConfigDict(from_attributes=True) 