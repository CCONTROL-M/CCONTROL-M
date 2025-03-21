"""Modelo de Log do Sistema para o sistema CCONTROL-M."""
import uuid
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class LogSistema(Base, TimestampedModel):
    """
    Modelo de log do sistema.
    
    Registra eventos e ações importantes no sistema CCONTROL-M.
    """
    
    __tablename__ = "logs_sistema"
    
    id_log: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    acao: Mapped[str] = mapped_column(String, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    dados: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        """Representação em string do log."""
        return f"<LogSistema(id={self.id_log}, acao='{self.acao}')>" 