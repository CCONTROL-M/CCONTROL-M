# Guia de Testes

## Problemas Comuns e Soluções

### 1. Configuração do Ambiente

#### Problema com PYTHONPATH
Os testes podem falhar com erro de importação de módulos. Para resolver:

```bash
# Windows (PowerShell)
$env:PYTHONPATH = "caminho/para/pasta/backend;$env:PYTHONPATH"

# Linux/Mac
export PYTHONPATH="/caminho/para/pasta/backend:$PYTHONPATH"
```

### 2. Banco de Dados de Teste

#### Configuração Correta
Use sempre `settings.DATABASE_URL_TEST` para testes. Exemplo:

```python
from app.config.settings import settings

test_engine = create_async_engine(
    settings.DATABASE_URL_TEST,
    echo=True,
    future=True
)
```

### 3. Sessões Assíncronas

#### Uso Correto
Sempre use sessões assíncronas com FastAPI:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

async_session_maker = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        await session.rollback()
```

### 4. Executando os Testes

#### Comando Correto
```bash
# Na pasta backend
python -m pytest tests/ -v
```

### 5. Fixtures Comuns

#### Configuração de Logger
```python
@pytest.fixture(autouse=True)
def setup_logger():
    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'request_id'):
                record.request_id = 'test-request-id'
            return True
    
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(RequestIDFilter())
    
    yield
    
    for handler in root_logger.handlers:
        for filter in handler.filters:
            if isinstance(filter, RequestIDFilter):
                handler.removeFilter(filter)
```

### 6. Boas Práticas

1. Use sempre `@pytest.mark.asyncio` para testes assíncronos
2. Evite misturar código síncrono e assíncrono
3. Use fixtures para reutilizar configurações
4. Limpe o banco após cada teste
5. Use mocks quando apropriado para testes unitários
6. Documente casos especiais nos testes

### 7. Estrutura de Arquivos

```
backend/
├── tests/
│   ├── conftest.py      # Configurações globais
│   ├── api/             # Testes de API
│   ├── services/        # Testes de serviços
│   └── repositories/    # Testes de repositórios
```

### 8. Depuração

Para depurar falhas nos testes:

1. Use o flag `-s` para ver prints: `pytest -s`
2. Use o flag `-v` para ver detalhes: `pytest -v`
3. Use o flag `-k` para rodar testes específicos: `pytest -k "test_nome"`
4. Use `breakpoint()` para debugging interativo 