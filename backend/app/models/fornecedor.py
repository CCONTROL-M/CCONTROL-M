"""Modelo de Fornecedor para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Fornecedor(Base, TimestampedModel):
    """
    Modelo de fornecedor.
    
    Representa um fornecedor no sistema CCONTROL-M.
    """
    
    __tablename__ = "fornecedores"
    
    id_fornecedor: Mapped[uuid.UUID] = mapped_column(
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
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="fornecedores")
    lancamentos = relationship("Lancamento", back_populates="fornecedor")
    
    def __repr__(self) -> str:
        """Representação em string do fornecedor."""
        return f"<Fornecedor(id={self.id_fornecedor}, nome='{self.nome}')>" 