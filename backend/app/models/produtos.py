from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db.base_class import Base


class Produto(Base):
    """Modelo para produtos no sistema"""
    __tablename__ = "produtos"
    
    id_produto = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    id_empresa = Column(PostgresUUID(as_uuid=True), ForeignKey("empresas.id_empresa"), nullable=False, index=True)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False, index=True)
    descricao = Column(String, nullable=True)
    preco_venda = Column(Numeric(10, 2), nullable=False)
    preco_custo = Column(Numeric(10, 2), nullable=False)
    estoque_atual = Column(Numeric(10, 2), nullable=False, default=0)
    estoque_minimo = Column(Numeric(10, 2), nullable=False, default=0)
    categoria = Column(String, nullable=True, index=True)
    ativo = Column(Boolean, nullable=False, default=True)
    
    # Relacionamento com empresa
    empresa = relationship("Empresa", back_populates="produtos")
    
    __table_args__ = (
        UniqueConstraint('id_empresa', 'codigo', name='uq_produto_codigo_empresa'),
    )
    
    def __repr__(self):
        return f"<Produto {self.nome} - {self.codigo}>" 