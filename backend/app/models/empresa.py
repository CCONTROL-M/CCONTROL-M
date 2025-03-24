"""Modelo de Empresa para o sistema CCONTROL-M."""
import uuid
from typing import Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base_model import TimestampedModel


class Empresa(Base, TimestampedModel):
    """
    Modelo de empresa no sistema.
    
    Representa uma empresa cliente do sistema CCONTROL-M.
    """
    
    __tablename__ = "empresas"
    
    id_empresa: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    razao_social: Mapped[str] = mapped_column(String, nullable=False)
    nome_fantasia: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cnpj: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    endereco: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cidade: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    usuarios: Mapped[List["Usuario"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    logs: Mapped[List["LogSistema"]] = relationship(
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    clientes: Mapped[List["Cliente"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    produtos: Mapped[List["Produto"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    fornecedores: Mapped[List["Fornecedor"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    categorias: Mapped[List["Categoria"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    centro_custos: Mapped[List["CentroCusto"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    contas_bancarias: Mapped[List["ContaBancaria"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    formas_pagamento: Mapped[List["FormaPagamento"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    lancamentos: Mapped[List["Lancamento"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    vendas: Mapped[List["Venda"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    compras: Mapped[List["Compra"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    auditoria_logs: Mapped[List["Auditoria"]] = relationship(
        back_populates="empresa", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """Representação em string da empresa."""
        return f"<Empresa(id={self.id_empresa}, razao_social='{self.razao_social}', cnpj='{self.cnpj}')>" 