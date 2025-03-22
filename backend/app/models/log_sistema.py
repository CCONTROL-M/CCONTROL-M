"""Modelo para logs do sistema."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, ForeignKey, DateTime, UUID, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class LogSistema(Base):
    """Modelo para logs do sistema."""
    __tablename__ = "logs_sistema"
    
    id_log = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=True)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("empresas.id_empresa"), nullable=True)
    acao = Column(String, nullable=False)
    descricao = Column(String, nullable=True, default='')
    dados = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="logs")
    usuario = relationship("Usuario", back_populates="logs")

    def __repr__(self) -> str:
        """Representação em string do log."""
        return f"<LogSistema(id={self.id_log}, acao='{self.acao}', usuario_id={self.id_usuario})>" 