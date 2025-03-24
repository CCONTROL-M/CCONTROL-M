"""
Schemas para relatórios do sistema CCONTROL-M.

Este módulo contém definições de schemas para relatórios financeiros
e análises utilizadas pelos serviços relacionados a contas a pagar e a receber.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class RelatorioContasPagar(BaseModel):
    """Schema para relatório de contas a pagar."""
    total_geral: float = Field(..., description="Valor total de todas as contas no período")
    total_pago: float = Field(..., description="Valor total já pago no período")
    total_pendente: float = Field(..., description="Valor total pendente no período")
    total_contas: int = Field(..., description="Número total de contas no período")
    contas_vencidas: int = Field(..., description="Número de contas vencidas")
    contas_a_vencer: int = Field(..., description="Número de contas a vencer")
    valor_vencido: float = Field(..., description="Valor total vencido")
    valor_a_vencer: float = Field(..., description="Valor total a vencer")
    por_status: Dict[str, float] = Field(..., description="Valor total por status")
    por_categoria: Dict[str, float] = Field(..., description="Valor total por categoria")
    data_geracao: datetime = Field(..., description="Data e hora de geração do relatório")
    periodo_inicial: Optional[date] = Field(None, description="Data inicial do período")
    periodo_final: Optional[date] = Field(None, description="Data final do período")


class RelatorioContasReceber(BaseModel):
    """Schema para relatório de contas a receber."""
    total_geral: float = Field(..., description="Valor total de todas as contas no período")
    total_recebido: float = Field(..., description="Valor total já recebido no período")
    total_pendente: float = Field(..., description="Valor total pendente no período")
    total_contas: int = Field(..., description="Número total de contas no período")
    contas_vencidas: int = Field(..., description="Número de contas vencidas")
    contas_a_vencer: int = Field(..., description="Número de contas a vencer")
    valor_vencido: float = Field(..., description="Valor total vencido")
    valor_a_vencer: float = Field(..., description="Valor total a vencer")
    por_status: Dict[str, float] = Field(..., description="Valor total por status")
    por_cliente: Dict[str, float] = Field(..., description="Valor total por cliente")
    data_geracao: datetime = Field(..., description="Data e hora de geração do relatório")
    periodo_inicial: Optional[date] = Field(None, description="Data inicial do período")
    periodo_final: Optional[date] = Field(None, description="Data final do período")


class ResumoPagamentos(BaseModel):
    """
    Resumo de pagamentos em um período específico.
    """
    periodo_inicio: date
    periodo_fim: date
    total_pago: float = Field(default=0.0, description="Valor total de pagamentos no período")
    quantidade: int = Field(default=0, description="Quantidade de pagamentos no período")
    por_categoria: Dict[str, float] = Field(default_factory=dict, description="Pagamentos agrupados por categoria")
    por_forma_pagamento: Dict[str, float] = Field(default_factory=dict, description="Pagamentos agrupados por forma de pagamento")


class ResumoRecebimentos(BaseModel):
    """
    Resumo de recebimentos em um período específico.
    """
    periodo_inicio: date
    periodo_fim: date
    total_recebido: float = Field(default=0.0, description="Valor total de recebimentos no período")
    quantidade: int = Field(default=0, description="Quantidade de recebimentos no período")
    por_categoria: Dict[str, float] = Field(default_factory=dict, description="Recebimentos agrupados por categoria")
    por_forma_pagamento: Dict[str, float] = Field(default_factory=dict, description="Recebimentos agrupados por forma de pagamento")


class ResumoDashboard(BaseModel):
    """
    Resumo financeiro para o dashboard.
    """
    caixa_atual: float = Field(default=0.0, description="Saldo total disponível nas contas bancárias")
    total_receber: float = Field(default=0.0, description="Total de valores a receber")
    total_pagar: float = Field(default=0.0, description="Total de valores a pagar")
    recebimentos_hoje: float = Field(default=0.0, description="Total de recebimentos do dia")
    pagamentos_hoje: float = Field(default=0.0, description="Total de pagamentos do dia")


class FluxoCaixa(BaseModel):
    """Schema para relatório de fluxo de caixa."""
    periodo_inicial: date = Field(..., description="Data inicial do período")
    periodo_final: date = Field(..., description="Data final do período")
    saldo_inicial: float = Field(..., description="Saldo inicial no período")
    saldo_final: float = Field(..., description="Saldo final no período")
    total_entradas: float = Field(..., description="Total de entradas no período")
    total_saidas: float = Field(..., description="Total de saídas no período")
    resultado_periodo: float = Field(..., description="Resultado líquido do período")
    detalhamento_diario: List[Dict[str, Union[date, float, int]]] = Field(..., description="Detalhamento diário")
    data_geracao: datetime = Field(..., description="Data e hora de geração do relatório") 