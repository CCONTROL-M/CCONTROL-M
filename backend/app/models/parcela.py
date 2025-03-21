"""Modelo de Parcela para o sistema CCONTROL-M."""
import uuid
from typing import Optional
from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Parcela(Base, TimestampedModel):
    """
    Modelo de parcela de lançamento no sistema.
    
    Representa uma parcela de um lançamento financeiro parcelado no sistema CCONTROL-M.
    Inclui informações como número da parcela, valor, data de vencimento e status.
    """
    
    __tablename__ = "parcelas"
    
    id_parcela: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_lancamento: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lancamentos.id_lancamento", ondelete="CASCADE")
    )
    numero_parcela: Mapped[int] = mapped_column(nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pendente", "pago", "cancelado", name="status_parcela"),
        default="pendente",
        nullable=False
    )
    observacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    lancamento = relationship("Lancamento", back_populates="parcelas")
    
    def __repr__(self) -> str:
        """Representação em string da parcela."""
        return f"<Parcela(id={self.id_parcela}, lancamento={self.id_lancamento}, n°={self.numero_parcela}, valor={self.valor})>" 