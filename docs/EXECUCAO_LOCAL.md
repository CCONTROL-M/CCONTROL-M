# Execução Local do Projeto CCONTROL-M

Este documento contém as instruções detalhadas para executar o projeto CCONTROL-M em ambiente de desenvolvimento local.

## Pré-requisitos

- Python 3.8+ (recomendado 3.12)
- Node.js 18+ (recomendado 20+)
- PostgreSQL 13+ (ou Supabase)
- Windows, Linux ou macOS

## Configuração e Execução do Backend

No Windows, o PowerShell não aceita o operador `&&` para separar comandos. É necessário usar um dos seguintes métodos:

### Método 1: Executar cada comando separadamente

```powershell
# Navegar para o diretório backend
cd backend

# Iniciar o servidor uvicorn na porta 8002
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### Método 2: Usar o operador `;` para separar comandos

```powershell
cd backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### Método 3: Executar o script PowerShell

```powershell
.\backend\app\start_win.ps1
```

**Importante**: O backend deve ser executado na porta 8002, pois essa é a porta configurada no frontend.

### Verificação do Backend

Para verificar se o backend está funcionando corretamente, acesse:

- API: http://127.0.0.1:8002/api/v1
- Documentação: http://127.0.0.1:8002/docs
- Health Check: http://127.0.0.1:8002/api/v1/health

## Configuração e Execução do Frontend

Assim como no backend, no Windows há múltiplos métodos para iniciar o frontend.

### Método 1: Executar cada comando separadamente

```powershell
# Navegar para o diretório frontend
cd frontend

# Iniciar o servidor de desenvolvimento
npm run dev
```

### Método 2: Usar o operador `;` para separar comandos

```powershell
cd frontend; npm run dev
```

### Método 3: Executar o script batch

```powershell
# No PowerShell, é necessário prefixar com .\
.\frontend\start_frontend.bat
```

O frontend estará disponível em http://localhost:3000.

## Verificação do Ambiente

O arquivo `.env` no diretório frontend está configurado para se conectar ao backend na porta 8002:

```
VITE_API_URL=http://127.0.0.1:8002/api/v1
```

## Solução de Problemas Comuns

### Erro: `O token '&&' não é um separador de instruções válido nesta versão`

**Solução**: Use `;` em vez de `&&` para separar comandos no PowerShell, ou execute os comandos um por um.

### Erro: `TypeError: BaseRepository.__init__() missing 1 required positional argument: 'session'`

**Causa**: Problema na inicialização do repositório de fornecedores.

**Solução**: Verificar o código do backend para garantir que a injeção de dependência da sessão está correta.

### Erro: `Formatting field not found in record: 'request_id'`

**Causa**: Problema na configuração de logging que tenta acessar 'request_id' que não existe.

**Solução**: Isso não impede o funcionamento da aplicação, apenas afeta o logging.

### Erro: `start_frontend.bat não é reconhecido como nome de cmdlet, função, arquivo de script ou programa operável`

**Solução**: Use `.\start_frontend.bat` em vez de `start_frontend.bat`.

## Utilização de Portas

- Backend: http://127.0.0.1:8002
- Frontend: http://localhost:3000

Essas portas são configuradas nos respectivos arquivos de configuração de cada parte do projeto. 