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
    """Schema para resumo de pagamentos em um período."""
    periodo: str = Field(..., description="Tipo de período (diario, mensal, anual)")
    ano: int = Field(..., description="Ano do período")
    mes: Optional[int] = Field(None, description="Mês do período (se aplicável)")
    total_valor: float = Field(..., description="Valor total dos pagamentos")
    quantidade: int = Field(..., description="Quantidade de pagamentos")
    dados: List[Dict[str, Any]] = Field(..., description="Dados detalhados dos pagamentos")


class ResumoRecebimentos(BaseModel):
    """Schema para resumo de recebimentos em um período."""
    periodo: str = Field(..., description="Tipo de período (diario, mensal, anual)")
    ano: int = Field(..., description="Ano do período")
    mes: Optional[int] = Field(None, description="Mês do período (se aplicável)")
    total_valor: float = Field(..., description="Valor total dos recebimentos")
    quantidade: int = Field(..., description="Quantidade de recebimentos")
    dados: List[Dict[str, Any]] = Field(..., description="Dados detalhados dos recebimentos")


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