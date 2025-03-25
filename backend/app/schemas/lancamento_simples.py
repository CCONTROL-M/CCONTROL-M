"""Schemas simplificados para testes de Lançamentos Financeiros."""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class Lancamento(BaseModel):
    """Schema simplificado para lançamentos em testes."""
    id: UUID
    descricao: str
    valor: float
    data_lancamento: str
    data_pagamento: Optional[str] = None
    tipo: str  # "RECEITA" ou "DESPESA"
    status: str  # "PENDENTE", "PAGO" ou "CANCELADO"
    id_categoria: UUID
    id_empresa: UUID
    

class LancamentoCreate(BaseModel):
    """Schema para criação de lançamentos em testes."""
    descricao: str
    valor: float
    data_lancamento: str
    data_pagamento: Optional[str] = None
    tipo: str  # "RECEITA" ou "DESPESA"
    id_categoria: UUID
    id_empresa: UUID
    id_conta: Optional[UUID] = None
    id_centro_custo: Optional[UUID] = None


class LancamentoUpdate(BaseModel):
    """Schema para atualização de lançamentos em testes."""
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_lancamento: Optional[str] = None
    data_pagamento: Optional[str] = None
    tipo: Optional[str] = None  # "RECEITA" ou "DESPESA"
    status: Optional[str] = None  # "PENDENTE", "PAGO" ou "CANCELADO"
    id_categoria: Optional[UUID] = None


class LancamentoWithDetalhes(Lancamento):
    """Schema para lançamento com informações detalhadas."""
    categoria_nome: Optional[str] = None
    conta_nome: Optional[str] = None
    centro_custo_nome: Optional[str] = None
    criado_por: Optional[str] = None
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Schema para resposta paginada."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


class RelatorioFinanceiro(BaseModel):
    """Schema simplificado para relatório financeiro."""
    periodo: str
    entradas: float
    saidas: float
    saldo: float
    detalhes: List[Dict[str, Any]] 