"""Modelo de Venda para o sistema CCONTROL-M."""
import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Float, Text, ForeignKey, Boolean, Integer, Date, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel
from app.models.enums import StatusVenda


class Venda(Base, TimestampedModel):
    """
    Modelo de venda.
    
    Representa uma venda de produtos ou serviços no sistema CCONTROL-M.
    """
    
    __tablename__ = "vendas"
    
    id_venda: Mapped[uuid.UUID] = mapped_column(
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
    
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    data_venda: Mapped[date] = mapped_column(
        Date, 
        nullable=False,
        default=date.today
    )
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    valor_desconto: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    valor_liquido: Mapped[float] = mapped_column(Float, nullable=False)
    
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    itens_venda: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    parcelado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    total_parcelas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    status: Mapped[StatusVenda] = mapped_column(
        Enum(StatusVenda), 
        default=StatusVenda.PENDENTE,
        nullable=False
    )
    
    nota_fiscal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")
    lancamentos = relationship("Lancamento", back_populates="venda")
    
    def __repr__(self) -> str:
        """Representação em string da venda."""
        return (
            f"<Venda(id={self.id_venda}, "
            f"descricao='{self.descricao}', "
            f"valor_total={self.valor_total}, "
            f"status={self.status})>"
        ) 