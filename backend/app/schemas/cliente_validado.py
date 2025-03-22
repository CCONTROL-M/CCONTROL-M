"""
Esquema Pydantic para validação de Clientes com funções avançadas.

Este módulo implementa esquemas fortemente validados para os dados de clientes,
usando as funções de validação personalizadas do sistema.
"""
from typing import Optional, List, Dict, Any, Union
from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator, EmailStr, root_validator
import re

from app.utils.validation import (
    is_valid_cpf, is_valid_cnpj, is_valid_phone, is_valid_email,
    sanitize_string, detect_attack_patterns
)
from app.schemas.validators import validar_cpf_cnpj, formatar_cpf_cnpj


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
    
    @validator('cep')
    def validate_cep(cls, v):
        """Valida o formato do CEP."""
        # Remover caracteres não numéricos
        v = re.sub(r'[^\d]', '', v)
        
        # Verificar se tem 8 dígitos
        if len(v) != 8:
            raise ValueError("CEP deve conter 8 dígitos")
            
        # Formatar como padrão: 00000-000
        return f"{v[:5]}-{v[5:]}"
    
    @validator('uf')
    def validate_uf(cls, v):
        """Valida a UF."""
        # Lista de UFs válidas
        ufs_validas = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
            "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
            "SP", "SE", "TO"
        ]
        
        v = v.upper()
        if v not in ufs_validas:
            raise ValueError("UF inválida")
        return v
    
    @validator('logradouro', 'complemento', 'bairro', 'cidade')
    def sanitize_text_fields(cls, v, values, field):
        """Sanitiza campos de texto para remover possíveis códigos maliciosos."""
        if v:
            # Verificar padrões de ataque
            attacks = detect_attack_patterns(v)
            if attacks:
                raise ValueError(f"Campo contém padrões de ataque: {', '.join(attacks)}")
                
            return sanitize_string(v)
        return v


class Contato(BaseModel):
    """Modelo para contato do cliente."""
    tipo: str = Field(..., max_length=20)
    valor: str = Field(..., max_length=100)
    principal: bool = False
    observacao: Optional[str] = Field(None, max_length=200)
    
    @validator('tipo')
    def validate_tipo(cls, v):
        """Valida o tipo de contato."""
        tipos_validos = ["celular", "telefone", "email", "whatsapp", "instagram", "facebook", "outro"]
        v = v.lower()
        if v not in tipos_validos:
            raise ValueError(f"Tipo de contato inválido. Tipos válidos: {', '.join(tipos_validos)}")
        return v
    
    @validator('valor')
    def validate_valor(cls, v, values):
        """Valida o valor do contato com base no tipo."""
        if 'tipo' not in values:
            return v
            
        tipo = values['tipo']
        
        if tipo in ["celular", "telefone", "whatsapp"]:
            if not is_valid_phone(v):
                raise ValueError("Número de telefone inválido")
                
        elif tipo == "email":
            if not is_valid_email(v):
                raise ValueError("Endereço de e-mail inválido")
                
        # Sanitizar o valor para remover possíveis códigos maliciosos
        return sanitize_string(v)


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
    
    @validator('nome', 'nome_fantasia')
    def sanitize_names(cls, v):
        """Sanitiza campos de nome para remover caracteres inválidos."""
        if v:
            return sanitize_string(v)
        return v
    
    @validator('documento')
    def validate_documento(cls, v, values):
        """Valida CPF ou CNPJ com base no tipo de cliente."""
        if 'tipo' not in values:
            return v
            
        try:
            # Usar o validador existente para CPF/CNPJ
            documento_limpo = validar_cpf_cnpj(v)
            
            # Verificar se o tipo de documento corresponde ao tipo de cliente
            if values['tipo'] == TipoCliente.PESSOA_FISICA and len(documento_limpo) != 11:
                raise ValueError("Para Pessoa Física, o documento deve ser um CPF válido")
                
            if values['tipo'] == TipoCliente.PESSOA_JURIDICA and len(documento_limpo) != 14:
                raise ValueError("Para Pessoa Jurídica, o documento deve ser um CNPJ válido")
                
            # Formatar o documento para exibição
            return formatar_cpf_cnpj(v)
            
        except ValueError as e:
            raise ValueError(str(e))
    
    @root_validator
    def validate_contato_principal(cls, values):
        """Verifica se existe pelo menos um contato principal."""
        contatos = values.get('contatos', [])
        if contatos and not any(c.principal for c in contatos):
            # Definir o primeiro contato como principal se nenhum for marcado
            contatos[0].principal = True
        return values
    
    @root_validator
    def validate_endereco_principal(cls, values):
        """Verifica se existe pelo menos um endereço principal."""
        enderecos = values.get('enderecos', [])
        if enderecos and not any(e.principal for e in enderecos):
            # Definir o primeiro endereço como principal se nenhum for marcado
            enderecos[0].principal = True
        return values


class ClienteUpdate(BaseModel):
    """Esquema para atualização de cliente com validações avançadas."""
    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    nome_fantasia: Optional[str] = Field(None, max_length=100)
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    limite_credito: Optional[Decimal] = Field(None, ge=0)
    situacao: Optional[SituacaoCliente] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    
    @validator('nome', 'nome_fantasia')
    def sanitize_names(cls, v):
        """Sanitiza campos de nome para remover caracteres inválidos."""
        if v:
            return sanitize_string(v)
        return v


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
    
    class Config:
        """Configuração do modelo."""
        orm_mode = True 