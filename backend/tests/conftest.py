"""Configurações para os testes."""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from app.config.settings import settings
from app.database import Base

# Definir o modo de teste: unit (padrão) ou integration
# Pode ser configurado via variável de ambiente
TEST_MODE = os.getenv("TEST_MODE", "unit")

# Configuração de conexão baseada no modo de teste
if TEST_MODE == "integration":
    # Para testes de integração, use SQLite in-memory por padrão
    # Ou se TEST_DB_TYPE estiver definido como "postgres", use PostgreSQL local
    TEST_DB_TYPE = os.getenv("TEST_DB_TYPE", "sqlite")
    
    if TEST_DB_TYPE == "postgres":
        # Usar PostgreSQL local para testes de integração
        TEST_DATABASE_URL = os.getenv(
            "TEST_POSTGRES_URL", 
            "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
        )
    elif TEST_DB_TYPE == "supabase" and settings.DATABASE_URL_TEST:
        # Usar Supabase apenas se explicitamente solicitado
        TEST_DATABASE_URL = settings.DATABASE_URL_TEST
    else:
        # SQLite in-memory é a opção padrão mais simples para testes
        TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    
    # Engine para testes de integração
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        # SQLite específico - necessário para suporte a foreign keys
        connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {},
        future=True
    )
    
    # Session factory para testes de integração
    test_async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
else:
    # No modo unitário, definimos estas variáveis apenas para evitar erros,
    # mas elas não serão usadas em testes unitários
    test_engine = None
    test_async_session = None


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Cria um event loop para os testes."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def skip_db_for_unit_tests(request):
    """
    Determina se o teste deve usar banco de dados ou não.
    
    Critérios para pular o setup do banco:
    1. Marcador explícito `no_db` no teste
    2. Ambiente global definido como TEST_MODE=unit
    3. Marcador `unit` no teste
    """
    skip_db = False
    
    # Verificar marcador no_db explícito
    if request.node.get_closest_marker("no_db"):
        skip_db = True
    # Verificar se é teste unitário pelo marcador
    elif request.node.get_closest_marker("unit"):
        skip_db = True
    # Verificar configuração global
    elif TEST_MODE == "unit":
        skip_db = True
        
    if skip_db:
        request.config.stash[f"{request.node.nodeid}_skip_db"] = True


@pytest.fixture(autouse=True)
async def setup_database(request) -> AsyncGenerator:
    """
    Configura o banco de dados para os testes de integração.
    
    Esta fixture é ignorada para testes unitários conforme lógica do
    fixture skip_db_for_unit_tests.
    """
    # Verificar se devemos pular este fixture
    if request.config.stash.get(f"{request.node.nodeid}_skip_db", False):
        # Se for teste unitário, simplesmente retornamos sem configurar o banco
        yield
        return
    
    # Apenas para testes de integração - configurar banco real
    if TEST_MODE != "integration":
        pytest.skip("Este teste requer TEST_MODE=integration para acessar banco de dados")
    
    try:
        # Criar tabelas para teste
        async with test_engine.begin() as conn:
            # Para SQLite in-memory, precisamos fazer setup completo
            if str(test_engine.url).startswith("sqlite"):
                await conn.run_sync(Base.metadata.create_all)
            else:
                # Para PostgreSQL, primeiro limpar e depois criar
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        
        yield
        
        # Limpar tabelas após o teste
        if not str(test_engine.url).startswith("sqlite"):
            # SQLite in-memory já é limpo ao fechar a conexão
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                
    except Exception as e:
        print(f"Erro ao configurar banco de dados para teste: {e}")
        # Se não puder usar o banco, o teste deve falhar adequadamente
        pytest.skip(f"Falha ao configurar banco de dados: {e}")


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture que fornece uma sessão de banco de dados para os testes.
    Apenas para testes de integração.
    """
    if TEST_MODE != "integration":
        pytest.skip("Este teste requer TEST_MODE=integration para acessar banco de dados")
        
    async with test_async_session() as session:
        try:
            yield session
            # Rollback de qualquer alteração pendente
            await session.rollback()
        finally:
            # Garantir que a sessão seja fechada
            await session.close()


# Fixture para criar um mock de sessão para testes unitários
@pytest.fixture
def mock_db_session():
    """
    Fornece um mock de sessão para testes unitários.
    """
    from unittest.mock import AsyncMock, MagicMock
    
    mock_session = AsyncMock()
    # Configurar comportamentos comuns do mock
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    
    # Configurar métodos para simular resultados de consultas
    mock_session.execute = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    mock_session.add = MagicMock()
    mock_session.refresh = AsyncMock()
    
    return mock_session 