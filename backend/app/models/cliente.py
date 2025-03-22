"""Modelo para clientes no sistema CCONTROL-M."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Cliente(Base):
    """Modelo para clientes."""
    __tablename__ = "clientes"
    
    id_cliente = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=True)  # CPF ou CNPJ
    telefone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="clientes")
    
    def __repr__(self) -> str:
        """Representação em string do cliente."""
        return f"<Cliente(id={self.id_cliente}, nome='{self.nome}')>" 