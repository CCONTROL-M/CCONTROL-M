"""Modelo de Centro de Custo para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class CentroCusto(Base, TimestampedModel):
    """
    Modelo de centro de custo.
    
    Representa um centro de custo para classificação de lançamentos financeiros.
    """
    
    __tablename__ = "centro_custos"
    
    id_centro: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="centro_custos")
    lancamentos = relationship("Lancamento", back_populates="centro_custo")
    
    def __repr__(self) -> str:
        """Representação em string do centro de custo."""
        return f"<CentroCusto(id={self.id_centro}, nome='{self.nome}')>" 