"""
Módulo de configuração do banco de dados para o CCONTROL-M.

Este módulo fornece a configuração e utilitários para interação com o banco de dados
PostgreSQL usando SQLAlchemy 2.0 e é compatível com Supabase.
"""
from contextlib import contextmanager
from typing import Generator, Any

from sqlalchemy import create_engine, Engine, URL, event
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool

from app.config.settings import settings


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos do SQLAlchemy."""
    pass


# Criação da engine do SQLAlchemy com as configurações adequadas
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={"options": "-c client_encoding=ASCII"},
    client_encoding="ASCII",
    echo=settings.DEBUG,
)

# Configuração da sessão local que será usada para acessar o banco de dados
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
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


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager para utilização da sessão do banco de dados fora do contexto FastAPI.
    
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
    cursor = dbapi_connection.cursor()
    cursor.execute("SET timezone='UTC'")
    cursor.close() 