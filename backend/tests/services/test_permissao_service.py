"""
Testes para o serviço de permissões de usuário.

Verifica o comportamento do PermissaoService que contém a lógica de negócio.
"""
import pytest
import uuid
from fastapi import HTTPException, status
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.schemas.permissao_usuario import PermissaoUsuarioCreate, PermissaoUsuarioUpdate
from app.services.permissao_service import PermissaoService
from app.repositories.permissao_usuario_repository import PermissaoUsuarioRepository
from app.models.permissao_usuario import PermissaoUsuario as PermissaoUsuarioModel


class MockPermissaoUsuario:
    """Mock para objeto de permissão de usuário."""
    def __init__(self, id_permissao, id_usuario, recurso, acoes, created_at):
        self.id_permissao = id_permissao
        self.id_usuario = id_usuario
        self.recurso = recurso
        self.acoes = acoes
        self.created_at = created_at


@pytest.fixture
def mock_repository():
    """Mock para o repositório de permissões."""
    with patch('app.services.permissao_service.PermissaoUsuarioRepository') as mock:
        repository_instance = mock.return_value
        
        # Mock para get_by_id
        repository_instance.get_by_id = AsyncMock()
        
        # Mock para create
        repository_instance.create = AsyncMock()
        
        # Mock para update
        repository_instance.update = AsyncMock()
        
        # Mock para delete
        repository_instance.delete = AsyncMock()
        
        # Mock para get_by_user_id
        repository_instance.get_by_user_id = AsyncMock()
        
        # Mock para get_by_user_and_resource
        repository_instance.get_by_user_and_resource = AsyncMock(return_value=None)
        
        # Mock para check_user_permission
        repository_instance.check_user_permission = AsyncMock(return_value=True)
        
        yield repository_instance


@pytest.fixture
def mock_db_session():
    """Mock para a sessão do banco de dados."""
    with patch('app.services.permissao_service.db_async_session') as mock_session:
        async_session = AsyncMock(spec=AsyncSession)
        mock_session.return_value.__aenter__.return_value = async_session
        yield mock_session


@pytest.fixture
def mock_log_service():
    """Mock para o serviço de log."""
    with patch('app.services.permissao_service.LogSistemaService') as mock:
        log_service_instance = mock.return_value
        log_service_instance.registrar_log = AsyncMock()
        yield log_service_instance


@pytest.fixture
def test_permissao_data():
    """Dados de teste para permissões."""
    return {
        "permissao_create": {
            "id_usuario": str(uuid.uuid4()),
            "recurso": "clientes",
            "acoes": ["listar", "visualizar", "criar", "editar"]
        },
        "permissao_update": {
            "acoes": ["listar", "visualizar", "criar", "editar", "excluir"]
        },
        "permissao_existente": {
            "id_permissao": str(uuid.uuid4()),
            "id_usuario": str(uuid.uuid4()),
            "recurso": "clientes",
            "acoes": ["listar", "visualizar", "criar"],
            "created_at": "2023-01-01T00:00:00"
        }
    }


class TestPermissaoService:
    """Testes para o serviço de permissões de usuário."""
    
    @pytest.mark.asyncio
    async def test_criar_permissao(self, mock_repository, mock_db_session, mock_log_service, test_permissao_data):
        """Teste para criação de uma nova permissão."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock do repositório para create
        permissao_criada = {
            "id_permissao": str(uuid.uuid4()),
            "id_usuario": test_permissao_data["permissao_create"]["id_usuario"],
            "recurso": test_permissao_data["permissao_create"]["recurso"],
            "acoes": test_permissao_data["permissao_create"]["acoes"],
            "created_at": "2023-01-01T00:00:00"
        }
        mock_repository.create.return_value = permissao_criada
        
        # Dados para criação
        permissao_create = PermissaoUsuarioCreate(**test_permissao_data["permissao_create"])
        id_empresa = uuid.uuid4()
        id_usuario_admin = uuid.uuid4()
        
        # Executar o método do serviço
        result = await service.criar_permissao(permissao_create, id_empresa, id_usuario_admin)
        
        # Verificar se o resultado é o esperado
        assert result == permissao_criada
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.get_by_user_and_resource.assert_called_once_with(
            user_id=uuid.UUID(test_permissao_data["permissao_create"]["id_usuario"]),
            recurso=test_permissao_data["permissao_create"]["recurso"],
            tenant_id=id_empresa
        )
        
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_criar_permissao_duplicada(self, mock_repository, mock_db_session, test_permissao_data):
        """Teste para garantir que não é possível criar permissão duplicada."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock para simular permissão já existente
        mock_repository.get_by_user_and_resource.return_value = {
            "id_permissao": str(uuid.uuid4()),
            "id_usuario": test_permissao_data["permissao_create"]["id_usuario"],
            "recurso": test_permissao_data["permissao_create"]["recurso"],
            "acoes": ["listar"],
        }
        
        # Dados para criação
        permissao_create = PermissaoUsuarioCreate(**test_permissao_data["permissao_create"])
        id_empresa = uuid.uuid4()
        id_usuario_admin = uuid.uuid4()
        
        # Verificar se lança exceção apropriada
        with pytest.raises(HTTPException) as excinfo:
            await service.criar_permissao(permissao_create, id_empresa, id_usuario_admin)
        
        # Verificar se a exceção tem o status code correto
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verificar se o repositório create não foi chamado
        mock_repository.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_atualizar_permissao(self, mock_repository, mock_db_session, mock_log_service, test_permissao_data):
        """Teste para atualização de uma permissão existente."""
        # Configurar o serviço
        service = PermissaoService()
        
        # ID da permissão a ser atualizada
        id_permissao = uuid.uuid4()
        
        # Criar um objeto MockPermissaoUsuario para simular o modelo
        permissao_existente = MockPermissaoUsuario(
            id_permissao=test_permissao_data["permissao_existente"]["id_permissao"],
            id_usuario=test_permissao_data["permissao_existente"]["id_usuario"],
            recurso=test_permissao_data["permissao_existente"]["recurso"],
            acoes=test_permissao_data["permissao_existente"]["acoes"],
            created_at=test_permissao_data["permissao_existente"]["created_at"]
        )
        
        # Configurar o retorno do mock para get_by_id
        mock_repository.get_by_id.return_value = permissao_existente
        
        # Configurar o retorno do mock para update
        permissao_atualizada = {
            "id_permissao": str(id_permissao),
            "id_usuario": test_permissao_data["permissao_existente"]["id_usuario"],
            "recurso": test_permissao_data["permissao_existente"]["recurso"],
            "acoes": test_permissao_data["permissao_update"]["acoes"],
            "created_at": test_permissao_data["permissao_existente"]["created_at"]
        }
        mock_repository.update.return_value = permissao_atualizada
        
        # Dados para atualização
        permissao_update = PermissaoUsuarioUpdate(**test_permissao_data["permissao_update"])
        id_empresa = uuid.uuid4()
        id_usuario_admin = uuid.uuid4()
        
        # Executar o método do serviço
        result = await service.atualizar_permissao(id_permissao, permissao_update, id_empresa, id_usuario_admin)
        
        # Verificar se o resultado é o esperado
        assert result == permissao_atualizada
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.get_by_id.assert_called_once_with(
            id=id_permissao,
            tenant_id=id_empresa
        )
        
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_atualizar_permissao_inexistente(self, mock_repository, mock_db_session, test_permissao_data):
        """Teste para garantir que não é possível atualizar permissão inexistente."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock para simular permissão não encontrada
        mock_repository.get_by_id.return_value = None
        
        # ID da permissão a ser atualizada
        id_permissao = uuid.uuid4()
        
        # Dados para atualização
        permissao_update = PermissaoUsuarioUpdate(**test_permissao_data["permissao_update"])
        id_empresa = uuid.uuid4()
        id_usuario_admin = uuid.uuid4()
        
        # Verificar se lança exceção apropriada
        with pytest.raises(HTTPException) as excinfo:
            await service.atualizar_permissao(id_permissao, permissao_update, id_empresa, id_usuario_admin)
        
        # Verificar se a exceção tem o status code correto
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        
        # Verificar se o repositório update não foi chamado
        mock_repository.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_remover_permissao(self, mock_repository, mock_db_session, mock_log_service, test_permissao_data):
        """Teste para remoção de uma permissão existente."""
        # Configurar o serviço
        service = PermissaoService()
        
        # ID da permissão a ser removida
        id_permissao = uuid.uuid4()
        
        # Criar um objeto MockPermissaoUsuario para simular o modelo
        permissao_existente = MockPermissaoUsuario(
            id_permissao=test_permissao_data["permissao_existente"]["id_permissao"],
            id_usuario=test_permissao_data["permissao_existente"]["id_usuario"],
            recurso=test_permissao_data["permissao_existente"]["recurso"],
            acoes=test_permissao_data["permissao_existente"]["acoes"],
            created_at=test_permissao_data["permissao_existente"]["created_at"]
        )
        
        # Configurar o retorno do mock para get_by_id
        mock_repository.get_by_id.return_value = permissao_existente
        
        # Executar o método do serviço
        id_empresa = uuid.uuid4()
        id_usuario_admin = uuid.uuid4()
        result = await service.remover_permissao(id_permissao, id_empresa, id_usuario_admin)
        
        # Verificar se o resultado é o esperado
        assert result == {"detail": "Permissão removida com sucesso"}
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.get_by_id.assert_called_once_with(
            id=id_permissao,
            tenant_id=id_empresa
        )
        
        mock_repository.delete.assert_called_once_with(
            id=id_permissao,
            tenant_id=id_empresa
        )
    
    @pytest.mark.asyncio
    async def test_remover_permissao_inexistente(self, mock_repository, mock_db_session, test_permissao_data):
        """Teste para garantir que não é possível remover permissão inexistente."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock para simular permissão não encontrada
        mock_repository.get_by_id.return_value = None
        
        # ID da permissão a ser removida
        id_permissao = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario_admin = uuid.uuid4()
        
        # Verificar se lança exceção apropriada
        with pytest.raises(HTTPException) as excinfo:
            await service.remover_permissao(id_permissao, id_empresa, id_usuario_admin)
        
        # Verificar se a exceção tem o status code correto
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        
        # Verificar se o repositório delete não foi chamado
        mock_repository.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_listar_permissoes_por_usuario(self, mock_repository, mock_db_session, test_permissao_data):
        """Teste para listagem de permissões por usuário."""
        # Configurar o serviço
        service = PermissaoService()
        
        # ID do usuário para filtrar
        id_usuario = uuid.UUID(test_permissao_data["permissao_existente"]["id_usuario"])
        
        # Configurar o retorno do mock para get_by_user_id
        permissoes = [
            {
                "id_permissao": str(uuid.uuid4()),
                "id_usuario": str(id_usuario),
                "recurso": "clientes",
                "acoes": ["listar", "visualizar", "criar"],
                "created_at": "2023-01-01T00:00:00"
            },
            {
                "id_permissao": str(uuid.uuid4()),
                "id_usuario": str(id_usuario),
                "recurso": "vendas",
                "acoes": ["listar", "visualizar"],
                "created_at": "2023-01-01T00:00:00"
            }
        ]
        mock_repository.get_by_user_id.return_value = permissoes
        
        # Executar o método do serviço
        id_empresa = uuid.uuid4()
        result, total = await service.listar_permissoes_por_usuario(id_usuario, id_empresa)
        
        # Verificar se o resultado é o esperado
        assert total == len(permissoes)
        assert len(result) == len(permissoes)
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.get_by_user_id.assert_called_once_with(
            user_id=id_usuario,
            tenant_id=id_empresa
        )
    
    @pytest.mark.asyncio
    async def test_verificar_permissao_concedida(self, mock_repository, mock_db_session):
        """Teste para verificação de permissão concedida."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock para check_user_permission
        mock_repository.check_user_permission.return_value = True
        
        # Parâmetros para verificação
        id_usuario = uuid.uuid4()
        recurso = "clientes"
        acao = "editar"
        id_empresa = uuid.uuid4()
        
        # Executar o método do serviço
        result = await service.verificar_permissao(id_usuario, recurso, acao, id_empresa)
        
        # Verificar se o resultado é o esperado
        assert result is True
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.check_user_permission.assert_called_once_with(
            user_id=id_usuario,
            recurso=recurso,
            acao=acao,
            tenant_id=id_empresa
        )
    
    @pytest.mark.asyncio
    async def test_verificar_permissao_negada(self, mock_repository, mock_db_session):
        """Teste para verificação de permissão negada."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock para check_user_permission
        mock_repository.check_user_permission.return_value = False
        
        # Parâmetros para verificação
        id_usuario = uuid.uuid4()
        recurso = "clientes"
        acao = "excluir"
        id_empresa = uuid.uuid4()
        
        # Executar o método do serviço
        result = await service.verificar_permissao(id_usuario, recurso, acao, id_empresa)
        
        # Verificar se o resultado é o esperado
        assert result is False
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.check_user_permission.assert_called_once_with(
            user_id=id_usuario,
            recurso=recurso,
            acao=acao,
            tenant_id=id_empresa
        )
    
    @pytest.mark.asyncio
    async def test_obter_permissao(self, mock_repository, mock_db_session, test_permissao_data):
        """Teste para obtenção de uma permissão por ID."""
        # Configurar o serviço
        service = PermissaoService()
        
        # ID da permissão a ser obtida
        id_permissao = uuid.uuid4()
        
        # Configurar o retorno do mock para get_by_id
        mock_repository.get_by_id.return_value = test_permissao_data["permissao_existente"]
        
        # Executar o método do serviço
        id_empresa = uuid.uuid4()
        result = await service.obter_permissao(id_permissao, id_empresa)
        
        # Verificar se o resultado é o esperado
        assert result == test_permissao_data["permissao_existente"]
        
        # Verificar se o repositório foi chamado corretamente
        mock_repository.get_by_id.assert_called_once_with(
            id=id_permissao,
            tenant_id=id_empresa
        )
    
    @pytest.mark.asyncio
    async def test_obter_permissao_inexistente(self, mock_repository, mock_db_session):
        """Teste para garantir que obter permissão inexistente lança exceção."""
        # Configurar o serviço
        service = PermissaoService()
        
        # Configurar o retorno do mock para simular permissão não encontrada
        mock_repository.get_by_id.return_value = None
        
        # ID da permissão a ser obtida
        id_permissao = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        # Verificar se lança exceção apropriada
        with pytest.raises(HTTPException) as excinfo:
            await service.obter_permissao(id_permissao, id_empresa)
        
        # Verificar se a exceção tem o status code correto
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND 