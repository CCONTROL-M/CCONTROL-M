"""Modelo para contas a pagar."""
from uuid import uuid4
from sqlalchemy import Column, String, Numeric, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from app.schemas.conta_pagar import StatusContaPagar


class ContaPagar(Base):
    """Modelo para contas a pagar."""
    
    __tablename__ = "contas_pagar"
    
    id_conta = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    descricao = Column(String(100), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    status = Column(
        Enum(StatusContaPagar),
        nullable=False,
        default=StatusContaPagar.PENDENTE
    )
    observacao = Column(String(500), nullable=True)
    fornecedor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fornecedores.id_fornecedor", ondelete="SET NULL"),
        nullable=True
    )
    categoria_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categorias.id_categoria", ondelete="SET NULL"),
        nullable=True
    )
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id_empresa", ondelete="CASCADE"),
        nullable=False
    ) 