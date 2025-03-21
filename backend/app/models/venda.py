"""Modelo de Venda para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Venda(Base, TimestampedModel):
    """
    Modelo de venda no sistema.
    
    Representa uma operação de venda de produtos ou serviços no sistema CCONTROL-M.
    Inclui informações como cliente, valor, data, status, itens, parcelamento e
    seu relacionamento com lançamentos financeiros.
    """
    
    __tablename__ = "vendas"
    
    id_venda: Mapped[uuid.UUID] = mapped_column(
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
    numero_venda: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    data_venda: Mapped[date] = mapped_column(Date, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    valor_desconto: Mapped[float] = mapped_column(Float, default=0.0)
    valor_liquido: Mapped[float] = mapped_column(Float, nullable=False)
    itens_venda: Mapped[dict] = mapped_column(JSON, nullable=False)
    parcelado: Mapped[bool] = mapped_column(Boolean, default=False)
    total_parcelas: Mapped[Optional[int]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pendente", "concluida", "cancelada", name="status_venda"),
        default="pendente",
        nullable=False
    )
    nota_fiscal: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="vendas")
    cliente = relationship("Cliente", back_populates="vendas")
    lancamentos = relationship("Lancamento", back_populates="venda")
    
    def __repr__(self) -> str:
        """Representação em string da venda."""
        return f"<Venda(id={self.id_venda}, descricao='{self.descricao}', valor_total={self.valor_total}, status='{self.status}')>" 