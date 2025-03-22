"""Modelo de Centro de Custo para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class CentroCusto(Base, TimestampedModel):
    """
    Modelo de centro de custo no sistema.
    
    Representa um centro de custo para classificação de lançamentos financeiros no sistema CCONTROL-M.
    """
    
    __tablename__ = "centros_custo"
    
    id_centro_custo: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="centros_custo")
    lancamentos = relationship("Lancamento", back_populates="centro_custo")
    
    def __repr__(self) -> str:
        """Representação em string do centro de custo."""
        return f"<CentroCusto(id={self.id_centro_custo}, descricao='{self.descricao}')>" 