"""Modelo de Lançamento Financeiro para o sistema CCONTROL-M."""
import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Float, Text, ForeignKey, Boolean, Integer, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel
from app.models.enums import TipoLancamento, StatusLancamento


class Lancamento(Base, TimestampedModel):
    """
    Modelo de lançamento financeiro.
    
    Representa uma entrada ou saída financeira no sistema CCONTROL-M.
    """
    
    __tablename__ = "lancamentos"
    
    id_lancamento: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    id_categoria: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categorias.id_categoria", ondelete="SET NULL"),
        nullable=True
    )
    id_centro: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("centro_custos.id_centro", ondelete="SET NULL"),
        nullable=True
    )
    id_cliente: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="SET NULL"),
        nullable=True
    )
    id_fornecedor: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("fornecedores.id_fornecedor", ondelete="SET NULL"),
        nullable=True
    )
    id_conta: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("contas_bancarias.id_conta", ondelete="SET NULL"),
        nullable=True
    )
    id_venda: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("vendas.id_venda", ondelete="SET NULL"),
        nullable=True
    )
    id_forma: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("formas_pagamento.id_forma", ondelete="SET NULL"),
        nullable=True
    )
    
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data_lancamento: Mapped[date] = mapped_column(
        Date, 
        nullable=False,
        default=date.today
    )
    data_vencimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_pagamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    comprovante_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    parcelado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    numero_parcela: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_parcelas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recorrente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    
    tipo: Mapped[TipoLancamento] = mapped_column(
        Enum(TipoLancamento), 
        nullable=False
    )
    status: Mapped[StatusLancamento] = mapped_column(
        Enum(StatusLancamento), 
        default=StatusLancamento.PENDENTE,
        nullable=False
    )
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="lancamentos")
    categoria = relationship("Categoria", back_populates="lancamentos")
    centro_custo = relationship("CentroCusto", back_populates="lancamentos")
    cliente = relationship("Cliente", back_populates="lancamentos")
    fornecedor = relationship("Fornecedor", back_populates="lancamentos")
    conta_bancaria = relationship("ContaBancaria", back_populates="lancamentos")
    venda = relationship("Venda", back_populates="lancamentos")
    forma_pagamento = relationship("FormaPagamento", back_populates="lancamentos")
    parcelas: Mapped[List["Parcela"]] = relationship(
        back_populates="lancamento", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Representação em string do lançamento."""
        return (
            f"<Lancamento(id={self.id_lancamento}, "
            f"descricao='{self.descricao}', "
            f"valor={self.valor}, "
            f"tipo={self.tipo}, "
            f"status={self.status})>"
        ) 