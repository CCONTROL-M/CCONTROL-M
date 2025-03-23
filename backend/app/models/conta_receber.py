"""Modelo de Conta a Receber para o sistema CCONTROL-M."""
import uuid
from datetime import date
from typing import Optional

from sqlalchemy import String, Text, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel
from app.schemas.conta_receber import StatusContaReceber


class ContaReceber(Base, TimestampedModel):
    """
    Modelo de conta a receber do sistema.
    
    Representa uma conta a receber no sistema CCONTROL-M.
    """
    
    __tablename__ = "contas_receber"
    
    id_conta_receber: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    id_cliente: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="SET NULL"),
        nullable=True
    )
    id_lancamento: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("lancamentos.id_lancamento", ondelete="SET NULL"),
        nullable=True
    )
    id_venda: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("vendas.id_venda", ondelete="SET NULL"),
        nullable=True
    )
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_recebimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[StatusContaReceber] = mapped_column(
        Enum(StatusContaReceber), 
        nullable=False, 
        default=StatusContaReceber.pendente
    )
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="contas_receber")
    cliente = relationship("Cliente", back_populates="contas_receber")
    lancamento = relationship("Lancamento", back_populates="contas_receber")
    venda = relationship("Venda", back_populates="contas_receber")
    
    def __repr__(self) -> str:
        return f"<ContaReceber(id={self.id_conta_receber}, descricao='{self.descricao}', valor={self.valor}, vencimento={self.data_vencimento})>" 