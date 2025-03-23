"""Testes para o serviço de permissões."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.permissao import Permissao
from app.models.permissao_usuario import PermissaoUsuario
from app.models.usuario import Usuario
from app.schemas.permissao import PermissaoCreate, PermissaoUpdate
from app.services.permissao_service import PermissaoService

# Fixtures - definição de dados para testes
@pytest.fixture
async def usuario(session: AsyncSession) -> Usuario:
    """Cria um usuário para testes."""
    # Criar um usuário diretamente no banco
    usuario = Usuario(
        id=uuid4(),
        nome="Usuário Teste",
        email="usuario@teste.com",
        senha_hash="senha_hash_teste",
        ativo=True,
        admin=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    
    return usuario

@pytest.fixture
async def permissao(session: AsyncSession) -> Permissao:
    """Cria uma permissão para testes."""
    # Criar uma permissão diretamente no banco
    permissao = Permissao(
        id=uuid4(),
        nome="permissao_teste",
        descricao="Permissão para testes",
        modulo="teste",
        recurso="teste",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(permissao)
    await session.commit()
    await session.refresh(permissao)
    
    return permissao

@pytest.fixture
async def permissao_usuario(session: AsyncSession, usuario: Usuario, permissao: Permissao) -> PermissaoUsuario:
    """Cria uma associação entre permissão e usuário para testes."""
    # Criar uma permissão de usuário
    permissao_usuario = PermissaoUsuario(
        id=uuid4(),
        usuario_id=usuario.id,
        permissao_id=permissao.id,
        empresa_id=uuid4(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(permissao_usuario)
    await session.commit()
    await session.refresh(permissao_usuario)
    
    return permissao_usuario

@pytest.fixture
async def permissao_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[Permissao, None]]:
    """Factory para criar permissões com parâmetros customizados."""
    async def _create_permissao(**kwargs) -> Permissao:
        # Valores padrão para testes
        defaults = {
            "id": uuid4(),
            "nome": f"permissao_{uuid4().hex[:8]}",
            "descricao": "Permissão para testes",
            "modulo": "teste",
            "recurso": "teste",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        permissao = Permissao(**defaults)
        session.add(permissao)
        await session.commit()
        await session.refresh(permissao)
        
        return permissao
    
    return _create_permissao

@pytest.fixture
async def permissoes_lista(session: AsyncSession, permissao_factory) -> list[Permissao]:
    """Cria uma lista de permissões para testes."""
    
    # Criar permissões para diferentes módulos
    permissoes = []
    
    # Módulos e recursos para teste
    modulos_recursos = [
        ("usuarios", "listar"),
        ("usuarios", "criar"),
        ("clientes", "listar"),
        ("clientes", "criar"),
        ("vendas", "listar")
    ]
    
    for i, (modulo, recurso) in enumerate(modulos_recursos):
        permissao = await permissao_factory(
            nome=f"permissao_{modulo}_{recurso}",
            descricao=f"Permissão para {recurso} {modulo}",
            modulo=modulo,
            recurso=recurso
        )
        
        permissoes.append(permissao)
    
    return permissoes


# Testes do serviço de permissões
@pytest.mark.asyncio
async def test_criar_permissao(session: AsyncSession):
    """Teste de criação de permissão."""
    # Arrange
    service = PermissaoService(session)
    
    dados_permissao = {
        "nome": "nova_permissao",
        "descricao": "Nova permissão para teste",
        "modulo": "teste",
        "recurso": "novo"
    }
    
    permissao_create = PermissaoCreate(**dados_permissao)
    
    # Act
    permissao = await service.create(permissao_create)
    
    # Assert
    assert permissao is not None
    assert permissao.id is not None
    assert permissao.nome == "nova_permissao"
    assert permissao.descricao == "Nova permissão para teste"
    assert permissao.modulo == "teste"
    assert permissao.recurso == "novo"


@pytest.mark.asyncio
async def test_buscar_permissao(session: AsyncSession, permissao: Permissao):
    """Teste de busca de permissão pelo ID."""
    # Arrange
    service = PermissaoService(session)
    
    # Act
    result = await service.get(permissao.id)
    
    # Assert
    assert result is not None
    assert result.id == permissao.id
    assert result.nome == permissao.nome
    assert result.descricao == permissao.descricao


@pytest.mark.asyncio
async def test_buscar_permissao_por_nome(session: AsyncSession, permissao: Permissao):
    """Teste de busca de permissão pelo nome."""
    # Arrange
    service = PermissaoService(session)
    
    # Act
    result = await service.get_by_nome(permissao.nome)
    
    # Assert
    assert result is not None
    assert result.id == permissao.id
    assert result.nome == permissao.nome


@pytest.mark.asyncio
async def test_listar_permissoes(session: AsyncSession, permissoes_lista: list[Permissao]):
    """Teste de listagem de permissões."""
    # Arrange
    service = PermissaoService(session)
    
    # Act
    result, total = await service.list(
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 5
    assert total == 5


@pytest.mark.asyncio
async def test_listar_permissoes_por_modulo(session: AsyncSession, permissoes_lista: list[Permissao]):
    """Teste de listagem de permissões por módulo."""
    # Arrange
    service = PermissaoService(session)
    
    # Act
    result, total = await service.list(
        modulo="usuarios",
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 2
    assert total == 2
    assert all(p.modulo == "usuarios" for p in result)


@pytest.mark.asyncio
async def test_atualizar_permissao(session: AsyncSession, permissao: Permissao):
    """Teste de atualização de permissão."""
    # Arrange
    service = PermissaoService(session)
    
    dados_atualizacao = {
        "descricao": "Descrição atualizada para teste",
        "modulo": "teste_atualizado"
    }
    
    permissao_update = PermissaoUpdate(**dados_atualizacao)
    
    # Act
    result = await service.update(
        id_permissao=permissao.id,
        permissao=permissao_update
    )
    
    # Assert
    assert result is not None
    assert result.id == permissao.id
    assert result.descricao == "Descrição atualizada para teste"
    assert result.modulo == "teste_atualizado"
    # O nome não deve ser alterado
    assert result.nome == permissao.nome


@pytest.mark.asyncio
async def test_verificar_permissao_usuario(session: AsyncSession, permissao_usuario: PermissaoUsuario):
    """Teste de verificação de permissão de usuário."""
    # Arrange
    service = PermissaoService(session)
    usuario_id = permissao_usuario.usuario_id
    empresa_id = permissao_usuario.empresa_id
    
    # Act
    result = await service.verificar_permissao(
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        modulo=permissao_usuario.permissao.modulo,
        recurso=permissao_usuario.permissao.recurso
    )
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_verificar_permissao_usuario_sem_acesso(session: AsyncSession, usuario: Usuario):
    """Teste de verificação de permissão para usuário sem acesso."""
    # Arrange
    service = PermissaoService(session)
    empresa_id = uuid4()
    
    # Act
    result = await service.verificar_permissao(
        usuario_id=usuario.id,
        empresa_id=empresa_id,
        modulo="teste",
        recurso="teste"
    )
    
    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_atribuir_permissao(session: AsyncSession, usuario: Usuario, permissao: Permissao):
    """Teste de atribuição de permissão a usuário."""
    # Arrange
    service = PermissaoService(session)
    empresa_id = uuid4()
    
    # Act
    result = await service.atribuir_permissao(
        usuario_id=usuario.id,
        permissao_id=permissao.id,
        empresa_id=empresa_id
    )
    
    # Assert
    assert result is not None
    assert result.usuario_id == usuario.id
    assert result.permissao_id == permissao.id
    assert result.empresa_id == empresa_id


@pytest.mark.asyncio
async def test_remover_permissao(session: AsyncSession, permissao_usuario: PermissaoUsuario):
    """Teste de remoção de permissão de usuário."""
    # Arrange
    service = PermissaoService(session)
    usuario_id = permissao_usuario.usuario_id
    permissao_id = permissao_usuario.permissao_id
    empresa_id = permissao_usuario.empresa_id
    
    # Act
    result = await service.remover_permissao(
        usuario_id=usuario_id,
        permissao_id=permissao_id,
        empresa_id=empresa_id
    )
    
    # Assert
    assert result is True
    
    # Verificar se a permissão foi realmente removida
    verificacao = await service.verificar_permissao(
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        modulo=permissao_usuario.permissao.modulo,
        recurso=permissao_usuario.permissao.recurso
    )
    
    assert verificacao is False


@pytest.mark.asyncio
async def test_listar_permissoes_usuario(session: AsyncSession, permissao_usuario: PermissaoUsuario):
    """Teste de listagem de permissões de um usuário."""
    # Arrange
    service = PermissaoService(session)
    usuario_id = permissao_usuario.usuario_id
    empresa_id = permissao_usuario.empresa_id
    
    # Act
    result = await service.listar_permissoes_usuario(
        usuario_id=usuario_id,
        empresa_id=empresa_id
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].id == permissao_usuario.permissao_id
    assert result[0].modulo == permissao_usuario.permissao.modulo
    assert result[0].recurso == permissao_usuario.permissao.recurso


@pytest.mark.asyncio
async def test_erro_ao_buscar_permissao_inexistente(session: AsyncSession):
    """Teste de erro ao buscar permissão inexistente."""
    # Arrange
    service = PermissaoService(session)
    id_inexistente = uuid4()
    
    # Act
    result = await service.get(id_inexistente)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_erro_ao_buscar_permissao_por_nome_inexistente(session: AsyncSession):
    """Teste de erro ao buscar permissão por nome inexistente."""
    # Arrange
    service = PermissaoService(session)
    nome_inexistente = f"permissao_inexistente_{uuid4().hex}"
    
    # Act
    result = await service.get_by_nome(nome_inexistente)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_erro_ao_atualizar_permissao_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar permissão inexistente."""
    # Arrange
    service = PermissaoService(session)
    id_inexistente = uuid4()
    
    dados_atualizacao = {
        "descricao": "Descrição para permissão inexistente"
    }
    
    permissao_update = PermissaoUpdate(**dados_atualizacao)
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_permissao=id_inexistente,
            permissao=permissao_update
        )
    
    assert exc_info.value.status_code == 404
    assert "Permissão não encontrada" in str(exc_info.value.detail) 