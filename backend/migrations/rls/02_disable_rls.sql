-- Migração para desativar Row-Level Security (RLS) nas tabelas do CCONTROL-M
-- Este script remove as políticas e desativa o RLS
-- Adaptado para o Supabase

-- ===== Remover políticas RLS =====

-- Políticas de tenant isolation
DROP POLICY IF EXISTS vendas_tenant_isolation_policy ON vendas;
DROP POLICY IF EXISTS lancamentos_tenant_isolation_policy ON lancamentos;
DROP POLICY IF EXISTS parcelas_tenant_isolation_policy ON parcelas;
DROP POLICY IF EXISTS produtos_tenant_isolation_policy ON produtos;
DROP POLICY IF EXISTS categorias_tenant_isolation_policy ON categorias;
DROP POLICY IF EXISTS centro_custos_tenant_isolation_policy ON centro_custos;

-- ATENÇÃO: Existem outras políticas no Supabase que não devem ser removidas
-- (policies criadas via interface do Supabase)

-- ===== Desativar o RLS nas tabelas =====
-- ATENÇÃO: Isso removerá todas as políticas e permissões RLS!
-- Use apenas em ambiente de desenvolvimento ou com extrema cautela

-- Usuários
ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;

-- Clientes
ALTER TABLE clientes DISABLE ROW LEVEL SECURITY;

-- Produtos
ALTER TABLE produtos DISABLE ROW LEVEL SECURITY;

-- Vendas
ALTER TABLE vendas DISABLE ROW LEVEL SECURITY;

-- Categorias
ALTER TABLE categorias DISABLE ROW LEVEL SECURITY;

-- Lançamentos
ALTER TABLE lancamentos DISABLE ROW LEVEL SECURITY;

-- Parcelas
ALTER TABLE parcelas DISABLE ROW LEVEL SECURITY;

-- Formas de Pagamento
ALTER TABLE formas_pagamento DISABLE ROW LEVEL SECURITY;

-- Contas Bancárias
ALTER TABLE contas_bancarias DISABLE ROW LEVEL SECURITY;

-- Fornecedores
ALTER TABLE fornecedores DISABLE ROW LEVEL SECURITY;

-- Centro de Custos
ALTER TABLE centro_custos DISABLE ROW LEVEL SECURITY;

-- Remover comentário de esquema
COMMENT ON SCHEMA public IS NULL; 