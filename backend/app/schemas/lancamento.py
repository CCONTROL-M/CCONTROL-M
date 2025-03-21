"""Schemas Pydantic para Lançamentos Financeiros no sistema CCONTROL-M."""
from datetime import date, datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class TipoLancamento(str, Enum):
    """Tipos de lançamento financeiro."""
    ENTRADA = "entrada"
    SAIDA = "saida"


class StatusLancamento(str, Enum):
    """Status possíveis para lançamentos financeiros."""
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"


class LancamentoBase(BaseModel):
    """Schema base com campos comuns para Lançamentos."""
    descricao: str = Field(..., description="Descrição do lançamento", min_length=3, max_length=255)
    tipo: TipoLancamento = Field(..., description="Tipo do lançamento: entrada ou saída")
    valor: float = Field(..., description="Valor do lançamento", gt=0)
    data_lancamento: date = Field(..., description="Data do lançamento")
    data_vencimento: date = Field(..., description="Data de vencimento")
    observacao: Optional[str] = Field(None, description="Observações adicionais sobre o lançamento", max_length=1000)
    conciliado: bool = Field(False, description="Indica se o lançamento foi conciliado")
    
    @field_validator('valor')
    def validar_valor(cls, v: float) -> float:
        """Valida que o valor seja positivo."""
        if v <= 0:
            raise ValueError("Valor do lançamento deve ser maior que zero")
        return v
    
    @field_validator('data_vencimento')
    def validar_data_vencimento(cls, v: date, values) -> date:
        """Verifica se a data de vencimento é igual ou posterior à data do lançamento."""
        if 'data_lancamento' in values.data and v < values.data['data_lancamento']:
            raise ValueError("Data de vencimento não pode ser anterior à data do lançamento")
        return v


class LancamentoCreate(LancamentoBase):
    """Schema para criação de lançamentos."""
    id_empresa: UUID = Field(..., description="ID da empresa associada ao lançamento")
    id_cliente: Optional[UUID] = Field(None, description="ID do cliente associado (opcional)")
    id_conta: UUID = Field(..., description="ID da conta bancária associada")
    id_forma_pagamento: UUID = Field(..., description="ID da forma de pagamento")
    id_venda: Optional[UUID] = Field(None, description="ID da venda associada (opcional)")
    status: StatusLancamento = Field(StatusLancamento.PENDENTE, description="Status do lançamento")
    data_pagamento: Optional[date] = Field(None, description="Data de pagamento (se houver)")
    numero_parcela: Optional[int] = Field(None, description="Número da parcela (se for parcelado)")
    total_parcelas: Optional[int] = Field(None, description="Total de parcelas (se for parcelado)")
    
    @model_validator(mode='after')
    def validar_pagamento(self) -> 'LancamentoCreate':
        """
        Valida a consistência entre status e data de pagamento.
        - Se status for 'pago', data_pagamento deve estar preenchida
        - Se data_pagamento estiver preenchida, status deve ser 'pago'
        """
        if self.status == StatusLancamento.PAGO and not self.data_pagamento:
            raise ValueError("Data de pagamento é obrigatória para lançamentos com status 'pago'")
        
        if self.data_pagamento and self.status != StatusLancamento.PAGO:
            raise ValueError("Lançamentos com data de pagamento devem ter status 'pago'")
        
        return self
    
    @model_validator(mode='after')
    def validar_parcelas(self) -> 'LancamentoCreate':
        """Valida a consistência das informações de parcelamento."""
        if self.numero_parcela is not None and self.total_parcelas is None:
            raise ValueError("Se número da parcela for informado, total de parcelas também deve ser")
        
        if self.total_parcelas is not None and self.numero_parcela is None:
            raise ValueError("Se total de parcelas for informado, número da parcela também deve ser")
        
        if self.numero_parcela is not None and self.total_parcelas is not None:
            if self.numero_parcela <= 0 or self.total_parcelas <= 0:
                raise ValueError("Número da parcela e total de parcelas devem ser maiores que zero")
            
            if self.numero_parcela > self.total_parcelas:
                raise ValueError("Número da parcela não pode ser maior que o total de parcelas")
        
        return self


class LancamentoUpdate(BaseModel):
    """Schema para atualização de lançamentos (todos campos opcionais)."""
    descricao: Optional[str] = Field(None, description="Descrição do lançamento", min_length=3, max_length=255)
    tipo: Optional[TipoLancamento] = Field(None, description="Tipo do lançamento: entrada ou saída")
    valor: Optional[float] = Field(None, description="Valor do lançamento", gt=0)
    data_lancamento: Optional[date] = Field(None, description="Data do lançamento")
    data_vencimento: Optional[date] = Field(None, description="Data de vencimento")
    data_pagamento: Optional[date] = Field(None, description="Data de pagamento (se houver)")
    observacao: Optional[str] = Field(None, description="Observações adicionais sobre o lançamento", max_length=1000)
    status: Optional[StatusLancamento] = Field(None, description="Status do lançamento")
    conciliado: Optional[bool] = Field(None, description="Indica se o lançamento foi conciliado")
    id_cliente: Optional[UUID] = Field(None, description="ID do cliente associado")
    id_conta: Optional[UUID] = Field(None, description="ID da conta bancária associada")
    id_forma_pagamento: Optional[UUID] = Field(None, description="ID da forma de pagamento")
    
    @field_validator('valor')
    def validar_valor(cls, v: Optional[float]) -> Optional[float]:
        """Valida que o valor, se fornecido, seja positivo."""
        if v is not None and v <= 0:
            raise ValueError("Valor do lançamento deve ser maior que zero")
        return v


class LancamentoInDB(LancamentoBase):
    """Schema para lançamento com campos específicos do banco de dados."""
    id_lancamento: UUID
    id_empresa: UUID
    id_cliente: Optional[UUID] = None
    id_conta: UUID
    id_forma_pagamento: UUID
    id_venda: Optional[UUID] = None
    status: StatusLancamento
    data_pagamento: Optional[date] = None
    numero_parcela: Optional[int] = None
    total_parcelas: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Lancamento(LancamentoInDB):
    """Schema completo de lançamento para resposta da API."""
    pass


class LancamentoList(BaseModel):
    """Schema reduzido para listagem de lançamentos."""
    id_lancamento: UUID
    descricao: str
    tipo: TipoLancamento
    valor: float
    data_vencimento: date
    data_pagamento: Optional[date] = None
    status: StatusLancamento
    conciliado: bool
    cliente_nome: Optional[str] = None
    conta_nome: str
    forma_pagamento_nome: str
    
    class Config:
        from_attributes = True


class LancamentoTotais(BaseModel):
    """Schema para retornar totais de lançamentos (por tipo ou status)."""
    total_entradas: float = Field(0, description="Total de entradas")
    total_saidas: float = Field(0, description="Total de saídas")
    saldo: float = Field(0, description="Saldo (entradas - saídas)")
    total_pendentes: float = Field(0, description="Total de lançamentos pendentes")
    total_pagos: float = Field(0, description="Total de lançamentos pagos")
    total_cancelados: float = Field(0, description="Total de lançamentos cancelados") 