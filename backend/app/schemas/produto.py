from uuid import UUID
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from datetime import datetime

# Esquema base
class ProdutoBase(BaseModel):
    nome: str
    codigo: str
    descricao: Optional[str] = None
    preco_venda: Decimal
    preco_custo: Decimal
    estoque_atual: Optional[Decimal] = Field(default=0)
    estoque_minimo: Optional[Decimal] = Field(default=0)
    categoria: Optional[str] = None
    ativo: Optional[bool] = True

# Esquema básico para relacionamentos
class ProdutoBasico(BaseModel):
    id_produto: UUID
    nome: str
    codigo: str
    preco_venda: Decimal
    
    class Config:
        from_attributes = True

# Esquema para criação
class ProdutoCreate(ProdutoBase):
    id_empresa: UUID

# Esquema para atualização parcial
class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    preco_venda: Optional[Decimal] = None
    preco_custo: Optional[Decimal] = None
    estoque_atual: Optional[Decimal] = None
    estoque_minimo: Optional[Decimal] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None

# Esquema para resposta
class ProdutoResponse(ProdutoBase):
    id_produto: UUID
    id_empresa: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Esquema para representação interna do produto no banco de dados
class ProdutoInDB(ProdutoResponse):
    """
    Schema para representação interna do produto no banco de dados.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass

# Alias para ProdutoResponse
class Produto(ProdutoResponse):
    """
    Alias para ProdutoResponse.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass

# Esquema para resposta com paginação
class ProdutoList(BaseModel):
    items: List[ProdutoResponse]
    total: int
    page: int
    size: int

# Esquema para atualização de estoque
class EstoqueUpdate(BaseModel):
    quantidade: Decimal = Field(..., description="Quantidade a adicionar (positivo) ou remover (negativo)")

    @validator('quantidade')
    def quantidade_nao_pode_ser_zero(cls, v):
        if v == 0:
            raise ValueError('Quantidade não pode ser zero')
        return v 