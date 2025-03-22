"""Modelo de Categoria para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Categoria(Base, TimestampedModel):
    """
    Modelo de categoria no sistema.
    
    Representa uma categoria para classificação de lançamentos financeiros no sistema CCONTROL-M.
    """
    
    __tablename__ = "categorias"
    
    id_categoria: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="categorias")
    lancamentos = relationship("Lancamento", back_populates="categoria")
    
    def __repr__(self) -> str:
        """Representação em string da categoria."""
        return f"<Categoria(id={self.id_categoria}, descricao='{self.descricao}')>" 