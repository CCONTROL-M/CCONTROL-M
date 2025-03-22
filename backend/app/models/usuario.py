"""Modelo de Usuário para o sistema CCONTROL-M."""
import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Usuario(Base, TimestampedModel):
    """
    Modelo de usuário do sistema.
    
    Representa um usuário que pode acessar o sistema CCONTROL-M.
    """
    
    __tablename__ = "usuarios"
    
    id_usuario: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_usuario: Mapped[str] = mapped_column(String, nullable=False)
    telas_permitidas: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="usuarios")
    logs = relationship("LogSistema", back_populates="usuario")
    
    def __repr__(self) -> str:
        """Representação em string do usuário."""
        return f"<Usuario(id={self.id_usuario}, nome='{self.nome}', email='{self.email}')>" 