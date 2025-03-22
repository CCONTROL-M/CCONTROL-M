# CCONTROL-M Backend

Sistema de gestão empresarial com controle financeiro, vendas e gestão multi-empresa.

## Requisitos

- Python 3.11+
- PostgreSQL 14+
- Pip

## Configuração do Ambiente

### Configuração de Variáveis de Ambiente

Existem três arquivos de ambiente:

- `.env.example` - Modelo de configuração
- `.env` - Ambiente de desenvolvimento
- `.env.prod` - Ambiente de produção

Crie os arquivos `.env` e `.env.prod` a partir do `.env.example` adaptando conforme necessário.

**Importante**: Nunca compartilhe seu arquivo `.env.prod` com senhas e tokens reais.

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

## Testes

Para executar todos os testes:

```bash
pytest
```

Para testes com cobertura:

```bash
pytest --cov=app tests/
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