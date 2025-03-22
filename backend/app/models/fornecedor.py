"""Modelo de Fornecedor para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Fornecedor(Base, TimestampedModel):
    """
    Modelo de fornecedor no sistema.
    
    Representa um fornecedor de produtos ou serviços para uma empresa no sistema CCONTROL-M.
    """
    
    __tablename__ = "fornecedores"
    
    id_fornecedor: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    cnpj: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    endereco: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avaliacao: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="fornecedores")
    
    def __repr__(self) -> str:
        """Representação em string do fornecedor."""
        return f"<Fornecedor(id={self.id_fornecedor}, nome='{self.nome}', cnpj='{self.cnpj}')>" 