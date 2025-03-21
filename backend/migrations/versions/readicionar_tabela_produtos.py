"""Readicionar tabela produtos

Revision ID: readicionar_tabela_produtos
Revises: a9984c6a1b6f
Create Date: 2025-03-21 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'readicionar_tabela_produtos'
down_revision = 'a9984c6a1b6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Recreate produtos table ###
    op.create_table(
        'produtos',
        sa.Column('id_produto', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('id_empresa', UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('codigo', sa.String(length=30), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('preco_venda', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('preco_custo', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('estoque_atual', sa.Numeric(precision=10, scale=2), nullable=False, server_default=text("0")),
        sa.Column('estoque_minimo', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('categoria', sa.String(length=50), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=text("true")),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id_empresa'], name='fk_produto_empresa', ondelete='CASCADE'),
        sa.UniqueConstraint('id_empresa', 'codigo', name='uq_produto_empresa_codigo')
    )
    
    # Adicionar índices
    op.create_index(op.f('ix_produtos_id_empresa'), 'produtos', ['id_empresa'], unique=False)
    op.create_index(op.f('ix_produtos_codigo'), 'produtos', ['codigo'], unique=False)
    op.create_index(op.f('ix_produtos_categoria'), 'produtos', ['categoria'], unique=False)


def downgrade() -> None:
    # ### Drop produtos table ###
    op.drop_index(op.f('ix_produtos_categoria'), table_name='produtos')
    op.drop_index(op.f('ix_produtos_codigo'), table_name='produtos')
    op.drop_index(op.f('ix_produtos_id_empresa'), table_name='produtos')
    op.drop_table('produtos') 