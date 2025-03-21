import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
import json

from app.main import app
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from app.repositories.usuario_repository import UsuarioRepository
from app.dependencies import get_current_user, check_permission
from app.database import get_db
from app.services.auth import get_password_hash
from tests.conftest import override_get_db

# Cliente de teste
client = TestClient(app)

# Mock de usuário autenticado para os testes (superadmin)
test_superadmin = {
    "id_usuario": "12345678-1234-5678-1234-567812345678",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Admin Teste",
    "email": "admin@exemplo.com",
    "tipo_usuario": "superadmin",
    "telas_permitidas": {"usuarios": True, "empresas": True}
}

# Mock de usuário comum para os testes (acesso limitado)
test_user = {
    "id_usuario": "87654321-8765-4321-8765-432187654321",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Usuário Teste",
    "email": "usuario@exemplo.com",
    "tipo_usuario": "adm",
    "telas_permitidas": {"usuarios": False}
}

# Fixture para criar um usuário de teste
@pytest.fixture
def usuario_teste(db_session: Session):
    # Dados para o usuário de teste
    senha_hash = get_password_hash("senha123")
    usuario_data = UsuarioCreate(
        id_empresa="98765432-9876-5432-9876-543298765432",
        nome="Usuário Teste",
        email="teste_usuario@exemplo.com",
        senha="senha123",
        tipo_usuario="operador",
        telas_permitidas={"vendas": True, "clientes": True}
    )
    
    # Criar usuário diretamente no banco para evitar hash duplo da senha
    db_usuario = Usuario(
        id_usuario=uuid4(),
        id_empresa=usuario_data.id_empresa,
        nome=usuario_data.nome,
        email=usuario_data.email,
        senha_hash=senha_hash,
        tipo_usuario=usuario_data.tipo_usuario,
        telas_permitidas=usuario_data.telas_permitidas,
        ativo=True
    )
    
    db_session.add(db_usuario)
    db_session.commit()
    db_session.refresh(db_usuario)
    
    yield db_usuario
    
    # Limpar após o teste
    db_session.query(Usuario).filter(Usuario.id_usuario == db_usuario.id_usuario).delete()
    db_session.commit()

# Testes para autenticação
def test_login_correto():
    """Teste de login com credenciais corretas"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    
    # Dados de login
    login_data = {
        "username": "teste_usuario@exemplo.com",
        "password": "senha123"
    }
    
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_login_incorreto():
    """Teste de login com credenciais incorretas"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    
    # Dados de login incorretos
    login_data = {
        "username": "teste_usuario@exemplo.com",
        "password": "senha_errada"
    }
    
    response = client.post("/token", data=login_data)
    assert response.status_code == 401
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

# Testes para CRUD de usuários
def test_obter_perfil():
    """Teste para obter o perfil do usuário logado"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_user
    
    response = client.get("/me")
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["id_usuario"] == test_user["id_usuario"]
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_listar_usuarios():
    """Teste para listar usuários (como superadmin)"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("usuarios")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.get("/usuarios")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_listar_usuarios_sem_permissao():
    """Teste para listar usuários sem permissão"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[check_permission("usuarios")] = lambda: test_user
    app.dependency_overrides[get_db] = override_get_db
    
    response = client.get("/usuarios")
    assert response.status_code == 403
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_criar_usuario():
    """Teste para criar um novo usuário"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("usuarios")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    # Dados para o novo usuário
    novo_usuario = {
        "id_empresa": "98765432-9876-5432-9876-543298765432",
        "nome": "Novo Usuário",
        "email": "novo_usuario@exemplo.com",
        "senha": "senha123",
        "tipo_usuario": "operador",
        "telas_permitidas": {"vendas": True, "clientes": True},
        "ativo": True
    }
    
    response = client.post("/usuarios", json=novo_usuario)
    assert response.status_code == 201
    
    data = response.json()
    assert data["nome"] == novo_usuario["nome"]
    assert data["email"] == novo_usuario["email"]
    assert "senha" not in data  # Garantir que a senha não é retornada
    assert data["tipo_usuario"] == novo_usuario["tipo_usuario"]
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_atualizar_usuario(usuario_teste):
    """Teste para atualizar um usuário existente"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("usuarios")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    # Dados para atualização
    usuario_atualizado = {
        "nome": "Nome Atualizado",
        "tipo_usuario": "adm",
        "telas_permitidas": {"vendas": True, "clientes": True, "lancamentos": True}
    }
    
    usuario_id = str(usuario_teste.id_usuario)
    response = client.put(f"/usuarios/{usuario_id}", json=usuario_atualizado)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == usuario_atualizado["nome"]
    assert data["tipo_usuario"] == usuario_atualizado["tipo_usuario"]
    assert "lancamentos" in data["telas_permitidas"]
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep

def test_excluir_usuario(usuario_teste):
    """Teste para excluir um usuário"""
    # Sobreescrever a dependência para este teste
    original_dep = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_superadmin
    app.dependency_overrides[check_permission("usuarios")] = lambda: test_superadmin
    app.dependency_overrides[get_db] = override_get_db
    
    usuario_id = str(usuario_teste.id_usuario)
    response = client.delete(f"/usuarios/{usuario_id}")
    assert response.status_code == 204
    
    # Verificar se o usuário foi excluído
    response = client.get(f"/usuarios/{usuario_id}")
    assert response.status_code == 404
    
    # Restaurar dependências originais
    app.dependency_overrides = original_dep 