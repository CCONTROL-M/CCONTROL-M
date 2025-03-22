import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import os
import logging
from unittest.mock import patch
from uuid import uuid4

from app.main import app
from app.db.session import get_session, create_db_and_tables
from app.models.fornecedor import Fornecedor
from app.models.empresa import Empresa
from app.models.endereco import Endereco
from app.models.usuario import Usuario
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate
from app.core.security import create_access_token

# Configurar logger para testes
logger = logging.getLogger("test_integration")


@pytest.fixture(scope="module")
async def test_db():
    """Fixture para criar e disponibilizar o banco de dados de teste."""
    # Criar banco de dados de teste
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_integration.db"
    
    # Criar tabelas no banco de teste
    await create_db_and_tables()
    
    yield
    
    # Limpar após os testes
    try:
        os.remove("./test_integration.db")
    except OSError:
        pass


@pytest.fixture
async def async_session():
    """Fixture para sessão assíncrona do SQLAlchemy."""
    async for session in get_session():
        yield session


@pytest.fixture
async def async_client():
    """Fixture para cliente HTTP assíncrono."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_client(async_client, async_session):
    """Fixture para cliente HTTP autenticado."""
    # Criar usuário de teste
    usuario_id = str(uuid4())
    usuario = Usuario(
        id=usuario_id,
        email="teste@ccontrolm.com.br",
        username="teste",
        hashed_password="$2b$12$TZ6Fk5WM0vlZ3GoS4Foqae6zq5Zs3S/uKIJDz5TkVQrQR6MXKcd9W",  # senha123
        is_active=True,
        is_superuser=True
    )
    
    # Criar empresa de teste
    empresa_id = str(uuid4())
    empresa = Empresa(
        id=empresa_id,
        nome="Empresa Teste",
        cnpj="12345678901234",
        telefone="47999999999",
        email="empresa@teste.com",
        is_active=True,
        usuario_id=usuario_id
    )
    
    # Salvar no banco
    async_session.add(usuario)
    async_session.add(empresa)
    await async_session.commit()
    
    # Criar token de acesso
    token = create_access_token(
        data={"sub": usuario.email, "empresa_id": empresa.id, "user_id": usuario.id}
    )
    
    # Configurar cabeçalho de autorização
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    
    yield async_client, usuario, empresa


@pytest.mark.asyncio
async def test_criar_fornecedor_db(authenticated_client, async_session, test_db):
    """Testa a criação de um fornecedor integrado com banco de dados."""
    client, usuario, empresa = authenticated_client
    
    # Dados para o teste
    fornecedor_data = {
        "nome": "Fornecedor Teste",
        "email": "fornecedor@teste.com",
        "telefone": "47999999999",
        "cnpj": "12345678901234",
        "inscricao_estadual": "123456789",
        "contato": "Contato Teste",
        "observacoes": "Observações de teste",
        "endereco": {
            "cep": "89010100",
            "logradouro": "Rua Teste",
            "numero": "123",
            "complemento": "Sala 1",
            "bairro": "Bairro Teste",
            "cidade": "Cidade Teste",
            "estado": "SC"
        }
    }
    
    # Fazer requisição para criar fornecedor
    response = await client.post(
        "/api/v1/fornecedores",
        json=fornecedor_data
    )
    
    # Verificar resposta
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == fornecedor_data["nome"]
    assert data["email"] == fornecedor_data["email"]
    assert data["empresa_id"] == empresa.id
    
    # Verificar se o fornecedor foi salvo no banco
    fornecedor_id = data["id"]
    db_fornecedor = await async_session.get(Fornecedor, fornecedor_id)
    
    assert db_fornecedor is not None
    assert db_fornecedor.nome == fornecedor_data["nome"]
    assert db_fornecedor.email == fornecedor_data["email"]
    assert db_fornecedor.empresa_id == empresa.id
    
    # Verificar se o endereço foi salvo corretamente
    endereco = await async_session.get(Endereco, db_fornecedor.endereco_id)
    assert endereco is not None
    assert endereco.logradouro == fornecedor_data["endereco"]["logradouro"]
    assert endereco.cidade == fornecedor_data["endereco"]["cidade"]


@pytest.mark.asyncio
async def test_listar_fornecedores_db(authenticated_client, async_session, test_db):
    """Testa a listagem de fornecedores integrada com banco de dados."""
    client, usuario, empresa = authenticated_client
    
    # Criar alguns fornecedores adicionais para teste
    for i in range(3):
        fornecedor = Fornecedor(
            id=str(uuid4()),
            nome=f"Fornecedor Teste {i}",
            email=f"fornecedor{i}@teste.com",
            telefone=f"479999999{i}",
            cnpj=f"1234567890123{i}",
            empresa_id=empresa.id,
            usuario_id=usuario.id
        )
        async_session.add(fornecedor)
    
    await async_session.commit()
    
    # Fazer requisição para listar fornecedores
    response = await client.get("/api/v1/fornecedores")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    
    # Deve haver pelo menos os 3 fornecedores criados + o do teste anterior
    assert len(data["items"]) >= 4
    assert data["total"] >= 4


@pytest.mark.asyncio
async def test_atualizar_fornecedor_db(authenticated_client, async_session, test_db):
    """Testa a atualização de um fornecedor integrado com banco de dados."""
    client, usuario, empresa = authenticated_client
    
    # Criar um fornecedor para atualizar
    fornecedor_id = str(uuid4())
    fornecedor = Fornecedor(
        id=fornecedor_id,
        nome="Fornecedor para Atualizar",
        email="atualizar@teste.com",
        telefone="47988888888",
        cnpj="98765432109876",
        empresa_id=empresa.id,
        usuario_id=usuario.id
    )
    async_session.add(fornecedor)
    await async_session.commit()
    
    # Dados para atualização
    update_data = {
        "nome": "Fornecedor Atualizado",
        "email": "atualizado@teste.com",
        "observacoes": "Observações atualizadas"
    }
    
    # Fazer requisição para atualizar fornecedor
    response = await client.patch(
        f"/api/v1/fornecedores/{fornecedor_id}",
        json=update_data
    )
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == update_data["nome"]
    assert data["email"] == update_data["email"]
    assert data["observacoes"] == update_data["observacoes"]
    
    # Verificar se o fornecedor foi atualizado no banco
    await async_session.refresh(fornecedor)
    assert fornecedor.nome == update_data["nome"]
    assert fornecedor.email == update_data["email"]
    assert fornecedor.observacoes == update_data["observacoes"]


@pytest.mark.asyncio
async def test_excluir_fornecedor_db(authenticated_client, async_session, test_db):
    """Testa a exclusão de um fornecedor integrado com banco de dados."""
    client, usuario, empresa = authenticated_client
    
    # Criar um fornecedor para excluir
    fornecedor_id = str(uuid4())
    fornecedor = Fornecedor(
        id=fornecedor_id,
        nome="Fornecedor para Excluir",
        email="excluir@teste.com",
        telefone="47977777777",
        cnpj="56789012345678",
        empresa_id=empresa.id,
        usuario_id=usuario.id
    )
    async_session.add(fornecedor)
    await async_session.commit()
    
    # Fazer requisição para excluir fornecedor
    response = await client.delete(f"/api/v1/fornecedores/{fornecedor_id}")
    
    # Verificar resposta
    assert response.status_code == 204
    
    # Verificar se o fornecedor foi marcado como inativo no banco
    await async_session.refresh(fornecedor)
    assert fornecedor.is_active == False 