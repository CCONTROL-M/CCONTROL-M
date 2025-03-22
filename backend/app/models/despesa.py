"""Modelo de Despesa para o sistema CCONTROL-M."""
import uuid
from typing import Optional
from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Despesa(Base, TimestampedModel):
    """
    Modelo de despesa no sistema.
    
    Representa uma despesa operacional ou administrativa no sistema CCONTROL-M.
    Inclui informações como valor, data, tipo, categoria e centro de custo.
    """
    
    __tablename__ = "despesas"
    
    id_despesa: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("empresas.id_empresa", ondelete="CASCADE")
    )
    id_centro_custo: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("centros_custo.id_centro_custo", ondelete="SET NULL"),
        nullable=True
    )
    id_categoria: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categorias.id_categoria", ondelete="SET NULL"),
        nullable=True
    )
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    data_despesa: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[str] = mapped_column(
        Enum("fixa", "variavel", "investimento", name="tipo_despesa"),
        default="variavel",
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("pendente", "paga", "cancelada", name="status_despesa"),
        default="pendente",
        nullable=False
    )
    observacao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="despesas")
    centro_custo = relationship("CentroCusto", back_populates="despesas")
    categoria = relationship("Categoria", back_populates="despesas")
    lancamento = relationship("Lancamento", back_populates="despesa")
    
    def __repr__(self) -> str:
        """Representação em string da despesa."""
        return f"<Despesa(id={self.id_despesa}, descricao='{self.descricao}', valor={self.valor}, status='{self.status}')>" 