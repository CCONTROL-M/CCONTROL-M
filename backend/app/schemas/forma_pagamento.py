"""Schemas Pydantic para Formas de Pagamento no sistema CCONTROL-M."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class FormaPagamentoBase(BaseModel):
    """Schema base com campos comuns para Forma de Pagamento."""
    nome: str = Field(..., description="Nome da forma de pagamento", min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, description="Descrição detalhada da forma de pagamento", max_length=255)
    icone: Optional[str] = Field(None, description="Ícone ou imagem da forma de pagamento", max_length=255)
    dias_compensacao: int = Field(0, description="Dias para compensação do pagamento", ge=0)
    taxa_percentual: float = Field(0.0, description="Taxa percentual cobrada pela forma de pagamento", ge=0.0)
    taxa_fixa: float = Field(0.0, description="Taxa fixa cobrada pela forma de pagamento", ge=0.0)
    ativa: bool = Field(True, description="Status de ativação da forma de pagamento")
    
    @field_validator('dias_compensacao')
    def validar_dias_compensacao(cls, v: int) -> int:
        """Valida que os dias de compensação sejam não-negativos."""
        if v < 0:
            raise ValueError("Dias de compensação não podem ser negativos")
        return v
    
    @field_validator('taxa_percentual', 'taxa_fixa')
    def validar_taxas(cls, v: float) -> float:
        """Valida que as taxas sejam não-negativas."""
        if v < 0:
            raise ValueError("Taxas não podem ser negativas")
        return v


class FormaPagamentoCreate(FormaPagamentoBase):
    """Schema para criação de formas de pagamento."""
    id_empresa: UUID = Field(..., description="ID da empresa a qual a forma de pagamento pertence")


class FormaPagamentoUpdate(BaseModel):
    """Schema para atualização de formas de pagamento (todos campos opcionais)."""
    nome: Optional[str] = Field(None, description="Nome da forma de pagamento", min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, description="Descrição detalhada da forma de pagamento", max_length=255)
    icone: Optional[str] = Field(None, description="Ícone ou imagem da forma de pagamento", max_length=255)
    dias_compensacao: Optional[int] = Field(None, description="Dias para compensação do pagamento", ge=0)
    taxa_percentual: Optional[float] = Field(None, description="Taxa percentual cobrada pela forma de pagamento", ge=0.0)
    taxa_fixa: Optional[float] = Field(None, description="Taxa fixa cobrada pela forma de pagamento", ge=0.0)
    ativa: Optional[bool] = Field(None, description="Status de ativação da forma de pagamento")


class FormaPagamentoInDB(FormaPagamentoBase):
    """Schema para forma de pagamento com campos específicos do banco de dados."""
    id_forma: UUID
    id_empresa: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FormaPagamento(FormaPagamentoInDB):
    """Schema completo de forma de pagamento para resposta da API."""
    pass


class FormaPagamentoList(BaseModel):
    """Schema reduzido para listagem de formas de pagamento."""
    id_forma: UUID
    nome: str
    dias_compensacao: int
    taxa_percentual: float
    taxa_fixa: float
    ativa: bool
    
    class Config:
        from_attributes = True 