# CCONTROL-M - Sistema de Controle Empresarial

## 📋 Sobre o Projeto

CCONTROL-M é um sistema de controle empresarial completo desenvolvido em Python usando FastAPI. O sistema oferece funcionalidades para gestão de produtos, vendas, clientes, fornecedores, controle financeiro e geração de relatórios.

## 🚀 Tecnologias

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, PostgreSQL
- **Segurança**: JWT, OAuth2, CORS, Rate Limiting
- **Documentação**: OpenAPI (Swagger), ReDoc
- **Monitoramento**: Prometheus, Grafana
- **CI/CD**: GitHub Actions
- **Containerização**: Docker, Docker Compose

## 🛠️ Requisitos

- Python 3.8+
- PostgreSQL 13+
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

5. Execute as migrações:
```bash
alembic upgrade head
```

6. Inicie o servidor de desenvolvimento:
```bash
uvicorn app.main:app --reload
```

### Usando Docker

1. Construa e inicie os containers:
```bash
docker-compose up -d --build
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