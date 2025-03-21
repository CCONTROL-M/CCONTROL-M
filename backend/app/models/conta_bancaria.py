"""Modelo de Conta Bancária para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class ContaBancaria(Base, TimestampedModel):
    """
    Modelo de conta bancária no sistema.
    
    Representa uma conta bancária de uma empresa no sistema CCONTROL-M.
    Inclui detalhes como banco, agência, número, tipo e saldos.
    """
    
    __tablename__ = "contas_bancarias"
    
    id_conta: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    banco: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    agencia: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    numero: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    saldo_inicial: Mapped[float] = mapped_column(Float, default=0.0)
    saldo_atual: Mapped[float] = mapped_column(Float, default=0.0)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    mostrar_dashboard: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="contas_bancarias")
    lancamentos = relationship("Lancamento", back_populates="conta_bancaria")
    
    def __repr__(self) -> str:
        """Representação em string da conta bancária."""
        return f"<ContaBancaria(id={self.id_conta}, nome='{self.nome}')>" 