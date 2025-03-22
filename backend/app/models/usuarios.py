from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base_class import Base


# Tabela de associação entre Usuário e Perfil
usuario_perfil = Table(
    "usuario_perfil",
    Base.metadata,
    Column("usuario_id", UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("perfil_id", UUID(as_uuid=True), ForeignKey("perfis.id", ondelete="CASCADE"), primary_key=True)
)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=False)
    senha_hash = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    superuser = Column(Boolean, default=False)

    # Relacionamento muitos-para-muitos com Perfil
    perfis = relationship("Perfil", secondary=usuario_perfil, back_populates="usuarios")
    
    # Relacionamento com Empresa
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True)
    empresa = relationship("Empresa", back_populates="usuarios")
    
    # Logs de auditoria
    audit_logs = relationship("AuditLog", back_populates="usuario")
    

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    cnpj = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    
    # Logo da empresa
    logo_url = Column(String, nullable=True)
    
    # Configurações específicas da empresa em formato JSON
    configuracoes = Column(Text, nullable=True)
    
    # Relacionamento com usuários
    usuarios = relationship("Usuario", back_populates="empresa")
    
    # Logs de auditoria
    audit_logs = relationship("AuditLog", back_populates="empresa")
    

class Perfil(Base):
    __tablename__ = "perfis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    
    # Permissões do perfil em formato JSON
    permissoes = Column(Text, nullable=True)
    
    # Relacionamento muitos-para-muitos com Usuário
    usuarios = relationship("Usuario", secondary=usuario_perfil, back_populates="perfis") 