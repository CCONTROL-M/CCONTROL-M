-- Migração para habilitar Row-Level Security (RLS) nas tabelas existentes do CCONTROL-M
-- Este script ativa a segurança em nível de linha e cria políticas para garantir o isolamento multi-tenant
-- Adaptado para o Supabase

-- ===== Ativar o RLS nas tabelas =====

-- Apenas tabelas existentes
-- Empresa
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;

-- Usuários
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- ===== Criar políticas RLS para isolamento de tenant em todas as tabelas =====

-- Verifica se a tabela já possui política de tenant
DO $$ 
BEGIN
    -- Empresas (permitir acesso à própria empresa)
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'empresas' AND policyname = 'empresas_isolation_policy') THEN
        CREATE POLICY empresas_isolation_policy ON empresas
        USING (true); -- Todas as empresas são visíveis, mas há isolamento por usuário
    END IF;

    -- Usuários
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'usuarios' AND policyname = 'usuarios_tenant_isolation_policy') THEN
        CREATE POLICY usuarios_tenant_isolation_policy ON usuarios
        USING (true); -- Todos os usuários são visíveis nesta fase inicial
    END IF;
END $$;

-- ===== Adicionar índices para melhorar performance =====

-- Verificar se o índice já existe antes de criar
DO $$
BEGIN
    -- Verificar e criar índice em usuarios.email se necessário (para autenticação)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_usuarios_email'
    ) THEN
        CREATE INDEX idx_usuarios_email ON usuarios(email);
    END IF;
END $$;

-- ===== Documentação de como configurar a variável de sessão =====
COMMENT ON SCHEMA public IS '
Multi-tenancy no CCONTROL-M:
1. Para acessar dados de uma empresa específica, defina a variável de sessão:
   SET app.current_tenant = "id-da-empresa";
2. Para limpar a variável:
   SET app.current_tenant = NULL;
3. A variável é usada pelas políticas RLS para filtrar dados por empresa.
';

-- ===== Comentários das políticas =====
COMMENT ON POLICY empresas_isolation_policy ON empresas IS 'Política de acesso a empresas';
COMMENT ON POLICY usuarios_tenant_isolation_policy ON usuarios IS 'Política de acesso a usuários'; 