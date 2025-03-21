"""Modelo de Categoria para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Categoria(Base, TimestampedModel):
    """
    Modelo de categoria financeira.
    
    Representa uma categoria para classificação de lançamentos financeiros.
    """
    
    __tablename__ = "categorias"
    
    id_categoria: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    icone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    id_categoria_pai: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categorias.id_categoria", ondelete="SET NULL"),
        nullable=True
    )
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ordem: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="categorias")
    lancamentos = relationship("Lancamento", back_populates="categoria")
    subcategorias = relationship(
        "Categoria",
        backref=relationship.backref("categoria_pai", remote_side=[id_categoria]),
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Representação em string da categoria."""
        return f"<Categoria(id={self.id_categoria}, nome='{self.nome}', nivel={self.nivel})>" 