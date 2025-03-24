"""
Modelo para registros de auditoria do sistema
"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Auditoria(Base):
    """
    Modelo para registros de auditoria do sistema.
    Armazena informações sobre ações realizadas pelos usuários.
    """
    __tablename__ = "auditoria"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False, comment="Tipo de entidade auditada")
    entity_id = Column(String, nullable=False, comment="ID da entidade auditada")
    action_type = Column(String, nullable=False, comment="Tipo de ação (create, update, delete)")
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False, comment="ID do usuário que realizou a ação")
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id_empresa"), nullable=False, comment="ID da empresa")
    timestamp = Column(DateTime, default=func.now(), nullable=False, comment="Data e hora da ação")
    data_before = Column(JSON, nullable=True, comment="Dados antes da alteração")
    data_after = Column(JSON, nullable=True, comment="Dados após da alteração")
    details = Column(String, nullable=True, comment="Detalhes adicionais da ação")
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="auditoria_logs")
    empresa = relationship("Empresa", back_populates="auditoria_logs")
    
    def __repr__(self):
        return f"<Auditoria(id={self.id}, entity={self.entity_type}, action={self.action_type})>" 