"""Schemas Pydantic para Contas Bancárias no sistema CCONTROL-M."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class TipoConta(str, Enum):
    """Tipos válidos de contas bancárias."""
    CORRENTE = "corrente"
    POUPANCA = "poupança"


class ContaBancariaBase(BaseModel):
    """Schema base com campos comuns para Conta Bancária."""
    nome: str = Field(..., description="Nome/identificação da conta bancária", min_length=2, max_length=100)
    banco: str = Field(..., description="Nome do banco", max_length=100)
    agencia: str = Field(..., description="Número da agência", max_length=20)
    conta: str = Field(..., description="Número da conta", max_length=30)
    tipo: str = Field(..., description="Tipo da conta (corrente ou poupança)")
    saldo_inicial: float = Field(0.0, description="Saldo inicial da conta")
    ativa: bool = Field(True, description="Status de ativação da conta")
    mostrar_dashboard: bool = Field(True, description="Mostrar conta no dashboard")
    
    @field_validator('tipo')
    def validar_tipo_conta(cls, v: str) -> str:
        """Valida o tipo da conta bancária."""
        tipos_validos = [tipo.value for tipo in TipoConta]
        if v.lower() not in tipos_validos:
            tipos_str = ", ".join(tipos_validos)
            raise ValueError(f"Tipo de conta inválido. Tipos válidos: {tipos_str}")
        return v.lower()


class ContaBancariaCreate(ContaBancariaBase):
    """Schema para criação de contas bancárias."""
    id_empresa: UUID = Field(..., description="ID da empresa a qual a conta pertence")
    
    @field_validator('saldo_inicial')
    def inicializar_saldo_atual(cls, v: float) -> float:
        """Garante que o saldo inicial não seja negativo."""
        if v < 0:
            raise ValueError("Saldo inicial não pode ser negativo")
        return v


class ContaBancariaUpdate(BaseModel):
    """Schema para atualização de contas bancárias (todos campos opcionais)."""
    nome: Optional[str] = Field(None, description="Nome/identificação da conta bancária", min_length=2, max_length=100)
    banco: Optional[str] = Field(None, description="Nome do banco", max_length=100)
    agencia: Optional[str] = Field(None, description="Número da agência", max_length=20)
    conta: Optional[str] = Field(None, description="Número da conta", max_length=30)
    tipo: Optional[str] = Field(None, description="Tipo da conta (corrente ou poupança)")
    ativa: Optional[bool] = Field(None, description="Status de ativação da conta")
    mostrar_dashboard: Optional[bool] = Field(None, description="Mostrar conta no dashboard")
    
    @field_validator('tipo')
    def validar_tipo_conta(cls, v: Optional[str]) -> Optional[str]:
        """Valida o tipo da conta bancária, se fornecido."""
        if v is not None:
            tipos_validos = [tipo.value for tipo in TipoConta]
            if v.lower() not in tipos_validos:
                tipos_str = ", ".join(tipos_validos)
                raise ValueError(f"Tipo de conta inválido. Tipos válidos: {tipos_str}")
            return v.lower()
        return v


class ContaBancariaInDB(ContaBancariaBase):
    """Schema para conta bancária com campos específicos do banco de dados."""
    id_conta: UUID
    id_empresa: UUID
    saldo_atual: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContaBancaria(ContaBancariaInDB):
    """Schema completo de conta bancária para resposta da API."""
    pass


class ContaBancariaList(BaseModel):
    """Schema reduzido para listagem de contas bancárias."""
    id_conta: UUID
    nome: str
    banco: str
    tipo: str
    saldo_atual: float
    ativa: bool
    
    class Config:
        from_attributes = True


class AtualizacaoSaldo(BaseModel):
    """Schema para operações de atualização de saldo."""
    valor: float = Field(..., description="Valor da operação", gt=0)
    descricao: Optional[str] = Field(None, description="Descrição da operação", max_length=255)
    
    @field_validator('valor')
    def validar_valor(cls, v: float) -> float:
        """Valida que o valor seja positivo."""
        if v <= 0:
            raise ValueError("O valor deve ser maior que zero")
        return v


# Alias para manter compatibilidade com código existente
ContaBancariaAtualizacaoSaldo = AtualizacaoSaldo 