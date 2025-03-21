# CCONTROL-M - Sistema de Controle Financeiro

Sistema de controle financeiro com suporte a multi-tenancy e recursos de segurança aprimorados.

## Arquivos de Configuração

### Variáveis de Ambiente

O sistema utiliza variáveis de ambiente para configuração. Um modelo dessas variáveis está disponível em `.env.example`. Para configurar o sistema:

1. Copie o arquivo `.env.example` para `.env`
2. Preencha com os valores reais do seu ambiente

**IMPORTANTE:** O arquivo `.env` contém informações sensíveis e nunca deve ser commitado no repositório Git. Ele já está adicionado ao `.gitignore`.

## Scripts de Manutenção

### Backup do Banco de Dados

O script `backend/backup_database.py` realiza backups completos do banco de dados PostgreSQL:

```bash
python backend/backup_database.py [--only-structure] [--only-data] [--keep-backups N]
```

Opções:
- `--only-structure`: Faz backup apenas da estrutura (schemas, tabelas, etc.)
- `--only-data`: Faz backup apenas dos dados
- `--keep-backups N`: Mantém apenas os últimos N backups diários (padrão: 10)

Os backups são comprimidos e organizados por data em `backend/backups/`.

### Validação de Integridade do Banco de Dados

O script `backend/validate_db_integrity.py` verifica a integridade do banco de dados:

```bash
python backend/validate_db_integrity.py
```

Este script busca por:
- Registros órfãos (com chaves estrangeiras inválidas)
- Inconsistências nos relacionamentos (vendas, parcelas, etc.)
- Dados duplicados (CPF/CNPJ, emails, etc.)

Os relatórios de validação são gerados no formato JSON na pasta `logs/`.

### Verificação de Consistência Financeira

O script `backend/check_financial_consistency.py` verifica a consistência dos dados financeiros:

```bash
python backend/check_financial_consistency.py [--fix]
```

Opções:
- `--fix`: Corrige automaticamente as inconsistências encontradas

Este script verifica e corrige:
- Vendas parceladas sem parcelas
- Inconsistências entre valor total de vendas e soma das parcelas
- Lançamentos com referências inválidas
- Parcelas pagas sem lançamentos correspondentes

Os relatórios são gerados no formato JSON na pasta `logs/`.

## Configuração de Multi-Tenancy

### Isolamento por Tenant (Empresa)

O script `backend/setup_tenant_isolation.py` configura o isolamento por tenant no banco de dados:

```bash
python backend/setup_tenant_isolation.py
```

Este script implementa:
- Funções para obter e definir o tenant atual
- Triggers para garantir que registros sejam inseridos no tenant correto
- Validações para evitar operações entre tenants diferentes
- Funções de API para manipulação de tenants

### Configuração de Políticas RLS

O script `backend/configure_rls_policies.py` configura as políticas de Row-Level Security:

```bash
python backend/configure_rls_policies.py
```

Este script:
- Faz backup das políticas RLS existentes
- Padroniza as políticas para todas as tabelas
- Configura políticas específicas para casos especiais

## Segurança

O sistema implementa diversas camadas de segurança:

1. **Isolamento de Tenants**: Dados de uma empresa são completamente isolados de outras empresas
2. **Políticas RLS**: Controle de acesso granular no nível do banco de dados
3. **Autenticação JWT**: Autenticação segura com tokens JWT
4. **Variáveis de Ambiente**: Informações sensíveis armazenadas em variáveis de ambiente
5. **Backups Regulares**: Sistema de backup automatizado

## Estrutura do Banco de Dados

O banco de dados utiliza PostgreSQL e está estruturado em quatro esquemas principais:

- `public`: Tabelas principais do aplicativo
- `auth`: Tabelas relacionadas à autenticação (gerenciadas pelo Supabase)
- `storage`: Armazenamento de arquivos (gerenciado pelo Supabase)
- `migration_history`: Histórico de migrações e backups de configurações

## Desenvolvimento

### Requisitos

- Python 3.10+
- PostgreSQL 14+
- Supabase (para autenticação e armazenamento)

### Configuração do Ambiente de Desenvolvimento

1. Crie um ambiente virtual Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Configure o arquivo `.env` conforme o modelo em `.env.example`

4. Execute as migrações:
   ```bash
   python backend/alembic upgrade head
   ```

5. Inicie o servidor de desenvolvimento:
   ```bash
   python backend/main.py
   ```

## Produção

Para implantação em produção, siga estas práticas recomendadas:

1. Use um proxy reverso (Nginx, Traefik) com SSL
2. Configure variáveis de ambiente específicas para produção
3. Ative o modo de produção nas configurações
4. Configure backups automatizados usando um agendador (cron, Task Scheduler)
5. Monitore os logs da aplicação regularmente

## Contribuição

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Envie para o repositório remoto (`git push origin feature/nova-funcionalidade`)
5. Crie um Pull Request 