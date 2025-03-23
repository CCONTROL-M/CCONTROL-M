# Guia de Instalação e Execução do CCONTROL-M

Este guia fornece instruções detalhadas para instalar e executar o CCONTROL-M em ambiente de desenvolvimento e produção.

## Requisitos do Sistema

Antes de começar, certifique-se de ter instalado:

- **Node.js**: v16.0.0 ou superior (para o frontend)
- **npm**: v8.0.0 ou superior (gerenciador de pacotes JavaScript)
- **Python**: v3.8 ou superior (para o backend)
- **pip**: Gerenciador de pacotes Python
- **PostgreSQL**: v13 ou superior (banco de dados)
- **Git**: Para clonar o repositório

## Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seuusuario/CCONTROL-M.git
cd CCONTROL-M
```

### 2. Configurar o Backend

```bash
# Entrar na pasta do backend
cd backend

# Criar ambiente virtual Python (opcional, mas recomendado)
python -m venv venv

# Ativar o ambiente virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
# Windows:
copy .env.example .env
# Linux/Mac:
# cp .env.example .env

# Edite o arquivo .env com suas configurações de banco de dados
```

### 3. Configurar o Frontend

```bash
# Voltar para a raiz do projeto
cd ..

# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
# Windows:
copy .env.example .env
# Linux/Mac:
# cp .env.example .env
```

## Execução

### Método 1: Scripts Automáticos (Recomendado)

O projeto inclui scripts que automatizam a inicialização tanto do backend quanto do frontend:

#### Windows PowerShell:
```bash
.\start_dev.ps1
```

#### Windows CMD:
```bash
start_dev.bat
```

Este método:
1. Encerra quaisquer processos nas portas 3000 e 8000
2. Inicia o backend (FastAPI/Uvicorn) em `http://localhost:8000`
3. Inicia o frontend (Vite/React) em `http://localhost:3000`
4. Gera logs na pasta `logs/`

### Método 2: Execução Manual

Se preferir iniciar os serviços manualmente:

#### Terminal 1 (Backend):
```bash
cd backend

# Ativar ambiente virtual (se criado)
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

## Acessando a Aplicação

Após a inicialização, você pode acessar:

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **Alternativa Swagger**: http://localhost:8000/redoc

## Configuração do Banco de Dados

O sistema suporta PostgreSQL. Certifique-se de:

1. Ter o PostgreSQL instalado e rodando
2. Configurar a string de conexão no arquivo `.env` do backend:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
   ```

## Troubleshooting

### Problemas Comuns:

1. **Porta já em uso**:
   - Os scripts automáticos tentam finalizar processos existentes
   - Manualmente, você pode verificar e encerrar processos:
     ```bash
     # Windows
     netstat -ano | findstr :3000
     taskkill /PID <PID> /F
     
     # Linux/Mac
     lsof -i :3000
     kill -9 <PID>
     ```

2. **Erro de Módulo não Encontrado**:
   - No frontend: `npm install`
   - No backend: `pip install -r requirements.txt`

3. **Erro de Conexão com o Banco**:
   - Verifique se o PostgreSQL está em execução
   - Confira as credenciais de acesso no `.env`

4. **Frontend sem Comunicação com API**:
   - Confirme se o backend está rodando
   - Verifique se as configurações de CORS estão corretas

## Execução em Ambiente de Produção

### Backend

Para produção, é recomendado usar Uvicorn com Gunicorn:

```bash
cd backend

# Instalar Gunicorn
pip install gunicorn

# Iniciar com workers adequados
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Frontend

Para produção, compile os arquivos estáticos e sirva-os com um servidor web:

```bash
cd frontend

# Compilar para produção
npm run build

# Os arquivos estarão disponíveis na pasta 'dist'
```

Você pode servir os arquivos estáticos usando Nginx, Apache, Vercel, Netlify ou outro servidor de sua preferência. 