-- Migração para habilitar Row-Level Security (RLS) em todas as tabelas relevantes do CCONTROL-M
-- Este script ativa a segurança em nível de linha e cria políticas para garantir o isolamento multi-tenant
-- Adaptado para o Supabase

-- ===== Ativar o RLS nas tabelas =====

-- Usuários
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Clientes
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;

-- Produtos
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;

-- Vendas
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;

-- Categorias
ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;

-- Lançamentos
ALTER TABLE lancamentos ENABLE ROW LEVEL SECURITY;

-- Parcelas
ALTER TABLE parcelas ENABLE ROW LEVEL SECURITY;

-- Formas de Pagamento
ALTER TABLE formas_pagamento ENABLE ROW LEVEL SECURITY;

-- Contas Bancárias
ALTER TABLE contas_bancarias ENABLE ROW LEVEL SECURITY;

-- Fornecedores
ALTER TABLE fornecedores ENABLE ROW LEVEL SECURITY;

-- Centro de Custos
ALTER TABLE centro_custos ENABLE ROW LEVEL SECURITY;

-- Logs do Sistema
ALTER TABLE logs_sistema ENABLE ROW LEVEL SECURITY;

-- ===== Criar políticas RLS para isolamento de tenant em todas as tabelas =====

-- Verifica se a tabela já possui política de tenant
DO $$ 
BEGIN
    -- Usuários
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'usuarios' AND policyname = 'usuarios_tenant_isolation_policy') THEN
        CREATE POLICY usuarios_tenant_isolation_policy ON usuarios
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Clientes
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'clientes' AND policyname = 'clientes_tenant_isolation_policy') THEN
        CREATE POLICY clientes_tenant_isolation_policy ON clientes
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Produtos
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'produtos' AND policyname = 'produtos_tenant_isolation_policy') THEN
        CREATE POLICY produtos_tenant_isolation_policy ON produtos
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Vendas
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'vendas' AND policyname = 'vendas_tenant_isolation_policy') THEN
        CREATE POLICY vendas_tenant_isolation_policy ON vendas
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Lançamentos
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'lancamentos' AND policyname = 'lancamentos_tenant_isolation_policy') THEN
        CREATE POLICY lancamentos_tenant_isolation_policy ON lancamentos
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Parcelas
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'parcelas' AND policyname = 'parcelas_tenant_isolation_policy') THEN
        CREATE POLICY parcelas_tenant_isolation_policy ON parcelas
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Categorias
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'categorias' AND policyname = 'categorias_tenant_isolation_policy') THEN
        CREATE POLICY categorias_tenant_isolation_policy ON categorias
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Centro de Custos
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'centro_custos' AND policyname = 'centro_custos_tenant_isolation_policy') THEN
        CREATE POLICY centro_custos_tenant_isolation_policy ON centro_custos
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Fornecedores
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'fornecedores' AND policyname = 'fornecedores_tenant_isolation_policy') THEN
        CREATE POLICY fornecedores_tenant_isolation_policy ON fornecedores
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Formas de Pagamento
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'formas_pagamento' AND policyname = 'formas_pagamento_tenant_isolation_policy') THEN
        CREATE POLICY formas_pagamento_tenant_isolation_policy ON formas_pagamento
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Contas Bancárias
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'contas_bancarias' AND policyname = 'contas_bancarias_tenant_isolation_policy') THEN
        CREATE POLICY contas_bancarias_tenant_isolation_policy ON contas_bancarias
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Logs do Sistema (opcional, dependendo se você quer isolar logs por empresa)
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'logs_sistema' AND policyname = 'logs_sistema_tenant_isolation_policy') THEN
        CREATE POLICY logs_sistema_tenant_isolation_policy ON logs_sistema
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;
END $$;

-- ===== Adicionar índices para melhorar performance em consultas com filtro de tenant =====

-- Verificar se o índice já existe antes de criar
DO $$
BEGIN
    -- Verificar e criar índice em usuarios.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_usuarios_id_empresa'
    ) THEN
        CREATE INDEX idx_usuarios_id_empresa ON usuarios(id_empresa);
    END IF;

    -- Verificar e criar índice em clientes.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_clientes_id_empresa'
    ) THEN
        CREATE INDEX idx_clientes_id_empresa ON clientes(id_empresa);
    END IF;

    -- Verificar e criar índice em produtos.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_produtos_id_empresa'
    ) THEN
        CREATE INDEX idx_produtos_id_empresa ON produtos(id_empresa);
    END IF;

    -- Verificar e criar índice em vendas.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_vendas_id_empresa'
    ) THEN
        CREATE INDEX idx_vendas_id_empresa ON vendas(id_empresa);
    END IF;

    -- Verificar e criar índice em lancamentos.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_lancamentos_id_empresa'
    ) THEN
        CREATE INDEX idx_lancamentos_id_empresa ON lancamentos(id_empresa);
    END IF;

    -- Verificar e criar índice em parcelas.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_parcelas_id_empresa'
    ) THEN
        CREATE INDEX idx_parcelas_id_empresa ON parcelas(id_empresa);
    END IF;
END $$;

-- ===== Documentação de como configurar a variável de sessão =====
COMMENT ON SCHEMA public IS '
Multi-tenancy no CCONTROL-M:
1. Para acessar dados de uma empresa específica, defina a variável de sessão:
   SET app.current_tenant = "id-da-empresa-uuid";
2. Para limpar a variável:
   SET app.current_tenant = NULL;
3. A variável é usada pelas políticas RLS para filtrar dados por empresa.
';

-- ===== Comentários das políticas =====
COMMENT ON POLICY usuarios_tenant_isolation_policy ON usuarios IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY clientes_tenant_isolation_policy ON clientes IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY produtos_tenant_isolation_policy ON produtos IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY vendas_tenant_isolation_policy ON vendas IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY lancamentos_tenant_isolation_policy ON lancamentos IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY parcelas_tenant_isolation_policy ON parcelas IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant'; 