"""Modelo de Compra para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Compra(Base, TimestampedModel):
    """
    Modelo de compra no sistema.
    
    Representa uma operação de compra de produtos ou serviços no sistema CCONTROL-M.
    Inclui informações como fornecedor, valor, data, status e itens.
    """
    
    __tablename__ = "compras"
    
    id_compra: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    id_fornecedor: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("fornecedores.id_fornecedor", ondelete="SET NULL"),
        nullable=True
    )
    numero_compra: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    data_compra: Mapped[date] = mapped_column(Date, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    itens_compra: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pendente", "concluida", "cancelada", name="status_compra"),
        default="pendente",
        nullable=False
    )
    observacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="compras")
    fornecedor = relationship("Fornecedor", back_populates="compras")
    
    def __repr__(self) -> str:
        """Representação em string da compra."""
        return f"<Compra(id={self.id_compra}, descricao='{self.descricao}', valor_total={self.valor_total}, status='{self.status}')>"


class ItemCompra(Base, TimestampedModel):
    """
    Modelo de item de compra.
    
    Representa um item individual em uma compra, com seu produto, quantidade e valores.
    """
    
    __tablename__ = "itens_compra"
    
    id_item_compra: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_compra: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("compras.id_compra", ondelete="CASCADE")
    )
    id_produto: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("produtos.id_produto", ondelete="SET NULL"),
        nullable=True
    )
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relacionamentos
    compra = relationship("Compra", backref="itens")
    produto = relationship("Produto")
    
    def __repr__(self) -> str:
        """Representação em string do item de compra."""
        return f"<ItemCompra(id={self.id_item_compra}, produto='{self.descricao}', quantidade={self.quantidade}, valor_total={self.valor_total})>" 