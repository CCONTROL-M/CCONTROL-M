-- Script para configuração de Row Level Security (RLS) no Supabase
-- Para o sistema CCONTROL-M

-- Ativar RLS em todas as tabelas
ALTER TABLE empresa ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuario_empresa ENABLE ROW LEVEL SECURITY;
ALTER TABLE cliente ENABLE ROW LEVEL SECURITY;
ALTER TABLE fornecedor ENABLE ROW LEVEL SECURITY;
ALTER TABLE categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE centro_custo ENABLE ROW LEVEL SECURITY;
ALTER TABLE conta_bancaria ENABLE ROW LEVEL SECURITY;
ALTER TABLE forma_pagamento ENABLE ROW LEVEL SECURITY;
ALTER TABLE lancamento ENABLE ROW LEVEL SECURITY;
ALTER TABLE lancamento_anexo ENABLE ROW LEVEL SECURITY;
ALTER TABLE venda ENABLE ROW LEVEL SECURITY;
ALTER TABLE parcela ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_atividade ENABLE ROW LEVEL SECURITY;

-- Políticas por tabela

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

-- Anexos de Lançamento: Acesso apenas aos anexos de lançamentos das empresas do usuário
CREATE POLICY "Acesso aos anexos de lançamentos da empresa" ON lancamento_anexo
    FOR ALL
    USING (lancamento_id IN (
        SELECT id FROM lancamento 
        WHERE empresa_id IN (
            SELECT empresa_id FROM usuario_empresa 
            WHERE usuario_id = auth.uid()
        )
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