"""Modelo para permissões no sistema."""
from uuid import UUID, uuid4
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Permissao(Base):
    """Modelo para permissões de usuários."""
    __tablename__ = "permissoes"

    id_permissao = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    id_usuario = Column(PgUUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False)
    id_empresa = Column(PgUUID(as_uuid=True), ForeignKey("empresas.id_empresa"), nullable=False)
    recurso = Column(String, nullable=False)
    acoes = Column(JSON, nullable=False)
    descricao = Column(String, nullable=True)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="permissoes")
    empresa = relationship("Empresa", back_populates="permissoes") 