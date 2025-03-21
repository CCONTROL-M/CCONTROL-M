"""Schemas Pydantic para Empresas no sistema CCONTROL-M."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


def validar_cnpj(cnpj: str) -> str:
    """
    Valida o formato do CNPJ.
    
    Args:
        cnpj: CNPJ a ser validado
        
    Returns:
        str: CNPJ validado
        
    Raises:
        ValueError: Se o CNPJ não estiver no formato válido
    """
    # Remove caracteres especiais para validação
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos numéricos")
    
    # Verifica se todos os dígitos são iguais (caso inválido)
    if len(set(cnpj_limpo)) == 1:
        raise ValueError("CNPJ inválido")
    
    # Reaplica a formatação padrão XX.XXX.XXX/XXXX-XX
    cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    
    return cnpj_formatado


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


class Empresa(EmpresaInDB):
    """Schema completo de empresa para resposta da API."""
    pass


class EmpresaList(BaseModel):
    """Schema reduzido para listagem de empresas."""
    id_empresa: UUID
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    cidade: Optional[str] = None
    estado: Optional[str] = None
    
    class Config:
        from_attributes = True 