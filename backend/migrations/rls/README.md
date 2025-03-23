# Segurança em Nível de Linha (RLS) no CCONTROL-M

Este diretório contém os scripts para configuração de Row-Level Security (RLS) no sistema CCONTROL-M.
A RLS é fundamental para garantir o isolamento de dados entre diferentes empresas no sistema multi-tenant.

## Arquivos Disponíveis

- **supabase_rls_unified.sql**: Script principal unificado para configuração de RLS (recomendado)
- **01_enable_rls.sql**: Script original para ativar RLS (mantido para compatibilidade)
- **02_disable_rls.sql**: Script para desativar RLS (uso em desenvolvimento/testes)
- **enable_only_existing.sql**: Script para ativar RLS apenas nas tabelas existentes

## Abordagens de Multi-tenancy no CCONTROL-M

O sistema implementa duas abordagens complementares para garantir o isolamento de dados:

### 1. Usando variável de sessão `app.current_tenant`

Esta abordagem configura uma variável de sessão PostgreSQL com o ID da empresa atual:

```sql
SET app.current_tenant = 'uuid-da-empresa';
```

As políticas RLS verificam se o `id_empresa` do registro corresponde ao valor definido:

```sql
CREATE POLICY tenant_isolation ON tabela
USING (id_empresa = (current_setting('app.current_tenant', TRUE))::uuid);
```

Esta abordagem é implementada automaticamente pelo middleware `tenant_middleware.py`.

### 2. Usando o ID do usuário autenticado (auth.uid)

Esta abordagem é usada no Supabase e se baseia nas relações entre usuários e empresas:

```sql
CREATE POLICY user_company_access ON tabela
USING (id_empresa IN (
    SELECT empresa_id FROM usuario_empresa 
    WHERE usuario_id = auth.uid()
));
```

Isso permite que um usuário acesse apenas dados das empresas às quais está vinculado.

## Tabelas com Políticas RLS Implementadas

Todas as seguintes tabelas possuem políticas RLS para garantir o isolamento adequado de dados entre empresas:

1. **Usuários** (`usuarios`/`usuario`)
2. **Clientes** (`clientes`/`cliente`)
3. **Produtos** (`produtos`/`produto`)
4. **Vendas** (`vendas`/`venda`)
5. **Categorias** (`categorias`/`categoria`)
6. **Lançamentos** (`lancamentos`/`lancamento`)
7. **Parcelas** (`parcelas`/`parcela`)
8. **Formas de Pagamento** (`formas_pagamento`/`forma_pagamento`)
9. **Contas Bancárias** (`contas_bancarias`/`conta_bancaria`)
10. **Fornecedores** (`fornecedores`/`fornecedor`)
11. **Centro de Custos** (`centro_custos`/`centro_custo`)
12. **Logs do Sistema** (`logs_sistema`/`log_sistema`)
13. **Empresas** (`empresas`/`empresa`)
14. **Relações Usuário-Empresa** (`usuario_empresa`)
15. **Contas a Pagar** (`contas_pagar`/`conta_pagar`) ✓
16. **Contas a Receber** (`contas_receber`/`conta_receber`) ✓
17. **Permissões** (`permissoes`/`permissao`) ✓
18. **Permissões de Usuário** (`permissoes_usuario`/`permissao_usuario`) ✓

> ✓ = Políticas adicionadas recentemente

## Verificação e Aplicação

Para verificar a configuração de RLS no banco de dados:

```bash
python scripts/check_rls.py
```

Para aplicar as políticas RLS:

```bash
python scripts/apply_unified_rls.py
```

Para realizar backup das tabelas, incluindo as políticas RLS:

```bash
python scripts/database_backup.py --include-rls
```

## Como Aplicar as Políticas RLS

### Método 1: Usando o script Python

Execute o script `apply_unified_rls.py` a partir da raiz do projeto:

```bash
python scripts/apply_unified_rls.py
```

Opções disponíveis:
- `--env-file`: Especificar um arquivo .env personalizado
- `--sql-file`: Especificar um arquivo SQL personalizado
- `--dry-run`: Executar em modo de simulação sem aplicar as alterações

### Método 2: Execução manual do SQL

1. Conecte-se ao banco de dados:
```bash
psql -d sua_base_de_dados -U seu_usuario
```

2. Execute o script SQL:
```sql
\i migrations/rls/supabase_rls_unified.sql
```

## Verificação

Para verificar se as políticas estão funcionando corretamente:

1. Liste as políticas ativas:
```sql
SELECT * FROM pg_policies;
```

2. Teste o isolamento para uma empresa específica:
```sql
-- Defina o tenant atual
SET app.current_tenant = 'uuid-da-empresa-1';

-- Tente acessar registros
SELECT * FROM clientes;
```

3. Mude para outra empresa e verifique se apenas seus dados são retornados:
```sql
SET app.current_tenant = 'uuid-da-empresa-2';
SELECT * FROM clientes;
```

## Importante

- As políticas RLS não substituem a autenticação e autorização na API
- A RLS é uma camada adicional de segurança no nível do banco de dados
- Sempre teste após a configuração para garantir o isolamento correto
- Em ambiente de desenvolvimento, pode ser útil desativar a RLS temporariamente usando `02_disable_rls.sql` 