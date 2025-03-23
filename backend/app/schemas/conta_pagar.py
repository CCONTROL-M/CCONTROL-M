"""Schemas para validação de dados de contas a pagar."""
from uuid import UUID
from typing import Optional, List
from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class StatusContaPagar(str, Enum):
    """Status possíveis para uma conta a pagar."""
    
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    VENCIDO = "VENCIDO"
    CANCELADO = "CANCELADO"


class ContaPagarBase(BaseModel):
    """Schema base para contas a pagar."""
    
    descricao: str = Field(..., min_length=3, max_length=100)
    valor: Decimal = Field(..., gt=0)
    data_vencimento: date
    data_pagamento: Optional[date] = None
    status: StatusContaPagar = Field(default=StatusContaPagar.PENDENTE)
    observacao: Optional[str] = Field(None, max_length=500)
    fornecedor_id: Optional[UUID] = None
    categoria_id: Optional[UUID] = None


class ContaPagarCreate(ContaPagarBase):
    """Schema para criação de contas a pagar."""
    id_empresa: UUID = Field(..., description="ID da empresa")


class ContaPagarUpdate(BaseModel):
    """Schema para atualização de contas a pagar."""
    
    descricao: Optional[str] = Field(None, min_length=3, max_length=100)
    valor: Optional[Decimal] = Field(None, gt=0)
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    status: Optional[StatusContaPagar] = None
    observacao: Optional[str] = Field(None, max_length=500)
    fornecedor_id: Optional[UUID] = None
    categoria_id: Optional[UUID] = None


class ContaPagar(ContaPagarBase):
    """Schema para retorno de contas a pagar."""
    
    id_conta: UUID
    empresa_id: UUID
    
    class Config:
        """Configurações do schema."""
        
        from_attributes = True


class ContaPagarList(BaseModel):
    """Schema para listar contas a pagar com paginação."""
    
    items: List[ContaPagar]
    total: int
    page: int
    size: int
    pages: int


class ContaPagarPagamento(BaseModel):
    """Schema para registrar pagamento de uma conta a pagar."""
    
    data_pagamento: date = Field(..., description="Data em que o pagamento foi realizado")
    valor_pago: Decimal = Field(..., gt=0, description="Valor pago")
    observacoes: Optional[str] = Field(None, max_length=500) 