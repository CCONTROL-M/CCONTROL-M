import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.main import app
from app.models.empresa import Empresa
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.empresa import EmpresaCreate
from app.dependencies import get_current_user, check_permission
from app.database import get_db
from tests.conftest import override_get_db

# Cliente de teste
client = TestClient(app)

# Mock de usuário superadmin para os testes
test_superadmin = {
    "id_usuario": "12345678-1234-5678-1234-567812345678",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Admin Teste",
    "email": "admin@exemplo.com",
    "tipo_usuario": "superadmin",
    "telas_permitidas": {"empresas": True}
}

# Mock de usuário comum para os testes (acesso limitado)
test_user = {
    "id_usuario": "87654321-8765-4321-8765-432187654321",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Usuário Teste",
    "email": "usuario@exemplo.com",
    "tipo_usuario": "adm",
    "telas_permitidas": {"empresas": True}
}

# Fixture para criar uma empresa de teste
@pytest.fixture
def empresa_teste(db_session: Session):
    # Criar empresa de teste
    empresa_data = EmpresaCreate(
        nome="Empresa Teste",
        nome_fantasia="Fantasia Teste",
        cnpj="12345678901234",
        email="empresa@teste.com",
        telefone="99999999999",
        endereco="Rua Teste, 123",
        cidade="Cidade Teste",
        estado="UF",
        cep="12345000",
        ativo=True
    )
    
    # Criar empresa diretamente no banco
    db_empresa = Empresa(
        id_empresa=uuid4(),
        nome=empresa_data.nome,
        nome_fantasia=empresa_data.nome_fantasia,
        cnpj=empresa_data.cnpj,
        email=empresa_data.email,
        telefone=empresa_data.telefone,
        endereco=empresa_data.endereco,
        cidade=empresa_data.cidade,
        estado=empresa_data.estado,
        cep=empresa_data.cep,
        ativo=empresa_data.ativo,
        configuracoes={"timezone": "America/Sao_Paulo"}
    )
    
    db_session.add(db_empresa)
    db_session.commit()
    db_session.refresh(db_empresa)
    
    yield db_empresa
    
    # Limpar após o teste
    db_session.query(Empresa).filter(Empresa.id_empresa == db_empresa.id_empresa).delete()
    db_session.commit()

# Testes para CRUD de empresas
def test_listar_empresas_superadmin():
    """Teste para listar empresas como superadmin"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("empresas")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.get("/empresas")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_listar_empresas_usuario_comum():
    """Teste para listar empresas como usuário comum (deve ver apenas sua própria empresa)"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[check_permission("empresas")] = lambda: test_user
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.get("/empresas")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1  # Deve ver apenas sua própria empresa
    assert data[0]["id_empresa"] == test_user["id_empresa"]
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_obter_empresa(empresa_teste):
    """Teste para obter uma empresa específica"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("empresas")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    empresa_id = str(empresa_teste.id_empresa)
    response = client.get(f"/empresas/{empresa_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == empresa_teste.nome
    assert data["cnpj"] == empresa_teste.cnpj
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_obter_empresa_outra_empresa():
    """Teste para obter uma empresa que não é a do usuário (deve falhar)"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[check_permission("empresas")] = lambda: test_user
    app.dependency_overrides[get_db] = override_get_db
    
    # UUID de outra empresa
    outro_id = "11111111-1111-1111-1111-111111111111"
    
    response = client.get(f"/empresas/{outro_id}")
    assert response.status_code == 403  # Acesso negado
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_criar_empresa():
    """Teste para criar uma nova empresa"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("empresas")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    # Dados para a nova empresa
    nova_empresa = {
        "nome": "Nova Empresa Teste",
        "nome_fantasia": "Nova Fantasia",
        "cnpj": "98765432109876",
        "email": "nova@empresa.com",
        "telefone": "88888888888",
        "endereco": "Rua Nova, 456",
        "cidade": "Nova Cidade",
        "estado": "NC",
        "cep": "54321000",
        "ativo": True
    }
    
    response = client.post("/empresas", json=nova_empresa)
    assert response.status_code == 201
    
    data = response.json()
    assert data["nome"] == nova_empresa["nome"]
    assert data["cnpj"] == nova_empresa["cnpj"]
    assert "id_empresa" in data
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_atualizar_empresa(empresa_teste):
    """Teste para atualizar uma empresa existente"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("empresas")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    # Dados para atualização
    empresa_atualizada = {
        "nome": "Empresa Atualizada",
        "telefone": "77777777777",
        "endereco": "Rua Atualizada, 789"
    }
    
    empresa_id = str(empresa_teste.id_empresa)
    response = client.put(f"/empresas/{empresa_id}", json=empresa_atualizada)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == empresa_atualizada["nome"]
    assert data["telefone"] == empresa_atualizada["telefone"]
    assert data["endereco"] == empresa_atualizada["endereco"]
    assert data["cnpj"] == empresa_teste.cnpj  # Campo não alterado
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_excluir_empresa(empresa_teste):
    """Teste para excluir uma empresa"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("empresas")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    empresa_id = str(empresa_teste.id_empresa)
    response = client.delete(f"/empresas/{empresa_id}")
    assert response.status_code == 204
    
    # Verificar se a empresa foi excluída
    response = client.get(f"/empresas/{empresa_id}")
    assert response.status_code == 404
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_multi_tenant_isolamento():
    """Teste para verificar isolamento multi-tenant (uma empresa não pode acessar dados de outra)"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    
    # Usuário da empresa A
    usuario_empresa_a = {
        "id_usuario": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "id_empresa": "11111111-1111-1111-1111-111111111111",
        "nome": "Usuário Empresa A",
        "email": "usuario_a@exemplo.com",
        "tipo_usuario": "adm",
        "telas_permitidas": {"empresas": True, "clientes": True}
    }
    
    # Usuário da empresa B
    usuario_empresa_b = {
        "id_usuario": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "id_empresa": "22222222-2222-2222-2222-222222222222",
        "nome": "Usuário Empresa B",
        "email": "usuario_b@exemplo.com",
        "tipo_usuario": "adm",
        "telas_permitidas": {"empresas": True, "clientes": True}
    }
    
    # Testar acesso à própria empresa
    app.dependency_overrides[get_current_user] = lambda: usuario_empresa_a
    app.dependency_overrides[check_permission("empresas")] = lambda: usuario_empresa_a
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.get("/empresas")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_empresa"] == usuario_empresa_a["id_empresa"]
    
    # Testar tentativa de acesso a outra empresa
    app.dependency_overrides[get_current_user] = lambda: usuario_empresa_a
    
    response = client.get(f"/empresas/{usuario_empresa_b['id_empresa']}")
    assert response.status_code == 403  # Acesso negado
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep 