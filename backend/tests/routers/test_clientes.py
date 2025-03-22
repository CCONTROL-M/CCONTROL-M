import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

from app.main import app
from app.services.cliente_service import ClienteService
from app.schemas.cliente import Cliente, ClienteCreate, ClienteUpdate, ClienteList
from app.models.cliente import Cliente as ClienteModel
from app.dependencies import get_current_user, get_async_session


# Sobrescrever dependências para testes
@pytest.fixture
def override_dependencies():
    """Sobrescrever dependências de autenticação e sessão para testes."""
    # Mock do usuário autenticado
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "12345678-1234-5678-1234-567812345678",
        "id_empresa": "98765432-9876-5432-9876-543298765432",
        "nome": "Usuário Teste",
        "email": "usuario@teste.com",
        "tipo": "admin",
        "telas_permitidas": {
            "clientes": {
                "visualizar": True,
                "criar": True,
                "editar": True,
                "deletar": True,
                "listar": True
            }
        }
    }
    
    # Mock da sessão assíncrona
    app.dependency_overrides[get_async_session] = lambda: AsyncMock()
    
    yield
    
    # Limpar todas as sobreposições após os testes
    app.dependency_overrides = {}


@pytest.fixture
def test_client(override_dependencies):
    """Fixture para criar um cliente de teste."""
    return TestClient(app)


@pytest.fixture
def cliente_mock():
    """Fixture para simular dados de cliente."""
    return {
        "id_cliente": str(uuid.uuid4()),
        "id_empresa": "98765432-9876-5432-9876-543298765432",
        "nome": "Cliente Teste",
        "documento": "12345678901",
        "telefone": "11987654321",
        "email": "cliente@teste.com",
        "ativo": True,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }


@pytest.fixture
def clientes_mock():
    """Fixture para simular uma lista de clientes."""
    return {
        "items": [
            {
                "id_cliente": str(uuid.uuid4()),
                "id_empresa": "98765432-9876-5432-9876-543298765432",
                "nome": "Cliente 1",
                "documento": "12345678901",
                "telefone": "11987654321",
                "email": "cliente1@teste.com",
                "ativo": True
            },
            {
                "id_cliente": str(uuid.uuid4()),
                "id_empresa": "98765432-9876-5432-9876-543298765432",
                "nome": "Cliente 2",
                "documento": "98765432109",
                "telefone": "11987654322",
                "email": "cliente2@teste.com",
                "ativo": True
            }
        ],
        "total": 2,
        "page": 1,
        "size": 10
    }


class TestClientesRouter:
    """Testes para o router de clientes."""
    
    @patch("app.routers.clientes.ClienteService")
    def test_listar_clientes(self, mock_service, test_client, clientes_mock):
        """Teste para rota de listagem de clientes com paginação."""
        # Arrange
        mock_service.return_value.listar_clientes.return_value = (
            clientes_mock["items"], clientes_mock["total"]
        )
        
        # Act
        response = test_client.get(
            "/api/clientes?id_empresa=98765432-9876-5432-9876-543298765432&skip=0&limit=10"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == clientes_mock["total"]
        assert len(data["items"]) == len(clientes_mock["items"])
        
        # Verificar chamada ao serviço
        mock_service.return_value.listar_clientes.assert_called_once()

    @patch("app.routers.clientes.ClienteService")
    def test_obter_cliente(self, mock_service, test_client, cliente_mock):
        """Teste para rota de obtenção de cliente por ID."""
        # Arrange
        mock_service.return_value.get_cliente.return_value = cliente_mock
        
        # Act
        response = test_client.get(
            f"/api/clientes/{cliente_mock['id_cliente']}?id_empresa=98765432-9876-5432-9876-543298765432"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id_cliente"] == cliente_mock["id_cliente"]
        assert data["nome"] == cliente_mock["nome"]
        assert data["documento"] == cliente_mock["documento"]
        
        # Verificar chamada ao serviço
        mock_service.return_value.get_cliente.assert_called_once_with(
            uuid.UUID(cliente_mock["id_cliente"]), 
            uuid.UUID("98765432-9876-5432-9876-543298765432")
        )

    @patch("app.routers.clientes.ClienteService")
    def test_obter_cliente_not_found(self, mock_service, test_client):
        """Teste para rota de obtenção de cliente inexistente."""
        # Arrange
        id_cliente = str(uuid.uuid4())
        mock_service.return_value.get_cliente.side_effect = Exception("Cliente não encontrado")
        
        # Act
        response = test_client.get(
            f"/api/clientes/{id_cliente}?id_empresa=98765432-9876-5432-9876-543298765432"
        )
        
        # Assert
        assert response.status_code == 500  # ou o código que sua API retorna para exceções

    @patch("app.routers.clientes.ClienteService")
    @patch("app.routers.clientes.LogSistemaService")
    def test_criar_cliente(self, mock_log_service, mock_service, test_client, cliente_mock):
        """Teste para rota de criação de cliente."""
        # Arrange
        novo_cliente = {
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "nome": "Novo Cliente",
            "documento": "11122233344",
            "telefone": "11987654321",
            "email": "novo@cliente.com",
            "ativo": True
        }
        
        mock_service.return_value.criar_cliente.return_value = cliente_mock
        mock_log_service.return_value.registrar_log.return_value = None
        
        # Act
        response = test_client.post(
            "/api/clientes",
            json=novo_cliente
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == cliente_mock["nome"]
        
        # Verificar chamadas aos serviços
        mock_service.return_value.criar_cliente.assert_called_once()
        mock_log_service.return_value.registrar_log.assert_called_once()

    @patch("app.routers.clientes.ClienteService")
    def test_criar_cliente_dados_invalidos(self, mock_service, test_client):
        """Teste para rota de criação de cliente com dados inválidos."""
        # Arrange
        cliente_invalido = {
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "nome": "",  # Nome inválido (vazio)
            "documento": "123",  # CPF inválido
            "telefone": "123",
            "email": "emailinvalido",
            "ativo": True
        }
        
        # Act
        response = test_client.post(
            "/api/clientes",
            json=cliente_invalido
        )
        
        # Assert
        assert response.status_code == 422  # Validation error

    @patch("app.routers.clientes.ClienteService")
    @patch("app.routers.clientes.LogSistemaService")
    def test_atualizar_cliente(self, mock_log_service, mock_service, test_client, cliente_mock):
        """Teste para rota de atualização de cliente."""
        # Arrange
        id_cliente = cliente_mock["id_cliente"]
        dados_atualizacao = {
            "nome": "Cliente Atualizado",
            "telefone": "11999999999",
            "email": "atualizado@cliente.com"
        }
        
        cliente_atualizado = {**cliente_mock, **dados_atualizacao}
        mock_service.return_value.get_cliente.return_value = cliente_mock
        mock_service.return_value.atualizar_cliente.return_value = cliente_atualizado
        mock_log_service.return_value.registrar_log.return_value = None
        
        # Act
        response = test_client.put(
            f"/api/clientes/{id_cliente}?id_empresa=98765432-9876-5432-9876-543298765432",
            json=dados_atualizacao
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == dados_atualizacao["nome"]
        assert data["telefone"] == dados_atualizacao["telefone"]
        assert data["email"] == dados_atualizacao["email"]
        
        # Verificar chamadas aos serviços
        mock_service.return_value.get_cliente.assert_called_once()
        mock_service.return_value.atualizar_cliente.assert_called_once()
        mock_log_service.return_value.registrar_log.assert_called_once()

    @patch("app.routers.clientes.ClienteService")
    @patch("app.routers.clientes.LogSistemaService")
    def test_remover_cliente(self, mock_log_service, mock_service, test_client, cliente_mock):
        """Teste para rota de remoção de cliente."""
        # Arrange
        id_cliente = cliente_mock["id_cliente"]
        mock_service.return_value.get_cliente.return_value = cliente_mock
        mock_service.return_value.remover_cliente.return_value = {"mensagem": "Cliente removido com sucesso"}
        mock_log_service.return_value.registrar_log.return_value = None
        
        # Act
        response = test_client.delete(
            f"/api/clientes/{id_cliente}?id_empresa=98765432-9876-5432-9876-543298765432"
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verificar chamadas aos serviços
        mock_service.return_value.get_cliente.assert_called_once()
        mock_service.return_value.remover_cliente.assert_called_once()
        mock_log_service.return_value.registrar_log.assert_called_once() 