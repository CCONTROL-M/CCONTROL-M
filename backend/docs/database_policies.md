# Políticas RLS no CCONTROL-M

Este documento descreve as políticas de Row Level Security (RLS) implementadas no CCONTROL-M para garantir o isolamento de dados entre diferentes empresas (multi-tenancy).

## Visão Geral

O CCONTROL-M utiliza Row Level Security (RLS) para implementar multi-tenancy no banco de dados PostgreSQL. Isso significa que cada consulta ao banco de dados é automaticamente filtrada para mostrar apenas os dados pertencentes à empresa do usuário atual, protegendo dados de outras empresas.

## Abordagens Implementadas

O sistema implementa duas abordagens complementares para RLS:

### 1. Usando Variáveis de Sessão (`app.current_tenant`)

Esta abordagem define uma variável de sessão `app.current_tenant` contendo o ID da empresa atual.

```sql
SET app.current_tenant = 'id-da-empresa-uuid';
```

As políticas RLS utilizam esta variável para filtrar os resultados:

```sql
CREATE POLICY tenant_isolation_policy ON tabela
USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
```

### 2. Usando `auth.uid()` e Relacionamentos

Esta abordagem utiliza a função `auth.uid()` do Supabase para obter o ID do usuário autenticado e filtra os dados com base nos relacionamentos entre usuário e empresas.

```sql
CREATE POLICY "Acesso aos clientes da empresa" ON clientes
FOR ALL
USING (id_empresa IN (
    SELECT empresa_id FROM usuario_empresa 
    WHERE usuario_id = auth.uid()
));
```

## Políticas Implementadas

### Contas a Pagar

```sql
-- Ativar RLS
ALTER TABLE contas_pagar ENABLE ROW LEVEL SECURITY;

-- Abordagem 1: Usando app.current_tenant
CREATE POLICY contas_pagar_tenant_isolation_policy ON contas_pagar
USING (empresa_id = (current_setting('app.current_tenant', TRUE))::uuid);

-- Abordagem 2: Usando auth.uid
CREATE POLICY "Acesso às contas a pagar da empresa" ON conta_pagar
FOR ALL
USING (empresa_id IN (
    SELECT empresa_id FROM usuario_empresa 
    WHERE usuario_id = auth.uid()
));
```

### Contas a Receber

```sql
-- Ativar RLS
ALTER TABLE contas_receber ENABLE ROW LEVEL SECURITY;

-- Abordagem 1: Usando app.current_tenant
CREATE POLICY contas_receber_tenant_isolation_policy ON contas_receber
USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);

-- Abordagem 2: Usando auth.uid
CREATE POLICY "Acesso às contas a receber da empresa" ON conta_receber
FOR ALL
USING (id_empresa IN (
    SELECT empresa_id FROM usuario_empresa 
    WHERE usuario_id = auth.uid()
));
```

### Permissões

```sql
-- Ativar RLS
ALTER TABLE permissoes ENABLE ROW LEVEL SECURITY;

-- Abordagem 1: Usando app.current_tenant
CREATE POLICY permissoes_tenant_isolation_policy ON permissoes
USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);

-- Abordagem 2: Usando auth.uid
CREATE POLICY "Acesso às permissões do usuário" ON permissao
FOR ALL
USING (
    id_usuario = auth.uid() OR 
    (id_empresa IN (
        SELECT empresa_id FROM usuario_empresa 
        WHERE usuario_id = auth.uid() AND is_admin = true
    ))
);
```

### Permissões de Usuário

```sql
-- Ativar RLS
ALTER TABLE permissoes_usuario ENABLE ROW LEVEL SECURITY;

-- Abordagem 1: Usando app.current_tenant
CREATE POLICY permissoes_usuario_tenant_isolation_policy ON permissoes_usuario
USING (
    id_usuario IN (
        SELECT id_usuario FROM usuarios WHERE id_empresa = (current_setting('app.current_tenant', TRUE))::uuid
    )
);

-- Abordagem 2: Usando auth.uid
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
```

## Índices Otimizados

Para garantir o desempenho adequado das consultas com filtros RLS, os seguintes índices foram adicionados:

```sql
CREATE INDEX idx_contas_pagar_empresa_id ON contas_pagar(empresa_id);
CREATE INDEX idx_contas_receber_id_empresa ON contas_receber(id_empresa);
CREATE INDEX idx_permissoes_id_empresa ON permissoes(id_empresa);
CREATE INDEX idx_permissoes_usuario_id_usuario ON permissoes_usuario(id_usuario);
```

## Verificação de RLS

Para verificar se as políticas RLS estão configuradas corretamente, execute:

```bash
python scripts/check_rls.py
```

## Backup e Restauração com RLS

Ao fazer backup e restauração do banco de dados, é importante incluir as definições RLS para manter a segurança dos dados. Utilize o script de backup dedicado:

```bash
python scripts/database_backup.py --include-rls
```

## Considerações para Desenvolvimento

Ao desenvolver novos recursos, lembre-se:

1. Todas as tabelas que contêm dados específicos de empresas devem ter RLS ativado
2. Adicione a coluna `id_empresa` ou `empresa_id` em todas as tabelas que necessitam de isolamento
3. Crie políticas RLS para novas tabelas seguindo os padrões existentes
4. Ao testar, defina a variável de sessão `app.current_tenant` ou utilize um usuário com acesso à empresa específica

## Limitações e Ajustes

- RLS adiciona uma pequena sobrecarga às consultas
- Consultas complexas podem exigir ajustes para otimização com RLS
- Operações em lote devem considerar o contexto de isolamento 