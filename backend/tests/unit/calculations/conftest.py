"""Fixtures compartilhadas para testes de cálculos financeiros."""
import pytest
import asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Configuração para um banco de dados SQLite em memória para testes
@pytest.fixture
def event_loop():
    """Cria um novo event loop para cada teste."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_sqlite_engine():
    """Cria um engine SQLite assíncrono em memória para testes."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    await engine.dispose()

@pytest.fixture
async def async_session_factory(async_sqlite_engine):
    """Cria uma fábrica de sessões assíncronas para SQLite."""
    from app.database import Base
    
    async with async_sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        async_sqlite_engine, class_=AsyncSession, expire_on_commit=False
    )
    yield async_session
    
    async with async_sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(async_session_factory):
    """Cria uma sessão de banco de dados para cada teste."""
    async with async_session_factory() as session:
        yield session

@pytest.fixture
def mock_db_session():
    """Mock de sessão de banco de dados para testes unitários puros."""
    mock = AsyncMock()
    mock.execute.return_value = AsyncMock()
    mock.execute.return_value.scalars.return_value.all.return_value = []
    mock.execute.return_value.scalar_one_or_none.return_value = None
    mock.commit.return_value = None
    mock.refresh.return_value = None
    return mock

@pytest.fixture
def feriados():
    """Lista de feriados para testes de ajuste de datas."""
    ano_atual = date.today().year
    return [
        date(ano_atual, 1, 1),    # Ano Novo
        date(ano_atual, 4, 21),   # Tiradentes
        date(ano_atual, 5, 1),    # Dia do Trabalho
        date(ano_atual, 9, 7),    # Independência
        date(ano_atual, 10, 12),  # Nossa Senhora Aparecida
        date(ano_atual, 11, 2),   # Finados
        date(ano_atual, 11, 15),  # Proclamação da República
        date(ano_atual, 12, 25),  # Natal
    ]

@pytest.fixture
def create_parcela_mock():
    """Cria um objeto parcela mock para testes."""
    def _create_parcela(
        id_parcela=None,
        numero=1,
        valor=Decimal("100.00"),
        data_vencimento=date.today() + timedelta(days=30),
        status="pendente",
        id_venda=None,
    ):
        parcela = MagicMock()
        parcela.id_parcela = id_parcela or uuid.uuid4()
        parcela.numero = numero
        parcela.valor = valor
        parcela.data_vencimento = data_vencimento
        parcela.status = status
        parcela.id_venda = id_venda or uuid.uuid4()
        parcela.id_empresa = uuid.uuid4()
        parcela.data_pagamento = None
        parcela.valor_pago = None
        return parcela
    
    return _create_parcela

@pytest.fixture
def create_lancamento_mock():
    """Cria um objeto lançamento mock para testes."""
    def _create_lancamento(
        id_lancamento=None,
        descricao="Lançamento teste",
        valor=Decimal("100.00"),
        tipo="receita",
        data_lancamento=date.today(),
        id_conta_bancaria=None,
        id_centro_custo=None,
    ):
        lancamento = MagicMock()
        lancamento.id_lancamento = id_lancamento or uuid.uuid4()
        lancamento.descricao = descricao
        lancamento.valor = valor
        lancamento.tipo = tipo
        lancamento.data_lancamento = data_lancamento
        lancamento.id_conta_bancaria = id_conta_bancaria or uuid.uuid4()
        lancamento.id_centro_custo = id_centro_custo or uuid.uuid4()
        lancamento.id_empresa = uuid.uuid4()
        return lancamento
    
    return _create_lancamento 