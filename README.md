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

- [Guia de Início Rápido](docs/guides/quickstart.md)
- [Documentação da API](docs/api/README.md)
- [Arquitetura](docs/architecture/README.md)
- [Guia de Desenvolvimento](docs/guides/development.md)
- [Catálogo de Erros](docs/errors/README.md)

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
- ❌ Categorias (pendente)
- ❌ Centros de Custo (pendente)
- ❌ Contas Bancárias (pendente)
- ❌ Empresas (pendente)
- ❌ Configurações (pendente)

Para mais detalhes sobre o modo mock, consulte o README específico do frontend em `frontend/src/README.md`.

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