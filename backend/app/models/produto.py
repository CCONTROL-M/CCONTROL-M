"""Modelo de Produto para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Float, Text, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Produto(Base, TimestampedModel):
    """
    Modelo de produto.
    
    Representa um produto no sistema CCONTROL-M.
    """
    
    __tablename__ = "produtos"
    
    id_produto: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    id_categoria: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categorias.id_categoria", ondelete="SET NULL"),
        nullable=True
    )
    
    nome: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    codigo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    codigo_barras: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    valor_compra: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    valor_venda: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estoque_atual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estoque_minimo: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    imagens: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="produtos")
    categoria = relationship("Categoria")
    
    def __repr__(self) -> str:
        """Representação em string do produto."""
        return f"<Produto(id={self.id_produto}, nome='{self.nome}', valor_venda={self.valor_venda})>" 