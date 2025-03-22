"""Modelo de Permissões de Usuário para o sistema CCONTROL-M."""
import uuid
from typing import List
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime, ARRAY, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base
from app.models.base_model import TimestampedModel


class PermissaoUsuario(Base, TimestampedModel):
    """
    Modelo para controle de permissões por usuário no sistema.
    
    Armazena as permissões de acesso de um usuário a recursos específicos,
    como 'clientes', 'vendas', 'financeiro', etc., e as ações permitidas em cada recurso.
    """
    
    __tablename__ = "permissoes_usuario"
    
    id_permissao: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    id_usuario: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    recurso: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        comment="Nome do recurso ou tela: 'clientes', 'vendas', 'financeiro', etc."
    )
    acoes: Mapped[List[str]] = mapped_column(
        ARRAY(String), 
        nullable=False, 
        comment="Lista de ações permitidas: 'criar', 'editar', 'listar', 'deletar', etc."
    )
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="permissoes")
    
    def __repr__(self) -> str:
        """Representação em string da permissão de usuário."""
        return f"<PermissaoUsuario(id={self.id_permissao}, usuario_id={self.id_usuario}, recurso='{self.recurso}')>" 