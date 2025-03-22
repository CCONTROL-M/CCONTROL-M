from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.base_class import Base


class AuditLog(Base):
    """
    Modelo para o registro de auditoria no sistema.
    Armazena ações críticas e erros para fins de segurança e compliance.
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    
    # Informações do usuário
    user_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), 
                     nullable=True, index=True)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="SET NULL"), 
                       nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Informações da ação
    action = Column(String(50), index=True, nullable=False)  # create, update, delete, etc.
    resource_type = Column(String(50), index=True, nullable=False)  # usuario, cliente, etc.
    resource_id = Column(String(255), index=True, nullable=True)
    
    # Informações da requisição
    request_method = Column(String(10), nullable=True)  # GET, POST, etc.
    request_path = Column(String(255), nullable=True)
    request_body = Column(Text, nullable=True)  # JSON como texto
    
    # Detalhes adicionais
    details = Column(Text, nullable=True)  # JSON como texto
    
    # Informações de status
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    is_error = Column(Boolean, default=False)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="audit_logs")
    empresa = relationship("Empresa", back_populates="audit_logs") 