"""Add missing tables and update schema

Revision ID: add_missing_tables_migration
Revises: readicionar_tabela_produtos
Create Date: 2025-03-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSON, ARRAY
import uuid
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'add_missing_tables_migration'
down_revision = 'readicionar_tabela_produtos'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar e criar tabela contas_pagar se não existir
    if not op.get_bind().dialect.has_table(op.get_bind(), 'contas_pagar'):
        op.create_table(
            'contas_pagar',
            sa.Column('id_conta', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('descricao', sa.String(100), nullable=False),
            sa.Column('valor', sa.Numeric(10, 2), nullable=False),
            sa.Column('data_vencimento', sa.Date(), nullable=False),
            sa.Column('data_pagamento', sa.Date(), nullable=True),
            sa.Column('status', sa.Enum('PENDENTE', 'PAGO', 'ATRASADO', 'CANCELADO', name='statuscontapagar'), nullable=False, server_default='PENDENTE'),
            sa.Column('observacao', sa.String(500), nullable=True),
            sa.Column('fornecedor_id', UUID(as_uuid=True), nullable=True),
            sa.Column('categoria_id', UUID(as_uuid=True), nullable=True),
            sa.Column('empresa_id', UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id_fornecedor'], name='fk_conta_pagar_fornecedor', ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id_categoria'], name='fk_conta_pagar_categoria', ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id_empresa'], name='fk_conta_pagar_empresa', ondelete='CASCADE')
        )
        
        # Criar índices para contas_pagar
        op.create_index(op.f('ix_contas_pagar_empresa_id'), 'contas_pagar', ['empresa_id'], unique=False)
        op.create_index(op.f('ix_contas_pagar_fornecedor_id'), 'contas_pagar', ['fornecedor_id'], unique=False)
        op.create_index(op.f('ix_contas_pagar_categoria_id'), 'contas_pagar', ['categoria_id'], unique=False)
        op.create_index(op.f('ix_contas_pagar_data_vencimento'), 'contas_pagar', ['data_vencimento'], unique=False)
        op.create_index(op.f('ix_contas_pagar_status'), 'contas_pagar', ['status'], unique=False)
    
    # Verificar e criar tabela contas_receber se não existir
    if not op.get_bind().dialect.has_table(op.get_bind(), 'contas_receber'):
        op.create_table(
            'contas_receber',
            sa.Column('id_conta_receber', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('id_empresa', UUID(as_uuid=True), nullable=False),
            sa.Column('id_cliente', UUID(as_uuid=True), nullable=True),
            sa.Column('id_lancamento', UUID(as_uuid=True), nullable=True),
            sa.Column('id_venda', UUID(as_uuid=True), nullable=True),
            sa.Column('descricao', sa.String(255), nullable=False),
            sa.Column('valor', sa.Numeric(15, 2), nullable=False),
            sa.Column('data_emissao', sa.Date(), nullable=False),
            sa.Column('data_vencimento', sa.Date(), nullable=False),
            sa.Column('data_recebimento', sa.Date(), nullable=True),
            sa.Column('observacoes', sa.Text(), nullable=True),
            sa.Column('status', sa.Enum('pendente', 'recebido', 'atrasado', 'cancelado', name='statuscontareceber'), nullable=False, server_default='pendente'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id_empresa'], name='fk_conta_receber_empresa', ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['id_cliente'], ['clientes.id_cliente'], name='fk_conta_receber_cliente', ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['id_lancamento'], ['lancamentos.id_lancamento'], name='fk_conta_receber_lancamento', ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['id_venda'], ['vendas.id_venda'], name='fk_conta_receber_venda', ondelete='SET NULL')
        )
        
        # Criar índices para contas_receber
        op.create_index(op.f('ix_contas_receber_id_empresa'), 'contas_receber', ['id_empresa'], unique=False)
        op.create_index(op.f('ix_contas_receber_id_cliente'), 'contas_receber', ['id_cliente'], unique=False)
        op.create_index(op.f('ix_contas_receber_id_venda'), 'contas_receber', ['id_venda'], unique=False)
        op.create_index(op.f('ix_contas_receber_data_vencimento'), 'contas_receber', ['data_vencimento'], unique=False)
        op.create_index(op.f('ix_contas_receber_status'), 'contas_receber', ['status'], unique=False)
    
    # Verificar e criar tabela permissoes se não existir
    if not op.get_bind().dialect.has_table(op.get_bind(), 'permissoes'):
        op.create_table(
            'permissoes',
            sa.Column('id_permissao', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('id_usuario', UUID(as_uuid=True), nullable=False),
            sa.Column('id_empresa', UUID(as_uuid=True), nullable=False),
            sa.Column('recurso', sa.String(100), nullable=False),
            sa.Column('acoes', JSON, nullable=False),
            sa.Column('descricao', sa.String(255), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='fk_permissao_usuario', ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['id_empresa'], ['empresas.id_empresa'], name='fk_permissao_empresa', ondelete='CASCADE')
        )
        
        # Criar índices para permissoes
        op.create_index(op.f('ix_permissoes_id_usuario'), 'permissoes', ['id_usuario'], unique=False)
        op.create_index(op.f('ix_permissoes_id_empresa'), 'permissoes', ['id_empresa'], unique=False)
        op.create_index(op.f('ix_permissoes_recurso'), 'permissoes', ['recurso'], unique=False)
    
    # Verificar e criar tabela permissoes_usuario se não existir
    if not op.get_bind().dialect.has_table(op.get_bind(), 'permissoes_usuario'):
        op.create_table(
            'permissoes_usuario',
            sa.Column('id_permissao', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
            sa.Column('id_usuario', UUID(as_uuid=True), nullable=False),
            sa.Column('recurso', sa.String(100), nullable=False),
            sa.Column('acoes', ARRAY(sa.String), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()'), nullable=False),
            sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='fk_permissao_usuario_usuario', ondelete='CASCADE')
        )
        
        # Criar índices para permissoes_usuario
        op.create_index(op.f('ix_permissoes_usuario_id_usuario'), 'permissoes_usuario', ['id_usuario'], unique=False)
        op.create_index(op.f('ix_permissoes_usuario_recurso'), 'permissoes_usuario', ['recurso'], unique=False)


def downgrade() -> None:
    # Remover tabelas na ordem inversa
    op.drop_table('permissoes_usuario')
    op.drop_table('permissoes')
    op.drop_table('contas_receber')
    op.drop_table('contas_pagar') 