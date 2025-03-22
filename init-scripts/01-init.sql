-- Script de inicialização do banco de dados para CCONTROL-M em produção
-- Este script cria a base de dados e configurações necessárias

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "plpgsql";

-- Criar funções para controle multi-tenant
CREATE OR REPLACE FUNCTION set_current_tenant_id()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.empresa_id = current_setting('app.current_tenant', FALSE);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.empresa_id = OLD.empresa_id;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Criar função para gerar números sequenciais por empresa
CREATE OR REPLACE FUNCTION gerar_sequencial_por_empresa(tabela text, coluna text, empresa_id uuid)
RETURNS integer AS $$
DECLARE
    ultimo_valor integer;
BEGIN
    EXECUTE format('SELECT COALESCE(MAX(%I), 0) FROM %I WHERE empresa_id = %L', coluna, tabela, empresa_id) INTO ultimo_valor;
    RETURN ultimo_valor + 1;
END;
$$ LANGUAGE plpgsql;

-- Função para auditoria
CREATE OR REPLACE FUNCTION audit_log()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data jsonb;
    v_new_data jsonb;
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        v_old_data = to_jsonb(OLD);
        v_new_data = to_jsonb(NEW);
        INSERT INTO logs(
            tabela, operacao, usuario_id, empresa_id, dados_antigos, dados_novos, registro_id
        ) VALUES (
            TG_TABLE_NAME::TEXT,
            TG_OP,
            current_setting('app.current_user_id', FALSE)::uuid,
            NEW.empresa_id,
            v_old_data,
            v_new_data,
            NEW.id
        );
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        v_old_data = to_jsonb(OLD);
        INSERT INTO logs(
            tabela, operacao, usuario_id, empresa_id, dados_antigos, dados_novos, registro_id
        ) VALUES (
            TG_TABLE_NAME::TEXT,
            TG_OP,
            current_setting('app.current_user_id', FALSE)::uuid,
            OLD.empresa_id,
            v_old_data,
            NULL,
            OLD.id
        );
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        v_new_data = to_jsonb(NEW);
        INSERT INTO logs(
            tabela, operacao, usuario_id, empresa_id, dados_antigos, dados_novos, registro_id
        ) VALUES (
            TG_TABLE_NAME::TEXT,
            TG_OP,
            current_setting('app.current_user_id', FALSE)::uuid,
            NEW.empresa_id,
            NULL,
            v_new_data,
            NEW.id
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Configurações de Conexão e Performance
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET effective_cache_size = '3GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET random_page_cost = '1.1';
ALTER SYSTEM SET effective_io_concurrency = '200';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '100';
ALTER SYSTEM SET autovacuum = 'on';
ALTER SYSTEM SET log_min_duration_statement = '1000';
ALTER SYSTEM SET idle_in_transaction_session_timeout = '10min';

-- Criar usuário de aplicação com permissões restritas
CREATE ROLE app_ccontrol WITH LOGIN PASSWORD 'senha_segura_aqui';
ALTER ROLE app_ccontrol SET search_path TO public;
GRANT CONNECT ON DATABASE ccontrolm_prod TO app_ccontrol;
GRANT USAGE ON SCHEMA public TO app_ccontrol;

-- Criar índices para melhorar performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lancamentos_empresa_data ON lancamentos(empresa_id, data_lancamento);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clientes_empresa_nome ON clientes(empresa_id, nome);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fornecedores_empresa_nome ON fornecedores(empresa_id, nome);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vendas_empresa_data ON vendas(empresa_id, data_venda);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categoria_empresa ON categorias(empresa_id, nome);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuarios_empresa ON usuarios(empresa_id, email);

-- Criar política de backup
COMMENT ON DATABASE ccontrolm_prod IS 'Backup diário às 02:00, retenção de 30 dias';

-- Notificar conclusão
DO $$
BEGIN
    RAISE NOTICE 'Inicialização do banco de dados CCONTROL-M concluída com sucesso!';
END $$; 