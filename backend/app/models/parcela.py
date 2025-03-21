"""Modelo de Parcela para o sistema CCONTROL-M."""
import uuid
from datetime import date
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, Integer, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel
from app.models.enums import StatusParcela


class Parcela(Base, TimestampedModel):
    """
    Modelo de parcela de pagamento.
    
    Representa uma parcela de pagamento de um lançamento financeiro.
    """
    
    __tablename__ = "parcelas"
    
    id_parcela: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_lancamento: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lancamentos.id_lancamento", ondelete="CASCADE"),
        nullable=False
    )
    
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    comprovante_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    status: Mapped[StatusParcela] = mapped_column(
        Enum(StatusParcela), 
        default=StatusParcela.PENDENTE,
        nullable=False
    )
    
    # Relacionamentos
    lancamento = relationship("Lancamento", back_populates="parcelas")
    
    def __repr__(self) -> str:
        """Representação em string da parcela."""
        return (
            f"<Parcela(id={self.id_parcela}, "
            f"numero={self.numero}, "
            f"valor={self.valor}, "
            f"status={self.status})>"
        ) 