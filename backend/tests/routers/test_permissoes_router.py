"""
Testes para as rotas de Permissões de Usuário.

Verifica o comportamento das APIs para operações CRUD de permissões de usuários.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from uuid import UUID, uuid4
from unittest.mock import patch, AsyncMock, MagicMock
import json

from app.main import app
from app.schemas.permissao_usuario import PermissaoUsuario, PermissaoUsuarioCreate, PermissaoUsuarioUpdate
from app.dependencies import get_current_user
from app.database import db_async_session


@pytest.fixture
def mock_current_user():
    """Mock para o usuário administrador autenticado."""
    return {
        "sub": "12345678-1234-5678-1234-567812345678",
        "empresa_id": "98765432-9876-5432-9876-543298765432",
        "nome": "Admin Teste",
        "email": "admin@exemplo.com",
        "tipo_usuario": "ADMIN",
        "permissions": {
            "usuarios": ["listar", "visualizar", "criar", "editar", "excluir"],
            "permissoes": ["listar", "visualizar", "criar", "editar", "excluir"]
        }
    }


@pytest.fixture
def client(mock_current_user):
    """Cliente de teste com dependências simuladas."""
    with patch('app.routers.permissoes.router.get_current_user', return_value=AsyncMock(return_value=mock_current_user)), \
         patch('app.routers.permissoes.get_async_session', return_value=AsyncMock()), \
         patch('app.dependencies.db_async_session', return_value=AsyncMock()), \
         patch('app.utils.permissions.verify_permission', return_value=AsyncMock(return_value=True)):
        client = TestClient(app)
        yield client


@pytest.fixture
def mock_permissao_service():
    """Fornece um mock para o PermissaoService."""
    with patch('app.routers.permissoes.PermissaoService') as mock_service:
        permissao_service_instance = mock_service.return_value
        
        # Mock para o método de criação
        permissao_service_instance.criar_permissao = AsyncMock(return_value={
            "id_permissao": "12345678-1234-5678-1234-567812345678",
            "id_usuario": "98765432-9876-5432-9876-543298765432",
            "recurso": "clientes",
            "acoes": ["listar", "visualizar", "criar", "editar"],
            "created_at": "2023-01-01T00:00:00"
        })
        
        # Mock para o método de atualização
        permissao_service_instance.atualizar_permissao = AsyncMock(return_value={
            "id_permissao": "12345678-1234-5678-1234-567812345678",
            "id_usuario": "98765432-9876-5432-9876-543298765432",
            "recurso": "clientes",
            "acoes": ["listar", "visualizar", "criar", "editar", "excluir"],
            "created_at": "2023-01-01T00:00:00"
        })
        
        # Mock para o método de remoção
        permissao_service_instance.remover_permissao = AsyncMock(return_value={
            "detail": "Permissão removida com sucesso"
        })
        
        # Mock para o método de verificação
        permissao_service_instance.verificar_permissao = AsyncMock(return_value=True)
        
        # Mock para o método de busca por ID
        permissao_service_instance.obter_permissao = AsyncMock(return_value={
            "id_permissao": "12345678-1234-5678-1234-567812345678",
            "id_usuario": "98765432-9876-5432-9876-543298765432",
            "recurso": "clientes",
            "acoes": ["listar", "visualizar", "criar", "editar"],
            "created_at": "2023-01-01T00:00:00"
        })
        
        # Mock para o método de listagem por usuário
        permissao_service_instance.listar_permissoes_por_usuario = AsyncMock(return_value=(
            [{
                "id_permissao": "12345678-1234-5678-1234-567812345678",
                "id_usuario": "98765432-9876-5432-9876-543298765432",
                "recurso": "clientes",
                "acoes": ["listar", "visualizar", "criar", "editar"],
                "created_at": "2023-01-01T00:00:00"
            },
            {
                "id_permissao": "23456789-2345-6789-2345-678923456789",
                "id_usuario": "98765432-9876-5432-9876-543298765432",
                "recurso": "vendas",
                "acoes": ["listar", "visualizar"],
                "created_at": "2023-01-01T00:00:00"
            }],
            2
        ))
        
        # Mock para o método de listagem todas as permissões
        permissao_service_instance.listar_todas_permissoes = AsyncMock(return_value=(
            [{
                "id_permissao": "12345678-1234-5678-1234-567812345678",
                "id_usuario": "98765432-9876-5432-9876-543298765432",
                "recurso": "clientes",
                "acoes": ["listar", "visualizar", "criar", "editar"],
                "created_at": "2023-01-01T00:00:00"
            },
            {
                "id_permissao": "23456789-2345-6789-2345-678923456789",
                "id_usuario": "87654321-8765-4321-8765-432187654321",
                "recurso": "vendas",
                "acoes": ["listar", "visualizar"],
                "created_at": "2023-01-01T00:00:00"
            }],
            2
        ))
        
        yield permissao_service_instance


@pytest.fixture
def mock_log_service():
    """Fornece um mock para o LogSistemaService."""
    with patch('app.services.log_sistema_service.LogSistemaService') as mock:
        mock_instance = mock.return_value
        mock_instance.registrar_atividade = AsyncMock()
        yield mock_instance


class TestPermissoesRouter:
    """Testes para as rotas de permissões de usuário."""
    
    def test_listar_permissoes(self, client, mock_permissao_service):
        """Teste para a rota de listagem de todas as permissões."""
        # Executa a requisição GET para listar permissões
        response = client.get("/api/v1/permissoes-usuario")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["recurso"] == "clientes"
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.listar_todas_permissoes.assert_called_once()
    
    def test_listar_permissoes_por_usuario(self, client, mock_permissao_service):
        """Teste para a rota de listagem de permissões por usuário."""
        # ID do usuário para filtrar permissões
        usuario_id = "98765432-9876-5432-9876-543298765432"
        
        # Executa a requisição GET para listar permissões do usuário
        response = client.get(f"/api/v1/permissoes-usuario?id_usuario={usuario_id}")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["id_usuario"] == usuario_id
        assert data["items"][1]["id_usuario"] == usuario_id
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.listar_permissoes_por_usuario.assert_called_once_with(
            UUID(usuario_id), 
            UUID(mock_current_user()["empresa_id"]),
            skip=0,
            limit=100
        )
    
    def test_obter_permissao(self, client, mock_permissao_service):
        """Teste para a rota de obtenção de uma permissão por ID."""
        # ID da permissão a ser obtida
        permissao_id = "12345678-1234-5678-1234-567812345678"
        
        # Executa a requisição GET para obter uma permissão específica
        response = client.get(f"/api/v1/permissoes-usuario/{permissao_id}")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["id_permissao"] == permissao_id
        assert data["recurso"] == "clientes"
        assert "listar" in data["acoes"]
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.obter_permissao.assert_called_once_with(
            UUID(permissao_id), 
            UUID(mock_current_user()["empresa_id"])
        )
    
    def test_criar_permissao(self, client, mock_permissao_service, mock_log_service):
        """Teste para a rota de criação de permissão."""
        # Dados para criação da permissão
        permissao_data = {
            "id_usuario": "98765432-9876-5432-9876-543298765432",
            "recurso": "clientes",
            "acoes": ["listar", "visualizar", "criar", "editar"]
        }
        
        # Executa a requisição POST para criar uma permissão
        response = client.post(
            "/api/v1/permissoes-usuario",
            json=permissao_data
        )
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["id_usuario"] == permissao_data["id_usuario"]
        assert data["recurso"] == permissao_data["recurso"]
        assert set(data["acoes"]) == set(permissao_data["acoes"])
        assert "id_permissao" in data
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.criar_permissao.assert_called_once()
    
    def test_atualizar_permissao(self, client, mock_permissao_service, mock_log_service):
        """Teste para a rota de atualização de permissão."""
        # ID da permissão a ser atualizada
        permissao_id = "12345678-1234-5678-1234-567812345678"
        
        # Dados para atualização da permissão
        permissao_data = {
            "acoes": ["listar", "visualizar", "criar", "editar", "excluir"]
        }
        
        # Executa a requisição PUT para atualizar uma permissão
        response = client.put(
            f"/api/v1/permissoes-usuario/{permissao_id}",
            json=permissao_data
        )
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "excluir" in data["acoes"]
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.atualizar_permissao.assert_called_once()
    
    def test_remover_permissao(self, client, mock_permissao_service, mock_log_service):
        """Teste para a rota de remoção de permissão."""
        # ID da permissão a ser removida
        permissao_id = "12345678-1234-5678-1234-567812345678"
        
        # Executa a requisição DELETE para remover uma permissão
        response = client.delete(f"/api/v1/permissoes-usuario/{permissao_id}")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Permissão removida com sucesso"
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.remover_permissao.assert_called_once_with(
            UUID(permissao_id), 
            UUID(mock_current_user()["empresa_id"]),
            UUID(mock_current_user()["sub"])
        )
    
    def test_verificar_permissao(self, client, mock_permissao_service):
        """Teste para a rota de verificação de permissão."""
        # Parâmetros para verificação de permissão
        usuario_id = "98765432-9876-5432-9876-543298765432"
        recurso = "clientes"
        acao = "editar"
        
        # Executa a requisição GET para verificar uma permissão
        response = client.get(f"/api/v1/permissoes-usuario/verificar?id_usuario={usuario_id}&recurso={recurso}&acao={acao}")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "tem_permissao" in data
        assert data["tem_permissao"] is True
        
        # Verifica se o serviço foi chamado corretamente
        mock_permissao_service.verificar_permissao.assert_called_once_with(
            UUID(usuario_id),
            recurso,
            acao,
            UUID(mock_current_user()["empresa_id"])
        )
    
    def test_criar_permissao_dados_invalidos(self, client, mock_permissao_service):
        """Teste para verificar comportamento ao criar permissão com dados inválidos."""
        # Dados inválidos para criação da permissão (faltando campos obrigatórios)
        permissao_data = {
            "recurso": "clientes"
            # Faltando id_usuario e acoes
        }
        
        # Executa a requisição POST para criar uma permissão
        response = client.post(
            "/api/v1/permissoes-usuario",
            json=permissao_data
        )
        
        # Verifica se a resposta foi de validação falhou
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Verifica se o serviço não foi chamado
        mock_permissao_service.criar_permissao.assert_not_called()
    
    def test_permissao_duplicada(self, client, mock_permissao_service):
        """Teste para verificar comportamento ao criar permissão duplicada."""
        # Dados para criação da permissão
        permissao_data = {
            "id_usuario": "98765432-9876-5432-9876-543298765432",
            "recurso": "clientes",
            "acoes": ["listar", "visualizar"]
        }
        
        # Configura o mock para lançar exceção de duplicidade
        mock_permissao_service.criar_permissao.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma permissão para o usuário no recurso 'clientes'"
        )
        
        # Executa a requisição POST para criar uma permissão
        response = client.post(
            "/api/v1/permissoes-usuario",
            json=permissao_data
        )
        
        # Verifica se a resposta foi de erro de requisição
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Já existe uma permissão para o usuário no recurso 'clientes'"
    
    def test_permissao_nao_encontrada(self, client, mock_permissao_service):
        """Teste para verificar comportamento quando a permissão não é encontrada."""
        # Configura o mock para lançar exceção de não encontrado
        mock_permissao_service.obter_permissao.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada"
        )
        
        # Executa a requisição GET para obter uma permissão inexistente
        permissao_id = "99999999-9999-9999-9999-999999999999"
        response = client.get(f"/api/v1/permissoes-usuario/{permissao_id}")
        
        # Verifica se a resposta foi de não encontrado
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Permissão não encontrada"
    
    def test_permissao_negada_admin_acesso(self, client, mock_permissao_service):
        """Teste para verificar comportamento quando acesso de admin é negado."""
        # Configura o mock para negar permissão
        with patch('app.utils.permissions.verify_permission', return_value=AsyncMock(return_value=False)):
            # Executa a requisição GET para listar permissões
            response = client.get("/api/v1/permissoes-usuario")
            
            # Verifica se a resposta foi de acesso negado
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
            # Verifica se o serviço não foi chamado
            mock_permissao_service.listar_todas_permissoes.assert_not_called() 