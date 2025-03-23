"""
Módulo de configuração do banco de dados para o CCONTROL-M.

Este módulo fornece a configuração e utilitários para interação com o banco de dados
PostgreSQL usando SQLAlchemy 2.0 e é compatível com Supabase.
"""
from contextlib import asynccontextmanager, contextmanager
from typing import Generator, Any, AsyncGenerator
import logging

from sqlalchemy import create_engine, Engine, URL, event
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config.settings import settings
from app.middlewares.tenant_middleware import get_tenant_id

# Configurar logger
logger = logging.getLogger(__name__)

# Criar classe base para modelos
Base = declarative_base()

# Criar engine síncrona para compatibilidade
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Criar engine assíncrona
# Verificar o tipo de banco de dados para usar o driver correto
if settings.DATABASE_URL.startswith(('postgresql', 'postgres')):
    async_db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif settings.DATABASE_URL.startswith('sqlite'):
    # Para SQLite, usamos aiosqlite como driver assíncrono
    async_db_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    # Default para outros bancos de dados
    async_db_url = settings.DATABASE_URL

async_engine = create_async_engine(
    async_db_url,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Configuração da sessão local síncrona
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuração da sessão local assíncrona
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependência para injeção da sessão do banco de dados em rotas FastAPI.
    
    Yields:
        Session: Sessão do SQLAlchemy.
        
    Example:
        ```python
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(models.Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência para injeção da sessão assíncrona do banco de dados em rotas FastAPI.
    
    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy.
        
    Example:
        ```python
        @app.get("/items/")
        async def read_items(session: AsyncSession = Depends(get_async_session)):
            result = await session.execute(select(models.Item))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager para utilização da sessão síncrona do banco de dados fora do contexto FastAPI.
    
    Yields:
        Session: Sessão do SQLAlchemy.
        
    Example:
        ```python
        with db_session() as session:
            results = session.query(models.User).all()
        ```
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def db_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager para utilização da sessão assíncrona do banco de dados fora do contexto FastAPI.
    
    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy.
        
    Example:
        ```python
        async with db_async_session() as session:
            result = await session.execute(select(models.User))
            users = result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_all_tables() -> None:
    """
    Cria todas as tabelas definidas nos modelos que herdam de Base.
    
    Esta função deve ser chamada durante a inicialização da aplicação
    ou em scripts de migração quando necessário.
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    ⚠️ PERIGO: Remove todas as tabelas do banco de dados.
    
    Esta função só deve ser usada em ambientes de teste ou desenvolvimento,
    nunca em produção.
    """
    Base.metadata.drop_all(bind=engine)


# Configuração de listeners de conexão (opcional)
@event.listens_for(engine, "connect")
def set_connection_defaults(dbapi_connection, connection_record: Any) -> None:
    """Define configurações padrão para cada nova conexão."""
    # Verifica se o banco de dados é PostgreSQL antes de executar comandos específicos
    if settings.DATABASE_URL.startswith(('postgresql', 'postgres')):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET timezone='UTC'")
        cursor.close()

# Eventos SQLAlchemy
@event.listens_for(SessionLocal, "after_begin")
def receive_after_begin(session, transaction, connection):
    """
    Evento disparado após o início de uma transação.
    Configura as variáveis de sessão para RLS no Supabase.
    """
    # Não executar para SQLite
    if not settings.DATABASE_URL.startswith('sqlite'):
        # Obter ID do tenant do contexto atual
        tenant_id = get_tenant_id()
        
        if tenant_id:
            # Definir variável de sessão PostgreSQL para tenant_id
            # Supabase utiliza 'app.current_tenant' como variável de sessão padrão
            connection.execute(f"SET app.current_tenant = '{tenant_id}'")
            logger.debug(f"Definindo tenant_id da sessão Supabase: {tenant_id}")
        else:
            # Se não houver tenant_id, definir como null
            # Isso garantirá que políticas RLS bloquearão o acesso
            connection.execute("SET app.current_tenant = NULL")
            logger.debug("Tenant_id não disponível, definindo como NULL") 