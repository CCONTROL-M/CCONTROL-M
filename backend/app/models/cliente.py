"""Modelo de Cliente para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Cliente(Base, TimestampedModel):
    """
    Modelo de cliente.
    
    Representa um cliente no sistema CCONTROL-M.
    """
    
    __tablename__ = "clientes"
    
    id_cliente: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    documento: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="clientes")
    lancamentos = relationship("Lancamento", back_populates="cliente")
    vendas = relationship("Venda", back_populates="cliente")
    
    def __repr__(self) -> str:
        """Representação em string do cliente."""
        return f"<Cliente(id={self.id_cliente}, nome='{self.nome}')>" 