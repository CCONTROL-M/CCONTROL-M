"""Tipos enumerados utilizados no sistema CCONTROL-M."""
import enum
from typing import List


class TipoLancamento(str, enum.Enum):
    """Tipos de lançamentos financeiros."""
    
    RECEITA = "receita"
    DESPESA = "despesa"
    
    @classmethod
    def list(cls) -> List[str]:
        """Retorna lista de valores do enum."""
        return [e.value for e in cls]


class StatusLancamento(str, enum.Enum):
    """Status de lançamentos financeiros."""
    
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"
    
    @classmethod
    def list(cls) -> List[str]:
        """Retorna lista de valores do enum."""
        return [e.value for e in cls]


class StatusParcela(str, enum.Enum):
    """Status de parcelas de pagamento."""
    
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"
    
    @classmethod
    def list(cls) -> List[str]:
        """Retorna lista de valores do enum."""
        return [e.value for e in cls]


class StatusVenda(str, enum.Enum):
    """Status de vendas."""
    
    PENDENTE = "pendente"
    PAGO = "pago"
    CANCELADO = "cancelado"
    PARCIAL = "parcial"
    
    @classmethod
    def list(cls) -> List[str]:
        """Retorna lista de valores do enum."""
        return [e.value for e in cls] 