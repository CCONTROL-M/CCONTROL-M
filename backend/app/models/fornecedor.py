"""Modelo para fornecedores no sistema CCONTROL-M."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Fornecedor(Base):
    """Modelo para fornecedores."""
    __tablename__ = "fornecedores"
    
    id_fornecedor = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=True)  # CNPJ
    telefone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    observacoes = Column(String, nullable=True)
    avaliacao = Column(Integer, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="fornecedores")
    
    def __repr__(self) -> str:
        """Representação em string do fornecedor."""
        return f"<Fornecedor(id={self.id_fornecedor}, nome='{self.nome}')>" 