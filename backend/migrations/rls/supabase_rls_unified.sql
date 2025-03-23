-- Script unificado para configuração de Row Level Security (RLS) no Supabase
-- Para o sistema CCONTROL-M
-- Este script ativa a segurança em nível de linha e cria políticas para garantir o isolamento multi-tenant

-- ===== ATIVAR RLS EM TODAS AS TABELAS =====

-- Usuários
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuario ENABLE ROW LEVEL SECURITY;

-- Clientes
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE cliente ENABLE ROW LEVEL SECURITY;

-- Produtos
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE produto ENABLE ROW LEVEL SECURITY;

-- Vendas
ALTER TABLE vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE venda ENABLE ROW LEVEL SECURITY;

-- Categorias
ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE categoria ENABLE ROW LEVEL SECURITY;

-- Lançamentos
ALTER TABLE lancamentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE lancamento ENABLE ROW LEVEL SECURITY;

-- Parcelas
ALTER TABLE parcelas ENABLE ROW LEVEL SECURITY;
ALTER TABLE parcela ENABLE ROW LEVEL SECURITY;

-- Formas de Pagamento
ALTER TABLE formas_pagamento ENABLE ROW LEVEL SECURITY;
ALTER TABLE forma_pagamento ENABLE ROW LEVEL SECURITY;

-- Contas Bancárias
ALTER TABLE contas_bancarias ENABLE ROW LEVEL SECURITY;
ALTER TABLE conta_bancaria ENABLE ROW LEVEL SECURITY;

-- Fornecedores
ALTER TABLE fornecedores ENABLE ROW LEVEL SECURITY;
ALTER TABLE fornecedor ENABLE ROW LEVEL SECURITY;

-- Centro de Custos
ALTER TABLE centro_custos ENABLE ROW LEVEL SECURITY;
ALTER TABLE centro_custo ENABLE ROW LEVEL SECURITY;

-- Logs do Sistema
ALTER TABLE logs_sistema ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_sistema ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_atividade ENABLE ROW LEVEL SECURITY;

-- Empresa
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE empresa ENABLE ROW LEVEL SECURITY;

-- Relacionamentos
ALTER TABLE usuario_empresa ENABLE ROW LEVEL SECURITY;

-- Contas a Pagar
ALTER TABLE contas_pagar ENABLE ROW LEVEL SECURITY;
ALTER TABLE conta_pagar ENABLE ROW LEVEL SECURITY;

-- Contas a Receber
ALTER TABLE contas_receber ENABLE ROW LEVEL SECURITY;
ALTER TABLE conta_receber ENABLE ROW LEVEL SECURITY;

-- Permissões
ALTER TABLE permissoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissao ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissoes_usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissao_usuario ENABLE ROW LEVEL SECURITY;

-- ===== CRIAR POLÍTICAS RLS - ABORDAGEM 1: USANDO app.current_tenant =====
-- Esta abordagem usa a variável de sessão app.current_tenant para filtragem

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

    -- Logs do Sistema
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'logs_sistema' AND policyname = 'logs_sistema_tenant_isolation_policy') THEN
        CREATE POLICY logs_sistema_tenant_isolation_policy ON logs_sistema
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Contas a Pagar
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'contas_pagar' AND policyname = 'contas_pagar_tenant_isolation_policy') THEN
        CREATE POLICY contas_pagar_tenant_isolation_policy ON contas_pagar
        USING (empresa_id = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Contas a Receber
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'contas_receber' AND policyname = 'contas_receber_tenant_isolation_policy') THEN
        CREATE POLICY contas_receber_tenant_isolation_policy ON contas_receber
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Permissões
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'permissoes' AND policyname = 'permissoes_tenant_isolation_policy') THEN
        CREATE POLICY permissoes_tenant_isolation_policy ON permissoes
        USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
    END IF;

    -- Permissões de Usuário
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'permissoes_usuario' AND policyname = 'permissoes_usuario_tenant_isolation_policy') THEN
        CREATE POLICY permissoes_usuario_tenant_isolation_policy ON permissoes_usuario
        USING (
            id_usuario IN (
                SELECT id_usuario FROM usuarios WHERE id_empresa = (current_setting('app.current_tenant', TRUE))::uuid
            )
        );
    END IF;
END $$;

-- ===== CRIAR POLÍTICAS RLS - ABORDAGEM 2: USANDO AUTH.UID =====
-- Esta abordagem usa o auth.uid para relacionar com as empresas do usuário

-- Empresa: Acesso apenas à empresa do usuário
CREATE POLICY "Usuários podem ver suas empresas" ON empresa
    FOR SELECT
    USING (id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Usuario: Ver apenas o próprio perfil ou usuários da mesma empresa (para admins)
CREATE POLICY "Usuários podem ver seu próprio perfil" ON usuario
    FOR SELECT
    USING (id = auth.uid() OR id IN (
        SELECT u.id FROM usuario u
        JOIN usuario_empresa ue1 ON u.id = ue1.usuario_id
        JOIN usuario_empresa ue2 ON ue1.empresa_id = ue2.empresa_id
        WHERE ue2.usuario_id = auth.uid() AND ue2.is_admin = true
    ));

-- Usuario_empresa: Acesso apenas aos vínculos do próprio usuário ou da empresa (para admins)
CREATE POLICY "Acesso ao próprio vínculo" ON usuario_empresa
    FOR SELECT
    USING (usuario_id = auth.uid() OR empresa_id IN (
        SELECT empresa_id FROM usuario_empresa
        WHERE usuario_id = auth.uid() AND is_admin = true
    ));

-- Cliente: Acesso apenas aos clientes das empresas do usuário
CREATE POLICY "Acesso aos clientes da empresa" ON cliente
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Fornecedor: Acesso apenas aos fornecedores das empresas do usuário
CREATE POLICY "Acesso aos fornecedores da empresa" ON fornecedor
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Categoria: Acesso apenas às categorias das empresas do usuário
CREATE POLICY "Acesso às categorias da empresa" ON categoria
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Centro de Custo: Acesso apenas aos centros de custo das empresas do usuário
CREATE POLICY "Acesso aos centros de custo da empresa" ON centro_custo
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Conta Bancária: Acesso apenas às contas das empresas do usuário
CREATE POLICY "Acesso às contas bancárias da empresa" ON conta_bancaria
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Forma de Pagamento: Acesso apenas às formas de pagamento das empresas do usuário
CREATE POLICY "Acesso às formas de pagamento da empresa" ON forma_pagamento
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Lançamento: Acesso apenas aos lançamentos das empresas do usuário
CREATE POLICY "Acesso aos lançamentos da empresa" ON lancamento
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Venda: Acesso apenas às vendas das empresas do usuário
CREATE POLICY "Acesso às vendas da empresa" ON venda
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Parcela: Acesso apenas às parcelas das vendas das empresas do usuário
CREATE POLICY "Acesso às parcelas da empresa" ON parcela
    FOR ALL
    USING (venda_id IN (
        SELECT id FROM venda 
        WHERE empresa_id IN (
            SELECT empresa_id FROM usuario_empresa 
            WHERE usuario_id = auth.uid()
        )
    ));

-- Conta a Pagar: Acesso apenas às contas a pagar das empresas do usuário
CREATE POLICY "Acesso às contas a pagar da empresa" ON conta_pagar
    FOR ALL
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Conta a Receber: Acesso apenas às contas a receber das empresas do usuário
CREATE POLICY "Acesso às contas a receber da empresa" ON conta_receber
    FOR ALL
    USING (id_empresa IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- Permissão: Acesso apenas às permissões do próprio usuário ou da empresa (para admins)
CREATE POLICY "Acesso às permissões do usuário" ON permissao
    FOR ALL
    USING (
        id_usuario = auth.uid() OR 
        (id_empresa IN (
            SELECT empresa_id FROM usuario_empresa 
            WHERE usuario_id = auth.uid() AND is_admin = true
        ))
    );

-- Permissão de Usuário: Acesso apenas às permissões do próprio usuário ou da empresa (para admins)
CREATE POLICY "Acesso às permissões de usuário" ON permissao_usuario
    FOR ALL
    USING (
        id_usuario = auth.uid() OR 
        id_usuario IN (
            SELECT u.id_usuario FROM usuarios u
            JOIN usuario_empresa ue ON u.id_empresa = ue.empresa_id
            WHERE ue.usuario_id = auth.uid() AND ue.is_admin = true
        )
    );

-- Log de Atividade: Acesso apenas aos logs das empresas do usuário (admin)
CREATE POLICY "Acesso aos logs da empresa" ON log_atividade
    FOR SELECT
    USING (empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid() AND is_admin = true
    ));

-- Política para inserção de logs (todos podem inserir logs da sua atividade)
CREATE POLICY "Inserção de logs da própria atividade" ON log_atividade
    FOR INSERT
    WITH CHECK (usuario_id = auth.uid() AND empresa_id IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid()
    ));

-- ===== ADICIONAR ÍNDICES PARA MELHORAR PERFORMANCE =====

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

    -- Verificar e criar índice em usuario.empresa_id se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_usuario_empresa_id'
    ) THEN
        CREATE INDEX idx_usuario_empresa_id ON usuario(empresa_id);
    END IF;

    -- Verificar e criar índice em clientes.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_clientes_id_empresa'
    ) THEN
        CREATE INDEX idx_clientes_id_empresa ON clientes(id_empresa);
    END IF;

    -- Verificar e criar índice em cliente.empresa_id se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_cliente_empresa_id'
    ) THEN
        CREATE INDEX idx_cliente_empresa_id ON cliente(empresa_id);
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
    
    -- Verificar e criar índice em contas_pagar.empresa_id se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_contas_pagar_empresa_id'
    ) THEN
        CREATE INDEX idx_contas_pagar_empresa_id ON contas_pagar(empresa_id);
    END IF;
    
    -- Verificar e criar índice em contas_receber.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_contas_receber_id_empresa'
    ) THEN
        CREATE INDEX idx_contas_receber_id_empresa ON contas_receber(id_empresa);
    END IF;
    
    -- Verificar e criar índice em permissoes.id_empresa se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_permissoes_id_empresa'
    ) THEN
        CREATE INDEX idx_permissoes_id_empresa ON permissoes(id_empresa);
    END IF;
    
    -- Verificar e criar índice em permissoes_usuario.id_usuario se necessário
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_permissoes_usuario_id_usuario'
    ) THEN
        CREATE INDEX idx_permissoes_usuario_id_usuario ON permissoes_usuario(id_usuario);
    END IF;
END $$;

-- ===== DOCUMENTAÇÃO DE COMO CONFIGURAR A VARIÁVEL DE SESSÃO =====
COMMENT ON SCHEMA public IS '
Multi-tenancy no CCONTROL-M:
1. Para acessar dados de uma empresa específica, defina a variável de sessão:
   SET app.current_tenant = "id-da-empresa-uuid";
2. Para limpar a variável:
   SET app.current_tenant = NULL;
3. A variável é usada pelas políticas RLS para filtrar dados por empresa.
4. Alternativa: Use auth.uid() e o relacionamento usuario_empresa.
';

-- ===== COMENTÁRIOS DAS POLÍTICAS =====
COMMENT ON POLICY usuarios_tenant_isolation_policy ON usuarios IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY clientes_tenant_isolation_policy ON clientes IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY produtos_tenant_isolation_policy ON produtos IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY vendas_tenant_isolation_policy ON vendas IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY lancamentos_tenant_isolation_policy ON lancamentos IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY parcelas_tenant_isolation_policy ON parcelas IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY contas_pagar_tenant_isolation_policy ON contas_pagar IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY contas_receber_tenant_isolation_policy ON contas_receber IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY permissoes_tenant_isolation_policy ON permissoes IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant';
COMMENT ON POLICY permissoes_usuario_tenant_isolation_policy ON permissoes_usuario IS 'Isolamento de tenant: apenas acessível pelo tenant atual via app.current_tenant'; 