"""Modelo para categorias no sistema CCONTROL-M."""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, UUID, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Categoria(Base):
    """Modelo para categorias financeiras."""
    __tablename__ = "categorias"
    
    id_categoria = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("empresas.id_empresa", ondelete="CASCADE"), nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # RECEITA, DESPESA, INVESTIMENTO, etc.
    descricao = Column(String, nullable=True)
    cor = Column(String, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    subcategorias = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="categorias")
    
    def __repr__(self) -> str:
        """Representação em string da categoria."""
        return f"<Categoria(id={self.id_categoria}, nome='{self.nome}', tipo='{self.tipo}')>" 