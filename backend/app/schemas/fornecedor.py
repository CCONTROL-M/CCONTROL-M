"""Schemas para a entidade Fornecedor."""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator, field_validator
from datetime import datetime
from .validators import validar_cnpj


class FornecedorBase(BaseModel):
    """Modelo base para fornecedores."""
    nome: str = Field(..., min_length=3, max_length=150)
    cnpj: str = Field(..., min_length=14, max_length=18)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    observacao: Optional[str] = None
    avaliacao: Optional[int] = Field(None, ge=1, le=5)
    ativo: bool = True

    @field_validator('cnpj')
    def validar_formato_cnpj(cls, v):
        """Valida e formata o CNPJ."""
        return validar_cnpj(v)


class FornecedorCreate(FornecedorBase):
    """Modelo para criação de fornecedores."""
    pass


class FornecedorUpdate(BaseModel):
    """Modelo para atualização de fornecedores."""
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    observacao: Optional[str] = None
    avaliacao: Optional[int] = None
    ativo: Optional[bool] = None

    @field_validator('cnpj')
    def validar_formato_cnpj(cls, v):
        """Valida e formata o CNPJ."""
        if v is None:
            return v
        return validar_cnpj(v)


class FornecedorResponse(FornecedorBase):
    """Modelo para resposta de fornecedores."""
    id_fornecedor: UUID
    id_empresa: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FornecedorInDB(FornecedorResponse):
    """
    Schema para representação interna do fornecedor no banco de dados.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class Fornecedor(FornecedorResponse):
    """
    Alias para FornecedorResponse.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class FornecedorList(BaseModel):
    """Modelo para listagem paginada de fornecedores."""
    items: List[FornecedorResponse]
    total: int
    page: int
    size: int 