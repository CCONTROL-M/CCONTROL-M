"""Schema para validação e serialização de fornecedores no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .pagination import PaginatedResponse


class FornecedorBase(BaseModel):
    """Schema base para fornecedores."""
    nome: str
    cnpj: str
    contato: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    avaliacao: Optional[int] = None


class FornecedorCreate(FornecedorBase):
    """Schema para criação de fornecedores."""
    id_empresa: UUID


class FornecedorUpdate(BaseModel):
    """Schema para atualização parcial de fornecedores."""
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    contato: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    avaliacao: Optional[int] = None
    ativo: Optional[bool] = None


class FornecedorInDB(FornecedorBase):
    """Schema para representação de fornecedores no banco de dados."""
    id_fornecedor: UUID
    id_empresa: UUID
    ativo: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Fornecedor(FornecedorInDB):
    """Schema para representação de fornecedores nas respostas da API."""
    
    class Config:
        from_attributes = True


class FornecedorList(PaginatedResponse):
    """Schema para listagem paginada de fornecedores."""
    items: List[Fornecedor] 