"""
Esquema Pydantic para validação de Clientes com funções avançadas.

Este módulo implementa esquemas fortemente validados para os dados de clientes,
usando as funções de validação personalizadas do sistema.
"""
from typing import Optional, List, Dict, Any, Union
from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator

from app.utils.validation import sanitize_string, detect_attack_patterns
from app.utils.validators_extra import (
    validar_cep, validar_uf, validar_telefone, validar_email,
    validar_tipo_contato, validar_valor_contato
)
from app.utils.validators import validar_cpf_cnpj, formatar_cpf_cnpj


class SituacaoCliente(str, Enum):
    """Enumeração para situação do cliente."""
    ATIVO = "ativo"
    INATIVO = "inativo"
    INADIMPLENTE = "inadimplente"
    BLOQUEADO = "bloqueado"
    EM_ANALISE = "em_analise"


class TipoCliente(str, Enum):
    """Enumeração para o tipo de cliente."""
    PESSOA_FISICA = "pessoa_fisica"
    PESSOA_JURIDICA = "pessoa_juridica"


class Endereco(BaseModel):
    """Modelo para endereço do cliente."""
    logradouro: str = Field(..., max_length=100)
    numero: str = Field(..., max_length=20)
    complemento: Optional[str] = Field(None, max_length=50)
    bairro: str = Field(..., max_length=50)
    cidade: str = Field(..., max_length=50)
    uf: str = Field(..., min_length=2, max_length=2)
    cep: str = Field(..., max_length=9)
    principal: bool = True
    
    @field_validator('cep')
    @classmethod
    def validate_cep(cls, v):
        """Valida o formato do CEP."""
        return validar_cep(v)
    
    @field_validator('uf')
    @classmethod
    def validate_uf(cls, v):
        """Valida o formato da UF."""
        return validar_uf(v)
    
    @field_validator('logradouro', 'complemento', 'bairro', 'cidade')
    @classmethod
    def sanitize_text_fields(cls, v, info):
        """Sanitiza campos de texto para prevenir ataques."""
        if v is None:
            return v
            
        # Aplicar sanitização
        v = sanitize_string(v)
        
        # Verificar padrões de ataque
        attack_patterns = detect_attack_patterns(v)
        if attack_patterns:
            field_name = info.field_name
            raise ValueError(f"Campo {field_name} contém padrão potencialmente malicioso: {', '.join(attack_patterns)}")
            
        return v


class Contato(BaseModel):
    """Modelo para contato do cliente."""
    tipo: str = Field(..., max_length=20)
    valor: str = Field(..., max_length=100)
    principal: bool = False
    observacao: Optional[str] = Field(None, max_length=200)
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        """Valida o tipo de contato."""
        return validar_tipo_contato(v)
    
    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v, info):
        """Valida o valor do contato de acordo com seu tipo."""
        values = info.data
        tipo = values.get('tipo', '')
        return validar_valor_contato(v, tipo)


class ClienteCreate(BaseModel):
    """Esquema para criação de cliente com validações avançadas."""
    tipo: TipoCliente
    nome: str = Field(..., min_length=3, max_length=100)
    nome_fantasia: Optional[str] = Field(None, max_length=100)
    documento: str = Field(..., min_length=11, max_length=18)
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    limite_credito: Optional[Decimal] = Field(None, ge=0)
    situacao: SituacaoCliente = SituacaoCliente.ATIVO
    observacoes: Optional[str] = Field(None, max_length=500)
    enderecos: List[Endereco] = Field(..., min_items=1)
    contatos: List[Contato] = Field(..., min_items=1)
    
    @field_validator('nome', 'nome_fantasia')
    @classmethod
    def sanitize_names(cls, v):
        """Sanitiza os campos de nome para evitar injeções."""
        if v is None:
            return v
        return sanitize_string(v)
    
    @field_validator('documento')
    @classmethod
    def validate_documento(cls, v, info):
        """Valida e formata o documento conforme tipo de cliente."""
        if not v:
            return v
            
        # Verificar formato do documento
        if not validar_cpf_cnpj(v):
            raise ValueError("Documento inválido")
            
        # Formatar documento
        v = formatar_cpf_cnpj(v)
        
        # Validar consistência com tipo de cliente
        values = info.data
        tipo = values.get('tipo')
        
        if tipo == TipoCliente.PESSOA_FISICA and len(v.replace(".", "").replace("-", "")) != 11:
            raise ValueError("CPF inválido para pessoa física")
            
        if tipo == TipoCliente.PESSOA_JURIDICA and len(v.replace(".", "").replace("-", "").replace("/", "")) != 14:
            raise ValueError("CNPJ inválido para pessoa jurídica")
            
        return v
    
    @model_validator(mode='after')
    def validate_contato_principal(self):
        """Verifica se existe pelo menos um contato principal."""
        if not self.contatos:
            return self
            
        # Verificar se há pelo menos um contato principal
        has_principal = any(contato.principal for contato in self.contatos)
        if not has_principal:
            # Se não houver, definir o primeiro como principal
            self.contatos[0].principal = True
            
        return self
    
    @model_validator(mode='after')
    def validate_endereco_principal(self):
        """Verifica se existe pelo menos um endereço principal."""
        if not self.enderecos:
            return self
            
        # Verificar se há pelo menos um endereço principal
        has_principal = any(endereco.principal for endereco in self.enderecos)
        if not has_principal:
            # Se não houver, definir o primeiro como principal
            self.enderecos[0].principal = True
            
        return self


class ClienteUpdate(BaseModel):
    """Esquema para atualização de cliente com validações avançadas."""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    nome_fantasia: Optional[str] = Field(None, max_length=100)
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    limite_credito: Optional[Decimal] = Field(None, ge=0)
    situacao: Optional[SituacaoCliente] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('nome', 'nome_fantasia', 'observacoes')
    @classmethod
    def sanitize_text(cls, v):
        """Sanitiza os campos de texto."""
        if v is None:
            return v
        return sanitize_string(v)


class ClienteResponse(BaseModel):
    """Esquema para resposta com dados de cliente."""
    id: int
    tipo: TipoCliente
    nome: str
    nome_fantasia: Optional[str] = None
    documento: str
    inscricao_estadual: Optional[str] = None
    data_nascimento: Optional[date] = None
    limite_credito: Optional[Decimal] = None
    situacao: SituacaoCliente
    observacoes: Optional[str] = None
    enderecos: List[Endereco]
    contatos: List[Contato]
    created_at: date
    updated_at: Optional[date] = None
    
    model_config = {
        "from_attributes": True
    } 