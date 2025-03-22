"""Schema para validação e serialização de clientes no sistema CCONTROL-M."""
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from .pagination import PaginatedResponse
from .validators import validar_cpf_cnpj


class ClienteBase(BaseModel):
    """Schema base para clientes."""
    nome: str = Field(
        ..., 
        example="João da Silva Comércio ME", 
        description="Nome completo do cliente (pessoa física ou jurídica)"
    )
    cpf_cnpj: str = Field(
        ..., 
        example="12345678000190", 
        description="CPF (para pessoa física) ou CNPJ (para pessoa jurídica) do cliente, sem formatação"
    )
    contato: Optional[str] = Field(
        None, 
        example="Maria Souza", 
        description="Nome da pessoa de contato na empresa cliente"
    )
    telefone: Optional[str] = Field(
        None, 
        example="11987654321", 
        description="Telefone principal do cliente, preferencialmente com DDD"
    )
    email: Optional[str] = Field(
        None, 
        example="contato@empresa.com.br", 
        description="Email principal do cliente para contato"
    )
    
    @field_validator('cpf_cnpj')
    def validar_documento(cls, v):
        """Valida e formata o CPF ou CNPJ."""
        return validar_cpf_cnpj(v)


class ClienteCreate(ClienteBase):
    """Schema para criação de clientes."""
    id_empresa: UUID = Field(
        ..., 
        example="123e4567-e89b-12d3-a456-426614174000", 
        description="ID da empresa à qual o cliente será vinculado"
    )


class ClienteUpdate(BaseModel):
    """Schema para atualização parcial de clientes."""
    nome: Optional[str] = Field(
        None, 
        example="João da Silva Comércio LTDA", 
        description="Nome atualizado do cliente"
    )
    cpf_cnpj: Optional[str] = Field(
        None, 
        example="12345678000190", 
        description="CPF/CNPJ atualizado do cliente"
    )
    contato: Optional[str] = Field(
        None, 
        example="José Pereira", 
        description="Nome atualizado do contato"
    )
    telefone: Optional[str] = Field(
        None, 
        example="11998765432", 
        description="Telefone atualizado do cliente"
    )
    email: Optional[str] = Field(
        None, 
        example="novo.contato@empresa.com.br", 
        description="Email atualizado do cliente"
    )
    ativo: Optional[bool] = Field(
        None, 
        example=True, 
        description="Status ativo/inativo do cliente"
    )
    
    @field_validator('cpf_cnpj')
    def validar_documento(cls, v):
        """Valida e formata o CPF ou CNPJ."""
        if v is not None:
            return validar_cpf_cnpj(v)
        return v


class ClienteInDB(ClienteBase):
    """Schema para representação de clientes no banco de dados."""
    id_cliente: UUID = Field(
        ..., 
        example="123e4567-e89b-12d3-a456-426614174000", 
        description="ID único do cliente gerado pelo sistema"
    )
    id_empresa: UUID = Field(
        ..., 
        example="123e4567-e89b-12d3-a456-426614174001", 
        description="ID da empresa à qual o cliente pertence"
    )
    ativo: bool = Field(
        True, 
        example=True, 
        description="Indica se o cliente está ativo ou inativo no sistema"
    )
    created_at: datetime = Field(
        ..., 
        example="2023-01-15T14:30:00Z", 
        description="Data e hora de criação do registro"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        example="2023-02-20T10:15:00Z", 
        description="Data e hora da última atualização"
    )

    class Config:
        from_attributes = True


class Cliente(ClienteInDB):
    """Schema para representação de clientes nas respostas da API."""
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_cliente": "123e4567-e89b-12d3-a456-426614174000",
                "id_empresa": "123e4567-e89b-12d3-a456-426614174001",
                "nome": "João da Silva Comércio ME",
                "cpf_cnpj": "12345678000190",
                "contato": "Maria Souza",
                "telefone": "11987654321",
                "email": "contato@empresa.com.br",
                "ativo": True,
                "created_at": "2023-01-15T14:30:00Z",
                "updated_at": "2023-02-20T10:15:00Z"
            }
        }


class ClienteList(PaginatedResponse):
    """Schema para listagem paginada de clientes."""
    items: List[Cliente] = Field(
        ..., 
        description="Lista de clientes retornados na consulta"
    ) 