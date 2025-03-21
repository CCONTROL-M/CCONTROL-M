"""Modelo de Lançamento para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Lancamento(Base, TimestampedModel):
    """
    Modelo de lançamento financeiro no sistema.
    
    Representa uma transação financeira (entrada ou saída) de uma empresa no sistema CCONTROL-M.
    Inclui informações como tipo de transação, valor, data, status, e associações com cliente,
    conta bancária, forma de pagamento e parcelas.
    """
    
    __tablename__ = "lancamentos"
    
    id_lancamento: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    id_cliente: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="SET NULL"),
        nullable=True
    )
    id_conta: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contas_bancarias.id_conta", ondelete="RESTRICT")
    )
    id_forma_pagamento: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("formas_pagamento.id_forma", ondelete="RESTRICT")
    )
    id_venda: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("vendas.id_venda", ondelete="SET NULL"),
        nullable=True
    )
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    tipo: Mapped[str] = mapped_column(
        Enum("entrada", "saida", name="tipo_lancamento"),
        nullable=False
    )
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data_lancamento: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pendente", "pago", "cancelado", name="status_lancamento"),
        default="pendente",
        nullable=False
    )
    conciliado: Mapped[bool] = mapped_column(Boolean, default=False)
    numero_parcela: Mapped[Optional[int]] = mapped_column(nullable=True)
    total_parcelas: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="lancamentos")
    cliente = relationship("Cliente", back_populates="lancamentos")
    conta_bancaria = relationship("ContaBancaria", back_populates="lancamentos")
    forma_pagamento = relationship("FormaPagamento", back_populates="lancamentos")
    venda = relationship("Venda", back_populates="lancamentos")
    parcelas = relationship("Parcela", back_populates="lancamento")
    
    def __repr__(self) -> str:
        """Representação em string do lançamento."""
        return f"<Lancamento(id={self.id_lancamento}, descricao='{self.descricao}', valor={self.valor}, tipo='{self.tipo}')>" 