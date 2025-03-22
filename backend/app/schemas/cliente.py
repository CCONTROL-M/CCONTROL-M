"""Schema para validação e serialização de clientes no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .pagination import PaginatedResponse


class ClienteBase(BaseModel):
    """Schema base para clientes."""
    nome: str
    cpf_cnpj: str
    contato: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None


class ClienteCreate(ClienteBase):
    """Schema para criação de clientes."""
    id_empresa: UUID


class ClienteUpdate(BaseModel):
    """Schema para atualização parcial de clientes."""
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    contato: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    ativo: Optional[bool] = None


class ClienteInDB(ClienteBase):
    """Schema para representação de clientes no banco de dados."""
    id_cliente: UUID
    id_empresa: UUID
    ativo: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Cliente(ClienteInDB):
    """Schema para representação de clientes nas respostas da API."""
    
    class Config:
        from_attributes = True


class ClienteList(PaginatedResponse):
    """Schema para listagem paginada de clientes."""
    items: List[Cliente] 