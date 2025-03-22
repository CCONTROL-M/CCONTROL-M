"""Modelo para centros de custo no sistema CCONTROL-M."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CentroCusto(Base):
    """Modelo para centros de custo."""
    __tablename__ = "centro_custos"
    
    id_centro = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="centro_custos")
    
    def __repr__(self) -> str:
        """Representação em string do centro de custo."""
        return f"<CentroCusto(id={self.id_centro}, nome='{self.nome}')>" 