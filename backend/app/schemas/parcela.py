"""Schemas Pydantic para Parcelas no sistema CCONTROL-M."""
from datetime import date, datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class StatusParcela(str, Enum):
    """Status possíveis para parcelas."""
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"


class ParcelaBase(BaseModel):
    """Schema base com campos comuns para Parcelas."""
    numero_parcela: int = Field(..., description="Número da parcela", gt=0)
    valor: float = Field(..., description="Valor da parcela", gt=0)
    data_vencimento: date = Field(..., description="Data de vencimento da parcela")
    observacao: Optional[str] = Field(None, description="Observações adicionais sobre a parcela", max_length=1000)
    
    @field_validator('valor')
    def validar_valor(cls, v: float) -> float:
        """Valida que o valor seja positivo."""
        if v <= 0:
            raise ValueError("Valor da parcela deve ser maior que zero")
        return v
    
    @field_validator('numero_parcela')
    def validar_numero_parcela(cls, v: int) -> int:
        """Valida que o número da parcela seja positivo."""
        if v <= 0:
            raise ValueError("Número da parcela deve ser maior que zero")
        return v


class ParcelaCreate(ParcelaBase):
    """Schema para criação de parcelas."""
    id_lancamento: UUID = Field(..., description="ID do lançamento associado à parcela")
    status: StatusParcela = Field(StatusParcela.PENDENTE, description="Status da parcela")
    data_pagamento: Optional[date] = Field(None, description="Data de pagamento (se houver)")
    
    @model_validator(mode='after')
    def validar_pagamento(self) -> 'ParcelaCreate':
        """
        Valida a consistência entre status e data de pagamento.
        - Se status for 'pago', data_pagamento deve estar preenchida
        - Se data_pagamento estiver preenchida, status deve ser 'pago'
        """
        if self.status == StatusParcela.PAGO and not self.data_pagamento:
            raise ValueError("Data de pagamento é obrigatória para parcelas com status 'pago'")
        
        if self.data_pagamento and self.status != StatusParcela.PAGO:
            raise ValueError("Parcelas com data de pagamento devem ter status 'pago'")
        
        return self


class ParcelaUpdate(BaseModel):
    """Schema para atualização de parcelas (todos campos opcionais)."""
    numero_parcela: Optional[int] = Field(None, description="Número da parcela", gt=0)
    valor: Optional[float] = Field(None, description="Valor da parcela", gt=0)
    data_vencimento: Optional[date] = Field(None, description="Data de vencimento da parcela")
    data_pagamento: Optional[date] = Field(None, description="Data de pagamento da parcela")
    status: Optional[StatusParcela] = Field(None, description="Status da parcela")
    observacao: Optional[str] = Field(None, description="Observações adicionais sobre a parcela", max_length=1000)
    
    @field_validator('valor')
    def validar_valor(cls, v: Optional[float]) -> Optional[float]:
        """Valida que o valor, se fornecido, seja positivo."""
        if v is not None and v <= 0:
            raise ValueError("Valor da parcela deve ser maior que zero")
        return v
    
    @field_validator('numero_parcela')
    def validar_numero_parcela(cls, v: Optional[int]) -> Optional[int]:
        """Valida que o número da parcela, se fornecido, seja positivo."""
        if v is not None and v <= 0:
            raise ValueError("Número da parcela deve ser maior que zero")
        return v


class ParcelaInDB(ParcelaBase):
    """Schema para parcela com campos específicos do banco de dados."""
    id_parcela: UUID
    id_lancamento: UUID
    status: StatusParcela
    data_pagamento: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Parcela(ParcelaInDB):
    """Schema completo de parcela para resposta da API."""
    pass


class ParcelaList(BaseModel):
    """Schema reduzido para listagem de parcelas."""
    id_parcela: UUID
    id_lancamento: UUID
    numero_parcela: int
    valor: float
    data_vencimento: date
    data_pagamento: Optional[date] = None
    status: StatusParcela
    
    class Config:
        from_attributes = True


class ParcelaPagamento(BaseModel):
    """Schema para registrar o pagamento de uma parcela."""
    data_pagamento: date = Field(..., description="Data de pagamento da parcela")
    valor_pago: float = Field(..., description="Valor efetivamente pago", gt=0)
    id_conta_bancaria: UUID = Field(..., description="ID da conta bancária utilizada para o pagamento")
    observacao: Optional[str] = Field(None, description="Observações sobre o pagamento", max_length=1000)
    
    @field_validator('valor_pago')
    def validar_valor_pago(cls, v: float) -> float:
        """Valida que o valor pago seja positivo."""
        if v <= 0:
            raise ValueError("Valor pago deve ser maior que zero")
        return v


class ParcelaResumo(BaseModel):
    """Schema para resumo de parcelas usado no dashboard."""
    quantidade: int = Field(0, description="Quantidade de parcelas")
    valor_total: float = Field(0.0, description="Valor total das parcelas")
    
    class Config:
        from_attributes = True


class ParcelaDashboard(BaseModel):
    """Schema para dashboard de parcelas."""
    vencidas: ParcelaResumo = Field(..., description="Resumo de parcelas vencidas")
    proximas: ParcelaResumo = Field(..., description="Resumo de parcelas próximas do vencimento")
    pagas_mes_atual: ParcelaResumo = Field(..., description="Resumo de parcelas pagas no mês atual")
    pendentes_total: ParcelaResumo = Field(..., description="Resumo de todas as parcelas pendentes")
    
    class Config:
        from_attributes = True 