# CCONTROL-M - Sistema de Controle Empresarial

## 📋 Sobre o Projeto

CCONTROL-M é um sistema de controle empresarial completo desenvolvido em Python usando FastAPI. O sistema oferece funcionalidades para gestão de produtos, vendas, clientes, fornecedores, controle financeiro e geração de relatórios.

## 🚀 Tecnologias

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, PostgreSQL
- **Banco de Dados**: PostgreSQL (local) ou Supabase (cloud)
- **Segurança**: JWT, OAuth2, CORS, Rate Limiting
- **Documentação**: OpenAPI (Swagger), ReDoc
- **Monitoramento**: Prometheus, Grafana
- **CI/CD**: GitHub Actions
- **Containerização**: Docker, Docker Compose

## 🛠️ Requisitos

- Python 3.8+
- PostgreSQL 13+ ou acesso ao Supabase
- Docker e Docker Compose (opcional)
- wkhtmltopdf (para geração de PDFs)

## 📦 Instalação

### Desenvolvimento Local

1. Clone o repositório:
```bash
git clone https://github.com/CCONTROL-M/CCONTROL-M.git
cd CCONTROL-M
```

2. Configure o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Configure o acesso ao banco de dados:

   **Opção 1: PostgreSQL Local**
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/ccontrolm
   ```

   **Opção 2: Supabase**
   ```
   DATABASE_URL=postgresql+asyncpg://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:5432/{SUPABASE_DB_NAME}
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_ANON_KEY=sua-chave-anon-aqui
   ```

6. Execute as migrações:
```bash
alembic upgrade head
```

7. Inicie o servidor de desenvolvimento:
```bash
uvicorn app.main:app --reload
```

### Usando Docker

1. Construa e inicie os containers:
```bash
docker-compose up -d --build
```

## 🗄️ Configuração do Banco de Dados

O sistema suporta dois modos de operação para o banco de dados:

### PostgreSQL Local

Para desenvolvimento local ou implantação em servidores próprios, configure o PostgreSQL:

1. Instale o PostgreSQL 13+
2. Crie um banco de dados para o projeto
3. Configure a URL de conexão no arquivo `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost/nome_do_banco
   ```

### Supabase (PostgreSQL na nuvem)

Para facilitar o desenvolvimento e implantação, o sistema também suporta o Supabase:

1. Crie uma conta no [Supabase](https://supabase.com/)
2. Crie um novo projeto
3. Obtenha as credenciais de conexão na seção "Settings > Database"
4. Configure no arquivo `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres.xxxxxxxxxxxx:senha@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## 📚 Documentação

A documentação completa do projeto está disponível na pasta [docs/](./docs/):

- [Documentação de Instalação](./docs/INSTALACAO.md)
- [Documentação Técnica](./docs/README.md)
- [Documentação de Testes Automatizados](./docs/TESTES.md) ✨ NOVO!

## 🔐 Segurança

O sistema implementa várias camadas de segurança:

- Autenticação JWT
- Rate Limiting
- CORS configurável
- Validação de inputs
- Auditoria de ações
- Row Level Security (RLS)

## 🧪 Testes

Execute os testes com:

```bash
# Testes unitários
pytest

# Com cobertura
pytest --cov=app

# Testes específicos
pytest tests/test_specific.py
```

## 📊 Monitoramento

- Métricas: `/metrics` (Prometheus)
- Health Check: `/health`
- Logs: Configurados para stdout/arquivo

## 🚢 Deploy

1. Produção com Docker:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. Sem Docker:
```bash
./scripts/setup-production.sh
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- Documentação: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/CCONTROL-M/CCONTROL-M/issues)
- Email: ricardoe@conectamoveis.net.br

## ⚡ Status do Projeto

![CI/CD](https://github.com/CCONTROL-M/CCONTROL-M/workflows/CI/CD/badge.svg)
![Tests](https://github.com/CCONTROL-M/CCONTROL-M/workflows/Tests/badge.svg)
![Coverage](https://codecov.io/gh/CCONTROL-M/CCONTROL-M/branch/master/graph/badge.svg)

## Visão Geral

O CCONTROL-M é um sistema completo de controle financeiro desenvolvido para gerenciar fluxo de caixa, vendas a prazo, contas a pagar e receber, e diversos relatórios financeiros.

## Estrutura do Projeto

O projeto é dividido em duas partes principais:

```
CCONTROL-M/
├── frontend/     # Aplicação React com TypeScript
├── backend/      # API Backend com FastAPI (Python)
├── scripts/      # Scripts auxiliares para o projeto
└── docs/         # Documentação do projeto
```

## Execução em Ambiente Docker (Produção Local)

> **⚠️ IMPORTANTE**: Para utilizar o ambiente Docker, é necessário instalar o [Docker Desktop](https://www.docker.com/products/docker-desktop/) em seu sistema. Se o Docker não estiver instalado, você poderá seguir as instruções de instalação no site oficial ou usar o método de desenvolvimento local descrito anteriormente.

### Passo a Passo para Executar com Docker

1. **Verificação do Docker**:
   ```powershell
   docker --version
   ```
   Certifique-se que o Docker está instalado e funcionando corretamente.

2. **Iniciar com Script Automatizado**:
   ```powershell
   .\start_prod.ps1
   ```
   Este script verifica requisitos, configura o ambiente e inicia os containers.

3. **OU Iniciar Manualmente**:
   ```powershell
   # Construir e iniciar containers
   docker-compose up -d --build
   ```

4. **Verificar Status dos Containers**:
   ```powershell
   docker-compose ps
   ```
   Todos os serviços devem estar como "running".

5. **Acessar a Aplicação**:
   - Frontend: http://localhost 
   - API: http://localhost/api/docs

6. **Encerrar o Ambiente**:
   ```powershell
   docker-compose down
   ```

Para simular um ambiente de produção localmente usando Docker, o CCONTROL-M disponibiliza uma configuração completa de containerização.

### Arquivos de Configuração Docker

O projeto inclui os seguintes arquivos para configuração Docker:
- `docker-compose.yml` - Orquestração dos serviços frontend e backend
- `backend/Dockerfile` - Configuração do contêiner backend (Python/FastAPI)
- `frontend/Dockerfile` - Configuração do contêiner frontend (build com Node.js, serve com Nginx)
- `frontend/nginx.conf` - Configuração do servidor web para o frontend
- `.env.docker` - Variáveis de ambiente para o ambiente Docker

#### Descrição Detalhada dos Componentes Docker

1. **Contêiner Backend**:
   - Baseado em Python 3.9
   - Expõe a porta 8002
   - Executa o FastAPI com Uvicorn
   - Conecta-se ao banco de dados Supabase (configurado no .env.docker)
   - Processa requisições da API REST

2. **Contêiner Frontend**:
   - Build multi-estágio: Node.js para compilação, Nginx para servir
   - Compila a aplicação React/TypeScript para arquivos estáticos
   - Configuração de Nginx otimizada com cache, compressão e segurança
   - Proxy reverso para API e documentação
   - Gerenciamento de rotas do React Router

3. **Rede Docker**:
   - Rede compartilhada `ccontrol-network` para comunicação entre serviços
   - Configuração do contêiner frontend para acessar o backend via nome de serviço

Estas configurações estão prontas para uso em um ambiente de produção local ou em servidores de homologação.

### Logs e Monitoramento Docker

Para visualizar os logs dos contêineres e monitorar sua execução:

```powershell
# Ver logs de todos os serviços
docker-compose logs

# Ver logs em tempo real (follow)
docker-compose logs -f

# Ver logs apenas do frontend
docker-compose logs -f frontend

# Ver logs apenas do backend
docker-compose logs -f backend
```

#### Exemplos de Logs Comuns

**Logs de inicialização bem-sucedida do Backend:**
```
ccontrol-m-backend  | INFO:     Started server process [1]
ccontrol-m-backend  | INFO:     Waiting for application startup.
ccontrol-m-backend  | INFO:     Application startup complete.
ccontrol-m-backend  | INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
```

**Logs de inicialização bem-sucedida do Frontend:**
```
ccontrol-m-frontend | /docker-entrypoint.sh: Configuration complete; ready for start up
ccontrol-m-frontend | 2025/03/24 12:34:56 [notice] 1#1: start worker processes
ccontrol-m-frontend | 2025/03/24 12:34:56 [notice] 1#1: start worker process 20
```

**Erros comuns e soluções:**
- Se o backend mostrar erros de conexão com o banco de dados, verifique as variáveis em `.env.docker`
- Se o frontend mostrar erros 502, verifique se o backend está em execução e acessível via rede Docker
- Para problemas de permissão em volumes, execute `docker-compose down -v` e inicie novamente

## Tecnologias Utilizadas

### Frontend
- React
- TypeScript
- React Router
- Axios para requisições HTTP
- CSS puro para estilização

### Backend
- FastAPI (Python)
- SQLAlchemy para ORM
- PostgreSQL como banco de dados
- Pydantic para validação de dados

## Padrões de Desenvolvimento

### Estrutura de Arquivos Frontend

```
frontend/
├── src/
│   ├── components/   # Componentes reutilizáveis
│   ├── pages/        # Páginas da aplicação
│   ├── services/     # Serviços de API
│   ├── App.tsx       # Componente principal e rotas
│   ├── index.css     # Estilos globais
│   └── main.tsx      # Ponto de entrada
```

### Modo Mock do Frontend

O frontend possui um modo mock para desenvolvimento e testes, que permite utilizar dados fictícios sem depender da API backend. Importante ressaltar:

- O modo mock está disponível **apenas em ambiente de desenvolvimento**.
- Um botão de toggle é exibido no canto inferior direito da aplicação em desenvolvimento.
- O modo mock pode ser ativado definindo `VITE_MOCK_ENABLED=true` no arquivo `.env.local`.
- O sistema NÃO entra automaticamente em modo mock quando a API está offline.
- Para mais detalhes, consulte o arquivo `frontend/src/README.md`.

### Convenções de Nomenclatura

- **Componentes**: PascalCase (ex: `Header.tsx`, `Sidebar.tsx`)
- **Páginas**: PascalCase (ex: `Dashboard.tsx`, `VendasParcelas.tsx`)
- **Serviços**: camelCase (ex: `api.ts`)
- **CSS**: Classes em kebab-case (ex: `sidebar-menu-item`)

### Padrão de Estilização

- Classes CSS seguem a nomenclatura BEM simplificada
- Cores, espaçamentos e tipografia são consistentes
- Todos os componentes usam as classes CSS definidas no `index.css`

## Endpoints da API

### Estrutura Geral

A API está disponível em `http://localhost:8000` e todos os endpoints têm o prefixo `/api/v1/`. Principais recursos:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/dashboard/resumo` | GET | Resumo dos indicadores financeiros |
| `/api/v1/lancamentos` | GET, POST | Listar e criar lançamentos financeiros |
| `/api/v1/vendas` | GET, POST | Listar e criar vendas |
| `/api/v1/parcelas` | GET | Listar parcelas de vendas |
| `/api/v1/clientes` | GET, POST | Listar e criar clientes |
| `/api/v1/fornecedores` | GET, POST | Listar e criar fornecedores |
| `/api/v1/contas-bancarias` | GET, POST | Listar e criar contas bancárias |
| `/api/v1/categorias` | GET, POST | Listar e criar categorias |
| `/api/v1/centros-custo` | GET, POST | Listar e criar centros de custo |
| `/api/v1/empresas` | GET, POST | Listar e criar empresas |
| `/api/v1/logs` | GET | Listar logs de auditoria |

### Formato de Respostas

As respostas da API seguem o formato JSON padrão. Exemplo:

```json
{
  "id_lancamento": "uuid",
  "descricao": "Pagamento fornecedor",
  "valor": 1500.00,
  "data": "2025-03-15T10:30:00Z",
  "tipo": "saida",
  "status": "efetivado"
}
```

## Fluxo de Trabalho

### Desenvolvimento de Nova Funcionalidade

1. Verificar endpoints disponíveis na API
2. Criar interface TypeScript para os dados
3. Implementar componente React com estados necessários
4. Adicionar chamadas à API usando o serviço `api`
5. Implementar tratamento de loading e erros
6. Estilizar seguindo o padrão visual existente
7. Adicionar rota no `App.tsx` e link no `Sidebar.tsx`

### Integração Frontend/Backend

- O frontend usa Axios configurado para apontar para `http://localhost:8000`
- Dados são validados no frontend antes de enviar para a API
- Todas as mensagens de erro são tratadas e exibidas ao usuário

## Execução do Projeto

### Frontend
```bash
cd frontend
npm install
npm run dev
```
A aplicação estará disponível em `http://localhost:3001`.

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```
A API estará disponível em `http://localhost:8000`.

## Solução de Problemas Comuns

### 1. Erro de Permissão de Scripts no PowerShell

**Problema**: Mensagem de erro "a execução de scripts foi desabilitada neste sistema" ao executar npm ou outros comandos.

**Solução**: Execute o PowerShell como administrador e utilize o comando:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Erro 404 em Páginas do Frontend

**Problema**: Erro "Failed to load resource: the server responded with a status of a 404 (Not Found)" em alguma página.

**Causas possíveis**:
- A página está referenciada no App.tsx mas o arquivo não existe em `frontend/src/pages/`
- A URL da API está incorreta no componente da página
- O endpoint no backend não corresponde ao especificado no frontend

**Solução**:
1. Verifique se o arquivo da página existe na pasta `frontend/src/pages/`
2. Certifique-se de que a chamada à API usa o formato correto: `/api/v1/[recurso]`
3. Compare as rotas definidas em `backend/app/routers/__init__.py` com as chamadas no frontend

### 3. Estrutura Correta do Diretório

**Atenção**: A estrutura correta dos diretórios é:
```
CCONTROL-M/
├── frontend/     # Aplicação React
├── backend/      # API FastAPI (e não "app" como referenciado em alguns lugares)
└── scripts/      # Scripts de inicialização e utilitários
```

Para iniciar corretamente o backend, use:
```bash
cd backend
uvicorn app.main:app --reload
```

### 4. Ferramenta de Diagnóstico

O projeto inclui ferramentas de diagnóstico que podem ajudar a identificar problemas:

- **Script de diagnóstico**: Execute `.\diagnostico.ps1` para verificar o estado do ambiente
- **Script de inicialização**: Execute `.\start_dev.ps1` para iniciar tanto o backend quanto o frontend
- **Componente de debug**: Nas páginas que incluem o componente APIDebug, use o botão "Mostrar Diagnóstico" para testar a conexão com a API

### 5. Problemas com CORS

Se encontrar erros de CORS, verifique:
1. Se o backend está rodando em `http://localhost:8000`
2. Se o frontend está rodando em `http://localhost:3000` ou `http://localhost:3001`
3. Se as configurações de CORS no backend (`backend/app/middlewares/cors_middleware.py`) incluem a origem do frontend

## Principais Páginas

- **Dashboard**: Resumo financeiro e indicadores
- **Lançamentos**: Gestão de entradas e saídas
- **Vendas & Parcelas**: Gestão de vendas parceladas
- **Relatórios**: DRE e Fluxo de Caixa
- **Cadastros**: Clientes, Fornecedores, Contas, etc.
- **Administração**: Usuários, Permissões e Logs

## Manutenção e Boas Práticas

1. Manter consistência visual entre as páginas
2. Reutilizar componentes sempre que possível
3. Seguir os padrões de nomenclatura estabelecidos
4. Documentar novas funcionalidades neste README
5. Tratar adequadamente todos os estados (loading, erro, vazio)
6. Testar novas funcionalidades antes de integrar 

## Modo Mock

O frontend possui um sistema de modo mock para funcionamento offline, permitindo o desenvolvimento e testes mesmo quando a API está indisponível.

### Como funciona o modo mock

- O sistema detecta automaticamente quando a API está offline e ativa o modo mock
- Existe um toggle na interface para ativar/desativar o modo mock manualmente
- Configuração via variável de ambiente: `VITE_MOCK_ENABLED=true`

### Serviços com suporte a mock implementado

- ✅ Clientes
- ✅ Fornecedores
- ✅ Vendas e Parcelas
- ✅ Lançamentos (contas a pagar/receber)
- ✅ Transferências entre Contas
- ✅ Logs do sistema
- ✅ Formas de pagamento
- ✅ Relatórios (DRE, Fluxo de Caixa, Inadimplência, Ciclo Operacional) - migrados para dados reais!
- ✅ Dashboard - migrado para dados reais!
- ❌ Categorias (pendente)
- ❌ Centros de Custo (pendente)
- ❌ Contas Bancárias (pendente)
- ❌ Empresas (pendente)
- ❌ Configurações (pendente)

Para mais detalhes sobre o modo mock, consulte o README específico do frontend em `frontend/src/README.md`.

## Status da Migração para Dados Reais

Todos os serviços principais do sistema agora estão utilizando dados reais do banco de dados PostgreSQL/Supabase, incluindo:

- **Relatórios Financeiros**:
  - ✅ DRE (Demonstrativo de Resultado do Exercício)
  - ✅ Fluxo de Caixa
  - ✅ Relatório de Inadimplência
  - ✅ Ciclo Operacional
  - ✅ Dashboard financeiro

- **Endpoints de Negócio**:
  - ✅ CRUD de Clientes
  - ✅ CRUD de Fornecedores
  - ✅ CRUD de Produtos
  - ✅ CRUD de Categorias
  - ✅ CRUD de Centros de Custo
  - ✅ CRUD de Lançamentos
  - ✅ CRUD de Vendas e Parcelas

A Fase 6.1 foi concluída com sucesso, com todas as rotas agora consumindo dados reais, sem uso de mock, com filtros corretos e integração estável com o frontend.

## URLs de Desenvolvimento e Testes

As seguintes URLs são utilizadas para desenvolvimento e testes:

- **Frontend:** http://localhost:3000
- **Backend API:** http://127.0.0.1:8002/api/v1
- **Documentação API (Swagger):** http://127.0.0.1:8002/docs

> **Nota:** Certifique-se de que o arquivo `.env` do frontend está configurado com `VITE_API_URL=http://127.0.0.1:8002/api/v1` para garantir a conexão correta com a API.

## Iniciando o Ambiente de Desenvolvimento

O CCONTROL-M possui scripts automatizados para facilitar a inicialização do ambiente de desenvolvimento completo (frontend + backend). Siga um dos métodos abaixo:

### Método 1: Scripts Automáticos (Recomendado)

Utilize os scripts prontos para iniciar automaticamente tanto o backend quanto o frontend em terminais separados:

#### Windows PowerShell:
```bash
.\start_dev.ps1
```

#### Windows CMD:
```bash
start_dev.bat
```

Esses scripts:
1. Encerram qualquer processo nas portas 3000 e 8000
2. Iniciam o servidor backend (FastAPI/Uvicorn) na porta 8000
3. Aguardam 5 segundos para o backend inicializar
4. Iniciam o servidor frontend (Vite) na porta 3000
5. Geram logs separados na pasta `logs/`

### Método 2: Inicialização Manual

Se preferir iniciar manualmente, abra dois terminais separados:

#### Terminal 1 (Backend):
```bash
cd backend
# Ativar ambiente virtual se necessário
# .\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### Acessando a Aplicação

Após iniciar o ambiente, acesse:
- **Frontend:** http://localhost:3000
- **API Backend:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs

## Preparando para Produção

### Backend (FastAPI)

Para ambiente de produção, recomendamos usar Uvicorn com Gunicorn:

```bash
cd backend

# Instalar Gunicorn (se ainda não estiver instalado)
pip install gunicorn

# Iniciar com Gunicorn (ajuste workers conforme necessário)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Frontend (React)

Para ambiente de produção, compile o frontend e sirva com um servidor web:

```bash
cd frontend

# Compilar para produção
npm run build

# Os arquivos estáticos serão gerados na pasta 'dist'
# Sirva esses arquivos usando Nginx, Apache, Vercel, Netlify, etc.
```

Exemplo de configuração Nginx:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        root /caminho/para/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Modo Real - Dados do Banco de Dados

> **IMPORTANTE**: Todas as rotas da API agora estão configuradas para usar dados reais do banco de dados Supabase, incluindo:
> - ✅ Dashboard e indicadores financeiros
> - ✅ Relatório DRE (Demonstrativo de Resultados)
> - ✅ Relatório de Fluxo de Caixa
> - ✅ Relatório de Inadimplência
> - ✅ Relatório de Ciclo Operacional
> - ✅ Todas as operações CRUD padrão (cadastros, atualizações, exclusões)

O sistema não utiliza mais o modo mock por padrão. Todos os dados são carregados diretamente do banco de dados PostgreSQL/Supabase.

### Conexão com a API

O frontend está configurado para conectar com o backend na URL: `http://127.0.0.1:8002/api/v1` definida na variável de ambiente `VITE_API_URL` no arquivo `.env`.

### Autenticação e ID Empresa

Todas as requisições à API incluem:
- **Bearer Token**: Obtido automaticamente do localStorage após login
- **ID Empresa**: Extraído do token JWT ou, em desenvolvimento, usando um ID temporário de fallback

### Tratamento de Erros

Em caso de falha na API:
- O sistema exibe mensagens de erro apropriadas
- O modo mock não é ativado automaticamente
- Os usuários são notificados do problema para tentar novamente 