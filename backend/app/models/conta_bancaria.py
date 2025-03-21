"""Modelo de Conta Bancária para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class ContaBancaria(Base, TimestampedModel):
    """
    Modelo de conta bancária.
    
    Representa uma conta bancária no sistema CCONTROL-M.
    """
    
    __tablename__ = "contas_bancarias"
    
    id_conta: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    banco: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    agencia: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    numero: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    saldo_inicial: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    saldo_atual: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    mostrar_dashboard: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="contas_bancarias")
    lancamentos = relationship("Lancamento", back_populates="conta_bancaria")
    
    def __repr__(self) -> str:
        """Representação em string da conta bancária."""
        return f"<ContaBancaria(id={self.id_conta}, nome='{self.nome}', saldo_atual={self.saldo_atual})>" 