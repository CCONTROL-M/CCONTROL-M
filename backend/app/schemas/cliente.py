"""Schema para validação e serialização de clientes no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator
from datetime import datetime
from .pagination import PaginatedResponse
from .validators import validar_cpf_cnpj


class ClienteBase(BaseModel):
    """Schema base para clientes."""
    nome: str
    cpf_cnpj: str
    contato: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    
    @field_validator('cpf_cnpj')
    def validar_documento(cls, v):
        """Valida e formata o CPF ou CNPJ."""
        return validar_cpf_cnpj(v)


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
    
    @field_validator('cpf_cnpj')
    def validar_documento(cls, v):
        """Valida e formata o CPF ou CNPJ."""
        if v is not None:
            return validar_cpf_cnpj(v)
        return v


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