import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
import json
from typing import Callable, AsyncGenerator

from app.main import app
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.repositories.usuario_repository import UsuarioRepository
from app.dependencies import get_current_user, check_permission
from app.database import get_db
from app.services.auth import get_password_hash
from tests.conftest import override_get_db
from app.services.usuario_service import UsuarioService
from app.services.auditoria_service import AuditoriaService

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

@pytest.mark.asyncio
async def test_criar_usuario(
    session: AsyncSession,
    usuario_factory: Callable[..., AsyncGenerator[Usuario, None]]
):
    """Teste de criação de usuário."""
    # Arrange
    nome = "Usuário Teste"
    email = "usuario@teste.com"
    senha = "Senha@123"
    
    # Act
    usuario = await usuario_factory(
        nome=nome,
        email=email,
        senha=senha
    )
    
    # Assert
    assert usuario.id_usuario is not None
    assert usuario.nome == nome
    assert usuario.email == email
    assert usuario.senha != senha  # Senha deve estar hasheada
    assert usuario.ativo is True

@pytest.mark.asyncio
async def test_atualizar_usuario(
    session: AsyncSession,
    usuario: Usuario
):
    """Teste de atualização de usuário."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    novo_nome = "Usuário Atualizado"
    novo_email = "atualizado@teste.com"
    
    usuario_update = UsuarioUpdate(
        nome=novo_nome,
        email=novo_email
    )
    
    # Act
    usuario_atualizado = await service.update(
        usuario.id_usuario,
        usuario_update
    )
    
    # Assert
    assert usuario_atualizado.id_usuario == usuario.id_usuario
    assert usuario_atualizado.nome == novo_nome
    assert usuario_atualizado.email == novo_email

@pytest.mark.asyncio
async def test_buscar_usuario(
    session: AsyncSession,
    usuario: Usuario
):
    """Teste de busca de usuário por ID."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    usuario_encontrado = await service.get_by_id(usuario.id_usuario)
    
    # Assert
    assert usuario_encontrado is not None
    assert usuario_encontrado.id_usuario == usuario.id_usuario
    assert usuario_encontrado.nome == usuario.nome
    assert usuario_encontrado.email == usuario.email

@pytest.mark.asyncio
async def test_listar_usuarios(
    session: AsyncSession,
    usuarios_lista: list[Usuario]
):
    """Teste de listagem de usuários."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    resultado = await service.get_multi(
        skip=0,
        limit=10
    )
    
    # Assert
    assert resultado.total == 5
    assert len(resultado.items) == 5
    assert resultado.page == 1

@pytest.mark.asyncio
async def test_buscar_usuario_por_email(
    session: AsyncSession,
    usuario: Usuario
):
    """Teste de busca de usuário por email."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    usuario_encontrado = await service.get_by_email(usuario.email)
    
    # Assert
    assert usuario_encontrado is not None
    assert usuario_encontrado.id_usuario == usuario.id_usuario
    assert usuario_encontrado.email == usuario.email

@pytest.mark.asyncio
async def test_autenticar_usuario(
    session: AsyncSession,
    usuario_factory: Callable[..., AsyncGenerator[Usuario, None]]
):
    """Teste de autenticação de usuário."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    email = "auth@teste.com"
    senha = "Senha@123"
    usuario = await usuario_factory(
        email=email,
        senha=senha
    )
    
    # Act
    usuario_autenticado = await service.authenticate(email, senha)
    
    # Assert
    assert usuario_autenticado is not None
    assert usuario_autenticado.id_usuario == usuario.id_usuario
    assert usuario_autenticado.email == email

@pytest.mark.asyncio
async def test_alterar_senha(
    session: AsyncSession,
    usuario: Usuario
):
    """Teste de alteração de senha."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    nova_senha = "NovaSenha@123"
    
    # Act
    usuario_atualizado = await service.change_password(
        usuario.id_usuario,
        nova_senha
    )
    
    # Assert
    assert usuario_atualizado.id_usuario == usuario.id_usuario
    assert usuario_atualizado.senha != nova_senha  # Senha deve estar hasheada
    assert usuario_atualizado.senha != usuario.senha  # Senha deve ser diferente da anterior

@pytest.mark.asyncio
async def test_desativar_usuario(
    session: AsyncSession,
    usuario: Usuario
):
    """Teste de desativação de usuário."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    usuario_desativado = await service.deactivate(usuario.id_usuario)
    
    # Assert
    assert usuario_desativado.id_usuario == usuario.id_usuario
    assert usuario_desativado.ativo is False

@pytest.mark.asyncio
async def test_erro_ao_criar_usuario_email_duplicado(
    session: AsyncSession,
    usuario: Usuario,
    usuario_factory: Callable[..., AsyncGenerator[Usuario, None]]
):
    """Teste de erro ao criar usuário com email duplicado."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await usuario_factory(email=usuario.email)
    assert excinfo.value.status_code == 400
    assert "já cadastrado" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_erro_ao_autenticar_usuario_senha_invalida(
    session: AsyncSession,
    usuario: Usuario
):
    """Teste de erro ao autenticar usuário com senha inválida."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.authenticate(usuario.email, "senha_errada")
    assert excinfo.value.status_code == 401
    assert "inválidos" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_erro_ao_autenticar_usuario_inativo(
    session: AsyncSession,
    usuario_factory: Callable[..., AsyncGenerator[Usuario, None]]
):
    """Teste de erro ao autenticar usuário inativo."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    email = "inativo@teste.com"
    senha = "Senha@123"
    usuario = await usuario_factory(
        email=email,
        senha=senha,
        ativo=False
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.authenticate(email, senha)
    assert excinfo.value.status_code == 401
    assert "inativo" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_erro_ao_buscar_usuario_inexistente(session: AsyncSession):
    """Teste de erro ao buscar usuário inexistente."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_by_id(uuid4())
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail)

@pytest.mark.asyncio
async def test_erro_ao_atualizar_usuario_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar usuário inexistente."""
    # Arrange
    service = UsuarioService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    usuario_update = UsuarioUpdate(nome="Teste")
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.update(uuid4(), usuario_update)
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail)

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