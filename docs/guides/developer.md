# Guia de Desenvolvimento - CCONTROL-M

Este documento fornece diretrizes e instruções para desenvolvedores que trabalham no projeto CCONTROL-M. Siga estas orientações para manter a consistência e a qualidade do código.

## Índice

1. [Configuração do Ambiente](#configuração-do-ambiente)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Convenções de Código](#convenções-de-código)
4. [Fluxo de Trabalho Git](#fluxo-de-trabalho-git)
5. [API e Endpoints](#api-e-endpoints)
6. [Banco de Dados](#banco-de-dados)
7. [Testes](#testes)
8. [Segurança](#segurança)
9. [Performance](#performance)
10. [Deploy](#deploy)
11. [Troubleshooting](#troubleshooting)

## Configuração do Ambiente

### Pré-requisitos

- Python 3.8+ 
- PostgreSQL 13+
- Docker e Docker Compose (opcional, mas recomendado)
- Git
- Editor recomendado: VS Code com Python, Docker e GitLens

### Ambiente Virtual Python

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows
.\venv\Scripts\activate
# No Linux/macOS
source venv/bin/activate

# Instalar dependências
cd backend
pip install -r requirements.txt
```

### Variáveis de Ambiente

Crie um arquivo `.env` a partir do `.env.example`:

```bash
cp backend/.env.example backend/.env
```

Edite as variáveis conforme suas configurações locais, especialmente:
- `DATABASE_URL`: URL de conexão do banco de dados
- `SECRET_KEY`: Chave secreta para JWT
- `ALLOWED_HOSTS`: Hosts permitidos
- `DEBUG`: Ative para desenvolvimento (`True`)

### Docker para Desenvolvimento

Para usar Docker no desenvolvimento:

```bash
# Iniciar todos os serviços (banco, backend, cache)
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Parar serviços
docker-compose down
```

## Estrutura do Projeto

```
backend/
├── app/                       # Código principal da aplicação
│   ├── api/                   # Definições da API
│   ├── core/                  # Core da aplicação
│   ├── db/                    # Definições e configurações de DB
│   ├── models/                # Modelos SQLAlchemy
│   ├── schemas/               # Modelos Pydantic
│   ├── services/              # Lógica de negócio
│   ├── repositories/          # Camada de acesso a dados
│   ├── routers/               # Rotas API
│   ├── middlewares/           # Middlewares
│   ├── utils/                 # Utilitários
│   └── main.py                # Ponto de entrada da aplicação
├── tests/                     # Testes
├── migrations/                # Migrações do banco de dados
├── alembic.ini                # Configuração Alembic
├── requirements.txt           # Dependências
└── docker-compose.yml         # Configuração Docker
```

## Convenções de Código

### Estilo de Código

Seguimos PEP 8 e usamos formatadores automáticos:

- Black para formatação de código
- isort para ordenação de imports
- flake8 para linting

Para formatar seu código:

```bash
# Formatar código com black
black backend/

# Ordenar imports com isort
isort backend/

# Verificar erros de estilo com flake8
flake8 backend/
```

### Convenções de Nomenclatura

- **Arquivos**: snake_case (ex: `user_service.py`)
- **Classes**: PascalCase (ex: `UserService`)
- **Funções/Métodos**: snake_case (ex: `get_user_by_id()`)
- **Variáveis**: snake_case (ex: `user_count`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_CONNECTIONS`)

### Docstrings e Comentários

Usamos docstrings no estilo Google para documentação:

```python
def calcular_preco_total(produtos, desconto=0.0):
    """
    Calcula o preço total dos produtos aplicando o desconto.
    
    Args:
        produtos (list): Lista de dicionários com produtos e preços.
        desconto (float, opcional): Valor do desconto (0.0-1.0). Padrão 0.0.
        
    Returns:
        float: Preço total após desconto.
        
    Raises:
        ValueError: Se o desconto for negativo ou maior que 1.0.
    """
```

## Fluxo de Trabalho Git

### Branches

- `main`: Código estável e pronto para produção
- `develop`: Branch de desenvolvimento principal
- `feature/*`: Novas funcionalidades (ex: `feature/gestao-estoque`)
- `bugfix/*`: Correções de bugs (ex: `bugfix/erro-calculo-preco`)
- `release/*`: Preparação para release (ex: `release/v1.0.0`)
- `hotfix/*`: Correções urgentes na produção (ex: `hotfix/v1.0.1`)

### Commits

Padrão de mensagens de commit:

```
tipo(escopo): descrição curta

Descrição detalhada se necessário.
```

Tipos comuns:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `refactor`: Refatoração de código
- `test`: Adição/modificação de testes
- `chore`: Mudanças em build, configs, etc.

### Pull Requests

- Crie PRs com descrições detalhadas
- Referencie issues relacionadas com `#numero_issue`
- Solicite code review de pelo menos um desenvolvedor
- Certifique-se que os testes passam antes de solicitar review

## API e Endpoints

### Padrões RESTful

Seguimos padrões RESTful com os seguintes verbos HTTP:

- `GET`: Obter recursos
- `POST`: Criar recursos
- `PUT`: Atualizar recursos (completo)
- `PATCH`: Atualizar recursos (parcial)
- `DELETE`: Remover recursos

### Estrutura de Rotas

```
/api/v1/[recurso]              # Listar ou criar
/api/v1/[recurso]/{id}         # Obter, atualizar ou excluir
/api/v1/[recurso]/{id}/[ação]  # Executar ação específica
```

### Versionamento

Usamos versionamento no path (`/api/v1/`). Mudanças incompatíveis devem incrementar o número da versão.

## Banco de Dados

### Migrações

Usamos Alembic para gerenciar migrações:

```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição da migração"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1
```

### Boas Práticas

- Use UUID como chave primária em vez de inteiros sequenciais
- Sempre crie índices para campos frequentemente consultados
- Use soft delete (flag `is_active`) em vez de excluir registros
- Utilize propriedades como `created_at`, `updated_at` em todas as tabelas
- Sempre use `async_session` para operações assíncronas

## Testes

### Tipos de Testes

- **Unitários**: Testam componentes isolados (services, repositories)
- **Integração**: Testam a interação entre componentes
- **API**: Testam endpoints HTTP
- **E2E**: Testam fluxos completos de usuário

### Executando Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/services/test_user_service.py

# Teste específico
pytest tests/test_file.py::test_function -v
```

### Mocking

Use `unittest.mock` ou `pytest-mock` para mocks:

```python
def test_get_user(mocker):
    # Criar mock do repositório
    mock_repo = mocker.patch("app.repositories.user_repository.UserRepository")
    mock_repo.get_by_id.return_value = User(id=1, name="Test User")
    
    # Testar serviço
    service = UserService(mock_repo)
    user = service.get_user(1)
    
    # Verificar resultado
    assert user.name == "Test User"
    mock_repo.get_by_id.assert_called_once_with(1)
```

## Segurança

### Autenticação e Autorização

- Use OAuth2 com JWT para autenticação
- Defina níveis de acesso claros
- Implemente rate limiting para evitar ataques de força bruta
- Use tempos de expiração curtos para tokens

### Dados Sensíveis

- Nunca armazene senhas em texto plano (use bcrypt)
- Use variáveis de ambiente para credenciais
- Sempre mascare dados sensíveis nos logs

### OWASP Top 10

Mitigamos as vulnerabilidades do OWASP Top 10:

- Injeção: Use parâmetros com SQLAlchemy
- Quebra de autenticação: Use OAuth2 e rate limiting
- Exposição de dados: Use HTTPS e mascare dados sensíveis
- XXE: Parseadores seguros de XML
- Quebra de controle de acesso: Verificação de permissões
- Security Misconfiguration: Hardening de configurações
- XSS: Validação e escape de inputs
- Deserialização insegura: Validação rigorosa com Pydantic
- Componentes vulneráveis: Dependabot para atualizar pacotes
- Logging e monitoramento: Logs estruturados e alertas

## Performance

### Otimizações

- Use paginação para listas grandes
- Implemente cache onde apropriado
- Otimize consultas SQL com índices adequados
- Use Lazy Loading com SQLAlchemy
- Configure timeouts para todas as operações externas

### Monitoramento

- Use Prometheus para métricas
- Configure alertas para problemas de performance
- Monitore logs para detectar gargalos
- Utilize APM (Application Performance Monitoring)

## Deploy

### Ambientes

- **Development**: Desenvolvimento local
- **Testing**: Testes automatizados
- **Staging**: Testes manuais, similar à produção
- **Production**: Ambiente de produção

### CI/CD

Pipeline no GitHub Actions:

1. Lint e verificação de código
2. Testes unitários e de integração
3. Build de imagem Docker
4. Deploy em ambiente de staging
5. Testes E2E em staging
6. Deploy em produção (manual ou automatizado)

## Troubleshooting

### Logs

- Os logs estão em `logs/app.log` e no stdout
- Use `--log-level DEBUG` para mais detalhes
- Consulte o Grafana para visualizar tendências

### Problemas Comuns

- **Erro de conexão com banco**: Verifique DATABASE_URL e firewall
- **Tempo limite excedido**: Verifique carga do servidor e índices
- **Erros 500**: Consulte logs para stack trace
- **Autenticação falhando**: Verifique chaves JWT e data de expiração 