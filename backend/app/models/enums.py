"""Definição de enumerações para o sistema CCONTROL-M."""
from enum import Enum, auto

class TipoLancamento(str, Enum):
    """Tipo de lançamento financeiro."""
    ENTRADA = "entrada"
    SAIDA = "saida"

class StatusLancamento(str, Enum):
    """Status do lançamento financeiro."""
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"

class StatusVenda(str, Enum):
    """Status de uma venda."""
    EM_ABERTO = "em_aberto"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    PARCIAL = "parcial"

class StatusParcela(str, Enum):
    """Status de uma parcela."""
    PENDENTE = "pendente"
    PAGA = "paga"
    CANCELADA = "cancelada"
    ATRASADA = "atrasada" 