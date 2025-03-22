"""Schemas Pydantic para Empresas no sistema CCONTROL-M."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator, RootModel
import re
from .validators import validar_cnpj


class EmpresaBase(BaseModel):
    """Schema base com campos comuns para Empresa."""
    razao_social: str = Field(..., description="Razão social da empresa", min_length=2, max_length=255)
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia da empresa", max_length=255)
    cnpj: str = Field(..., description="CNPJ da empresa")
    email: Optional[EmailStr] = Field(None, description="Email de contato da empresa")
    telefone: Optional[str] = Field(None, description="Telefone de contato da empresa", max_length=20)
    endereco: Optional[str] = Field(None, description="Endereço da empresa", max_length=255)
    cidade: Optional[str] = Field(None, description="Cidade da empresa", max_length=100)
    estado: Optional[str] = Field(None, description="Estado da empresa (sigla)", max_length=2)
    logo_url: Optional[str] = Field(None, description="URL da logomarca da empresa", max_length=255)
    ativo: Optional[bool] = Field(True, description="Indica se a empresa está ativa")

    @field_validator('cnpj')
    def validar_formato_cnpj(cls, v: str) -> str:
        """Valida e formata o CNPJ."""
        return validar_cnpj(v)
    
    @field_validator('estado')
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        """Valida o formato da sigla do estado."""
        if v is not None:
            if len(v) != 2:
                raise ValueError("Estado deve ser uma sigla com 2 caracteres")
            return v.upper()
        return v


class EmpresaCreate(EmpresaBase):
    """Schema para criação de empresas."""
    pass


class EmpresaUpdate(BaseModel):
    """Schema para atualização de empresas (todos campos opcionais)."""
    razao_social: Optional[str] = Field(None, description="Razão social da empresa", min_length=2, max_length=255)
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia da empresa", max_length=255)
    cnpj: Optional[str] = Field(None, description="CNPJ da empresa")
    email: Optional[EmailStr] = Field(None, description="Email de contato da empresa")
    telefone: Optional[str] = Field(None, description="Telefone de contato da empresa", max_length=20)
    endereco: Optional[str] = Field(None, description="Endereço da empresa", max_length=255)
    cidade: Optional[str] = Field(None, description="Cidade da empresa", max_length=100)
    estado: Optional[str] = Field(None, description="Estado da empresa (sigla)", max_length=2)
    logo_url: Optional[str] = Field(None, description="URL da logomarca da empresa", max_length=255)
    ativo: Optional[bool] = None

    @field_validator('cnpj')
    def validar_formato_cnpj(cls, v: Optional[str]) -> Optional[str]:
        """Valida e formata o CNPJ."""
        if v is not None:
            return validar_cnpj(v)
        return v
    
    @field_validator('estado')
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        """Valida o formato da sigla do estado."""
        if v is not None:
            if len(v) != 2:
                raise ValueError("Estado deve ser uma sigla com 2 caracteres")
            return v.upper()
        return v


class EmpresaInDB(EmpresaBase):
    """Schema para empresa com campos específicos do banco de dados."""
    id_empresa: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EmpresaResponse(EmpresaBase):
    """Schema para resposta de empresas."""
    id_empresa: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Empresa(EmpresaResponse):
    """
    Alias para EmpresaResponse.
    Mantido por motivos de compatibilidade com código existente.
    """
    pass


class EmpresaList(RootModel):
    """Schema para listar empresas."""
    root: List[Empresa] 