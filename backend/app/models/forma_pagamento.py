"""Modelo de Forma de Pagamento para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Integer, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class FormaPagamento(Base, TimestampedModel):
    """
    Modelo de forma de pagamento.
    
    Representa uma forma de pagamento no sistema CCONTROL-M.
    """
    
    __tablename__ = "formas_pagamento"
    
    id_forma: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    icone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dias_compensacao: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    taxa_percentual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    taxa_fixa: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="formas_pagamento")
    lancamentos = relationship("Lancamento", back_populates="forma_pagamento")
    
    def __repr__(self) -> str:
        """Representação em string da forma de pagamento."""
        return f"<FormaPagamento(id={self.id_forma}, nome='{self.nome}')>" 