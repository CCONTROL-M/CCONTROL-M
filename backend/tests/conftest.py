import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from app.database import Base, get_db
from app.dependencies import get_current_active_user

# Conexão de teste com banco de dados
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "ccontrolm", "ccontrolm_test"
)

# Criar engine para testes
test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "client_encoding": 'ASCII',
        "options": "-c client_encoding=ASCII"
    },
)

# Criar fábrica de sessões para testes
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def db_engine():
    # Criar tabelas no banco de dados de teste
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    # Remover tabelas ao finalizar os testes
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(db_engine):
    # Criar sessão para teste
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    # Limpar após o teste
    session.close()
    transaction.rollback()
    connection.close()

# Mock para substituir a dependência de get_db
def override_get_db():
    """Substitui a dependência de conexão com o banco durante os testes"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Mock para substituir a dependência de usuário autenticado
def override_get_current_active_user():
    """Substitui a dependência de autenticação durante os testes"""
    return {
        "id_usuario": "12345678-1234-5678-1234-567812345678",
        "id_empresa": "98765432-9876-5432-9876-543298765432",
        "nome": "Teste Usuário",
        "email": "teste@exemplo.com",
        "tipo_usuario": "adm",
        "telas_permitidas": {
            "produtos": True,
            "categorias": True,
            "formas_pagamento": True,
            "contas_bancarias": True,
            "lancamentos": True,
            "clientes": True,
            "fornecedores": True,
            "vendas": True,
            "centro_custos": True
        }
    } 