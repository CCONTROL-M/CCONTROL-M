# CCONTROL-M Backend

## Visão Geral
Sistema backend para gerenciamento financeiro empresarial, com foco em controle de pagamentos, recebimentos e cálculos financeiros precisos para pequenas e médias empresas.

## Estrutura de Pastas

- `app/` - Código principal da aplicação
  - `models/` - Modelos de dados SQLAlchemy
  - `schemas/` - Schemas Pydantic para validação
  - `api/` - Endpoints da API REST
  - `services/` - Lógica de negócio
  - `utils/` - Funções utilitárias

- `tests/` - Testes automatizados
  - `unit/` - Testes unitários
  - `integration/` - Testes de integração

- `migrations/` - Scripts de migração de banco de dados
  - `rls/` - Políticas de Row Level Security

- `scripts/` - Scripts auxiliares e ferramentas de administração

- `docs/` - Documentação técnica

## Executando Testes Financeiros

Para executar todos os testes de cálculos financeiros, use o seguinte comando:

```bash
$env:TEST_MODE="integration"; python -m pytest tests/unit/calculations/ --maxfail=1 --disable-warnings --cov=app --cov-report=term-missing
```

> **Nota**: O modo de integração é necessário para garantir que os testes não sejam pulados.

## Cobertura de Cálculos

| Arquivo de Teste | O que Valida |
|------------------|--------------|
| `test_parcelas.py` | Geração de parcelas, arredondamento, pagamento antecipado e parcial |
| `test_juros_e_multas.py` | Juros simples, juros compostos, multas e taxas variáveis |
| `test_fluxo_caixa.py` | Projeção de saldo, análise de fluxo, balanço patrimonial |
| `test_datas_vencimento.py` | Ajuste de datas para feriados/fins de semana, dias úteis |
| `test_exceptions.py` | Validação de erros, exceções de pagamento, formato de dados |

## Configuração de Ambiente de Teste

### Variáveis de Ambiente

```
TEST_MODE=integration  # Modo de teste (unit/integration)
TEST_DB_TYPE=sqlite    # Tipo de banco (sqlite/postgres)
```

### SQLite In-Memory

Por padrão, os testes usam SQLite in-memory para facilitar os testes sem dependências externas:

```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

Para usar PostgreSQL local:

```
TEST_DB_TYPE=postgres
TEST_POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/testdb
```

## Políticas de Segurança (RLS)

O sistema utiliza Row Level Security para isolamento de dados entre empresas.

Scripts principais:
- [`migrations/rls/empresa_policies.sql`](migrations/rls/empresa_policies.sql) - Políticas de isolamento por empresa
- [`migrations/rls/user_policies.sql`](migrations/rls/user_policies.sql) - Políticas de acesso por usuário

Para aplicar as políticas:

```bash
psql -U postgres -d ccontrol_db -f migrations/rls/empresa_policies.sql
```

## Próximos Passos

- [ ] Completar migrações para PostgreSQL
- [ ] Revisar testes restantes (rotas e serviços)
- [ ] Ativar métricas Prometheus
- [ ] Implementar cache para queries frequentes
- [ ] Adicionar suporte para exportação de relatórios em PDF
- [ ] Completar integração com serviços de pagamento
- [ ] Refinar documentação com exemplos de uso

## Requisitos

- Python 3.11+
- PostgreSQL 14+ (local) ou Supabase (cloud)
- Pip

## Configuração do Ambiente

### Configuração de Variáveis de Ambiente

Existem três arquivos de ambiente:

- `.env.example` - Modelo de configuração
- `.env` - Ambiente de desenvolvimento
- `.env.prod` - Ambiente de produção

Crie os arquivos `.env` e `.env.prod` a partir do `.env.example` adaptando conforme necessário.

**Importante**: Nunca compartilhe seu arquivo `.env.prod` com senhas e tokens reais.

### Configuração do Banco de Dados

O sistema suporta duas opções de banco de dados:

#### 1. PostgreSQL Local

```
# No arquivo .env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/ccontrolm
DATABASE_URL_TEST=postgresql+asyncpg://postgres:postgres@localhost/ccontrolm_test
```

#### 2. Supabase (PostgreSQL na nuvem)

```
# No arquivo .env
DATABASE_URL=postgresql+asyncpg://postgres.xxxxxxxxxxxx:senha@db.xxxxxxxxxxxx.supabase.co:5432/postgres
DATABASE_URL_TEST=postgresql+asyncpg://postgres.xxxxxxxxxxxx:senha@db.xxxxxxxxxxxx.supabase.co:5432/postgres

# Credenciais do Supabase
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SUPABASE_DB_HOST=db.xxxxxxxxxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.xxxxxxxxxxxx
SUPABASE_DB_PASSWORD=suasenha
```

### Instalação de Dependências

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Executando o Sistema

### Ambiente de Desenvolvimento

```bash
# Na pasta backend
python -m app.main
```

Ou:

```bash
uvicorn app.main:app --reload
```

### Ambiente de Produção

```bash
# Na pasta backend
chmod +x start_prod.sh
./start_prod.sh
```

Ou via Docker:

```bash
docker build -t ccontrol-m-backend .
docker run -d -p 8000:8000 --name ccontrol-backend ccontrol-m-backend
```

## Configurando o Supabase

Para configurar corretamente o Supabase para uso com o sistema:

1. Crie uma conta no [Supabase](https://supabase.com/)
2. Crie um novo projeto
3. Na seção "Table Editor", você precisará criar as seguintes tabelas:
   - `usuarios`
   - `empresas`
   - `logs_sistema`
   - `lancamentos`
   - `clientes`
   - `fornecedores`
   - `produtos`
   - `categorias`
   - `parcelas`
   - `contas_bancarias`
   - `formas_pagamento`
   - `vendas`
   - `centro_custos`

4. Você pode criar as tabelas manualmente ou utilizar as migrações do sistema:
   ```bash
   # Configurar DATABASE_URL para apontar para o Supabase
   alembic upgrade head
   ```

5. Configure as políticas de segurança (RLS) no Supabase conforme necessário

## Acessando o MCP do Supabase

O MCP (Supabase Management Console Protocol) permite acessar e gerenciar o Supabase diretamente do código. Para utilizá-lo:

1. Certifique-se de que seu ambiente tem acesso ao MCP
2. Use as ferramentas do MCP para consultar schemas, tabelas e dados
3. Para desenvolvimento, utilize o Console do Supabase para visualizar dados

## Testes

Para executar todos os testes:

```bash
pytest
```

Para testes com cobertura:

```bash
pytest --cov=app tests/
```

Para testes isolados que não dependem de conexão com o banco:

```bash
pytest tests/unit_test_*.py
```

## Acesso à API

- API: http://localhost:8000/api/v1
- Documentação: http://localhost:8000/api/v1/docs
- Saúde: http://localhost:8000/health

## Estrutura do Projeto

```
backend/
│
├── app/                  # Código principal
│   ├── config/           # Configurações
│   ├── models/           # Modelos ORM
│   ├── repositories/     # Camada de acesso a dados
│   ├── routers/          # Endpoints da API
│   ├── schemas/          # Esquemas Pydantic
│   ├── services/         # Lógica de negócio
│   └── utils/            # Utilitários e módulos auxiliares
│
├── migrations/           # Migrações do banco de dados
├── tests/                # Testes automatizados
├── .env.example          # Modelo de variáveis de ambiente
├── .env                  # Variáveis para desenvolvimento
├── .env.prod             # Variáveis para produção
├── requirements.txt      # Dependências
├── start_prod.sh         # Script para iniciar em produção
└── Dockerfile            # Configuração para Docker
```

## Configuração de Testes

O projeto CCONTROL-M utiliza uma estrutura de testes que permite executar testes unitários sem depender de conexões reais com banco de dados, e testes de integração que podem usar diferentes engines de banco de dados conforme necessário.

### Estratégia de Testes

O sistema de testes usa duas abordagens principais:

1. **Testes Unitários**: 
   - Funcionam sem conexão real com o banco de dados
   - Usam mocks completos para simular interações com o banco
   - São mais rápidos e não precisam de infraestrutura externa

2. **Testes de Integração**: 
   - Testam a interação com dependências reais ou simuladas
   - Podem usar diferentes engines de banco de dados
   - Verificam o funcionamento completo dos componentes

### Marcadores de Teste

O sistema utiliza marcadores do pytest para controlar o comportamento dos testes:

- `@pytest.mark.unit`: Marca testes unitários que não devem usar banco de dados
- `@pytest.mark.integration`: Marca testes que requerem acesso ao banco de dados
- `@pytest.mark.no_db`: Marca explicitamente testes que não devem usar banco de dados (alternativa ao `unit`)
- `@pytest.mark.slow`: Marca testes que são mais lentos para execução

Os marcadores podem ser usados tanto em funções individuais quanto em nível de módulo:

```python
# Marcar todo o módulo
pytestmark = pytest.mark.unit

# OU marcar funções específicas
@pytest.mark.unit
def test_exemplo():
    pass
```

### Configuração do Ambiente de Teste

Os testes podem ser executados em diferentes modos através de variáveis de ambiente:

- `TEST_MODE`: Define o modo de teste (`unit` ou `integration`)
- `TEST_DB_TYPE`: Para testes de integração, especifica o tipo de banco (`sqlite`, `postgres` ou `supabase`)

### Como Executar os Testes

#### Testes Unitários (Padrão)

```bash
# Executar todos os testes unitários (modo padrão)
pytest -m unit

# Executar arquivo de teste específico
pytest tests/unit_test_auditoria_service.py -v
```

#### Testes de Integração

```bash
# Executar testes de integração com SQLite (sem dependências externas)
TEST_MODE=integration pytest -m integration

# Executar testes de integração com PostgreSQL local
TEST_MODE=integration TEST_DB_TYPE=postgres pytest -m integration

# Executar testes de integração com Supabase (apenas se necessário)
TEST_MODE=integration TEST_DB_TYPE=supabase pytest -m integration
```

### Estrutura do Projeto de Testes

- `conftest.py`: Contém configurações e fixtures comuns para os testes
- `tests/unit_*.py`: Testes unitários sem dependência de banco
- `tests/integration_*.py`: Testes de integração com dependência de banco

### Melhores Práticas

1. **Para Testes Unitários:**
   - Use o marcador `@pytest.mark.unit` ou `pytestmark = pytest.mark.unit`
   - Utilize `AsyncMock` e `MagicMock` para simular serviços e repositórios
   - Nunca tente acessar o banco de dados real

2. **Para Testes de Integração:**
   - Use o marcador `@pytest.mark.integration`
   - Para testes locais, prefira SQLite in-memory (`TEST_DB_TYPE=sqlite`)
   - Use o fixture `db_session` para acesso ao banco

3. **Dicas Gerais:**
   - Execute testes unitários com frequência durante o desenvolvimento
   - Execute testes de integração antes de fazer commit/push
   - Mantenha os testes independentes entre si 

## Documentação

- A documentação da API está disponível em `/docs` quando o servidor está em execução
- [Guia de Estilo e Nomenclatura](docs/STYLE_GUIDE.md) - Padrões de código e nomenclatura adotados no projeto 

## Segurança e Multi-tenancy

- Todas as tabelas do sistema utilizam Row Level Security (RLS) para isolamento de dados
- Políticas RLS completamente implementadas e documentadas em [docs/database_policies.md](docs/database_policies.md)
- Verificação e aplicação de RLS via scripts em `scripts/check_rls.py` e `scripts/apply_unified_rls.py`
- Backup com suporte a RLS disponível via `scripts/database_backup.py`

## Migrações de Banco de Dados

- Migrações gerenciadas com Alembic através do SQLAlchemy
- Adicione novas migrações com `alembic revision -m "descrição"`
- Execute migrações pendentes com `alembic upgrade head`
- Verifique o estado atual das migrações com `alembic current`
- Todas as entidades do sistema estão refletidas nas migrações 

Este diretório contém a implementação do backend para o sistema CCONTROL-M de controle financeiro.

## Servidor de Teste

Foi implementado um servidor de teste simplificado para os endpoints de lançamentos financeiros, permitindo testes sem dependências externas como banco de dados.

### Como executar o servidor de teste

```bash
# A partir do diretório backend
python -m app.test_server
```

O servidor será executado na porta 8002 e disponibilizará os seguintes endpoints:

### Endpoints Disponíveis

#### Verificação de Saúde
- **GET /health** - Verifica o status do servidor

#### Lançamentos Financeiros (CRUD)
- **GET /api/v1/lancamentos** - Lista lançamentos financeiros com filtros e paginação
  - Parâmetros: id_empresa (obrigatório), tipo, id_categoria, id_centro_custo, id_conta, status, data_inicio, data_fim, page, page_size
  
- **POST /api/v1/lancamentos** - Cria um novo lançamento financeiro
  - Corpo da requisição: descricao, valor, data_lancamento, data_pagamento (opcional), tipo, id_categoria, id_empresa, id_conta (opcional), id_centro_custo (opcional)

- **GET /api/v1/lancamentos/{id_lancamento}** - Obtém detalhes de um lançamento específico
  - Parâmetros: id_lancamento (no caminho), id_empresa (na query)

- **PUT /api/v1/lancamentos/{id_lancamento}** - Atualiza um lançamento existente
  - Parâmetros: id_lancamento (no caminho), id_empresa (na query)
  - Corpo da requisição: campos a serem atualizados (todos opcionais)

- **DELETE /api/v1/lancamentos/{id_lancamento}** - Exclui um lançamento existente
  - Parâmetros: id_lancamento (no caminho), id_empresa (na query)

### Documentação

A API possui documentação Swagger completa acessível em:
- http://127.0.0.1:8002/docs - Interface Swagger UI
- http://127.0.0.1:8002/openapi.json - Especificação OpenAPI em formato JSON

## Servidor de Produção

Para o servidor de produção, utilize o módulo app.main:

```bash
# A partir do diretório raiz do projeto
uvicorn app.main:app --reload
```

Os endpoints do servidor de produção seguem a mesma estrutura do servidor de teste, mas utilizam o banco de dados PostgreSQL configurado. 