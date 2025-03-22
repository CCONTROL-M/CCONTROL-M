import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from httpx import AsyncClient
import json

from app.main import app
from app.services.fornecedor_service import FornecedorService
from app.schemas.fornecedor import Fornecedor, FornecedorCreate, FornecedorUpdate, FornecedorList
from app.models.fornecedor import Fornecedor as FornecedorModel
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
            "fornecedores": {
                "visualizar": True,
                "criar": True,
                "editar": True,
                "excluir": True,
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
def fornecedor_mock():
    """Fixture para simular dados de fornecedor."""
    return {
        "id_fornecedor": str(uuid.uuid4()),
        "id_empresa": "98765432-9876-5432-9876-543298765432",
        "nome": "Fornecedor Teste",
        "cnpj": "12345678000199",
        "telefone": "11987654321",
        "email": "fornecedor@teste.com",
        "endereco": "Rua Teste, 123",
        "observacao": "Observação teste",
        "avaliacao": 4,
        "ativo": True,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }


@pytest.fixture
def fornecedores_mock():
    """Fixture para simular uma lista de fornecedores."""
    return {
        "items": [
            {
                "id_fornecedor": str(uuid.uuid4()),
                "id_empresa": "98765432-9876-5432-9876-543298765432",
                "nome": "Fornecedor 1",
                "cnpj": "12345678000199",
                "telefone": "11987654321",
                "email": "fornecedor1@teste.com",
                "avaliacao": 5,
                "ativo": True
            },
            {
                "id_fornecedor": str(uuid.uuid4()),
                "id_empresa": "98765432-9876-5432-9876-543298765432",
                "nome": "Fornecedor 2",
                "cnpj": "98765432000199",
                "telefone": "11987654322",
                "email": "fornecedor2@teste.com",
                "avaliacao": 3,
                "ativo": True
            }
        ],
        "total": 2,
        "page": 1,
        "size": 10
    }


class TestFornecedoresRouter:
    """Testes para o router de fornecedores."""
    
    @patch("app.routers.fornecedores.FornecedorService")
    def test_listar_fornecedores(self, mock_service, test_client, fornecedores_mock):
        """Teste para rota de listagem de fornecedores com paginação."""
        # Arrange
        mock_service.return_value.listar_fornecedores.return_value = (
            fornecedores_mock["items"], fornecedores_mock["total"]
        )
        
        # Act
        response = test_client.get(
            "/api/fornecedores?id_empresa=98765432-9876-5432-9876-543298765432&skip=0&limit=10"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == fornecedores_mock["total"]
        assert len(data["items"]) == len(fornecedores_mock["items"])
        
        # Verificar chamada ao serviço
        mock_service.return_value.listar_fornecedores.assert_called_once()

    @patch("app.routers.fornecedores.FornecedorService")
    def test_obter_fornecedor(self, mock_service, test_client, fornecedor_mock):
        """Teste para rota de obtenção de fornecedor por ID."""
        # Arrange
        mock_service.return_value.get_fornecedor.return_value = fornecedor_mock
        
        # Act
        response = test_client.get(
            f"/api/fornecedores/{fornecedor_mock['id_fornecedor']}?id_empresa=98765432-9876-5432-9876-543298765432"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id_fornecedor"] == fornecedor_mock["id_fornecedor"]
        assert data["nome"] == fornecedor_mock["nome"]
        assert data["cnpj"] == fornecedor_mock["cnpj"]
        
        # Verificar chamada ao serviço
        mock_service.return_value.get_fornecedor.assert_called_once_with(
            uuid.UUID(fornecedor_mock["id_fornecedor"]), 
            uuid.UUID("98765432-9876-5432-9876-543298765432")
        )

    @patch("app.routers.fornecedores.FornecedorService")
    def test_obter_fornecedor_not_found(self, mock_service, test_client):
        """Teste para rota de obtenção de fornecedor inexistente."""
        # Arrange
        id_fornecedor = str(uuid.uuid4())
        mock_service.return_value.get_fornecedor.side_effect = Exception("Fornecedor não encontrado")
        
        # Act
        response = test_client.get(
            f"/api/fornecedores/{id_fornecedor}?id_empresa=98765432-9876-5432-9876-543298765432"
        )
        
        # Assert
        assert response.status_code == 500  # ou o código que sua API retorna para exceções

    @patch("app.routers.fornecedores.FornecedorService")
    @patch("app.routers.fornecedores.LogSistemaService")
    def test_criar_fornecedor(self, mock_log_service, mock_service, test_client, fornecedor_mock):
        """Teste para rota de criação de fornecedor."""
        # Arrange
        novo_fornecedor = {
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "nome": "Novo Fornecedor",
            "cnpj": "12345678000199",
            "telefone": "11987654321",
            "email": "novo@fornecedor.com",
            "endereco": "Rua Nova, 456",
            "avaliacao": 5,
            "ativo": True
        }
        
        mock_service.return_value.criar_fornecedor.return_value = fornecedor_mock
        mock_log_service.return_value.registrar_log.return_value = None
        
        # Act
        response = test_client.post(
            "/api/fornecedores",
            json=novo_fornecedor
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == fornecedor_mock["nome"]
        
        # Verificar chamadas aos serviços
        mock_service.return_value.criar_fornecedor.assert_called_once()
        mock_log_service.return_value.registrar_log.assert_called_once()

    @patch("app.routers.fornecedores.FornecedorService")
    def test_criar_fornecedor_cnpj_invalido(self, mock_service, test_client):
        """Teste para rota de criação de fornecedor com CNPJ inválido."""
        # Arrange
        fornecedor_invalido = {
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "nome": "Fornecedor CNPJ Inválido",
            "cnpj": "123",  # CNPJ inválido
            "telefone": "123",
            "email": "emailinvalido",
            "ativo": True
        }
        
        mock_service.return_value.criar_fornecedor.side_effect = HTTPException(
            status_code=400, detail="CNPJ inválido"
        )
        
        # Act
        response = test_client.post(
            "/api/fornecedores",
            json=fornecedor_invalido
        )
        
        # Assert
        assert response.status_code in [400, 422]  # Validation error

    @patch("app.routers.fornecedores.FornecedorService")
    def test_criar_fornecedor_dados_invalidos(self, mock_service, test_client):
        """Teste para rota de criação de fornecedor com dados inválidos."""
        # Arrange
        fornecedor_invalido = {
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "nome": "",  # Nome inválido (vazio)
            "cnpj": "12345678000199",
            "telefone": "123",
            "email": "emailinvalido",
            "ativo": True
        }
        
        # Act
        response = test_client.post(
            "/api/fornecedores",
            json=fornecedor_invalido
        )
        
        # Assert
        assert response.status_code == 422  # Validation error

    @patch("app.routers.fornecedores.FornecedorService")
    @patch("app.routers.fornecedores.LogSistemaService")
    def test_atualizar_fornecedor(self, mock_log_service, mock_service, test_client, fornecedor_mock):
        """Teste para rota de atualização de fornecedor."""
        # Arrange
        id_fornecedor = fornecedor_mock["id_fornecedor"]
        dados_atualizacao = {
            "nome": "Fornecedor Atualizado",
            "telefone": "11999999999",
            "email": "atualizado@fornecedor.com",
            "avaliacao": 5
        }
        
        fornecedor_atualizado = {**fornecedor_mock, **dados_atualizacao}
        mock_service.return_value.get_fornecedor.return_value = fornecedor_mock
        mock_service.return_value.atualizar_fornecedor.return_value = fornecedor_atualizado
        mock_log_service.return_value.registrar_log.return_value = None
        
        # Act
        response = test_client.put(
            f"/api/fornecedores/{id_fornecedor}?id_empresa=98765432-9876-5432-9876-543298765432",
            json=dados_atualizacao
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == dados_atualizacao["nome"]
        assert data["telefone"] == dados_atualizacao["telefone"]
        assert data["email"] == dados_atualizacao["email"]
        assert data["avaliacao"] == dados_atualizacao["avaliacao"]
        
        # Verificar chamadas aos serviços
        mock_service.return_value.get_fornecedor.assert_called_once()
        mock_service.return_value.atualizar_fornecedor.assert_called_once()
        mock_log_service.return_value.registrar_log.assert_called_once()

    @patch("app.routers.fornecedores.FornecedorService")
    @patch("app.routers.fornecedores.LogSistemaService")
    def test_remover_fornecedor(self, mock_log_service, mock_service, test_client, fornecedor_mock):
        """Teste para rota de remoção de fornecedor."""
        # Arrange
        id_fornecedor = fornecedor_mock["id_fornecedor"]
        mock_service.return_value.get_fornecedor.return_value = fornecedor_mock
        mock_service.return_value.remover_fornecedor.return_value = {"mensagem": "Fornecedor removido com sucesso"}
        mock_log_service.return_value.registrar_log.return_value = None
        
        # Act
        response = test_client.delete(
            f"/api/fornecedores/{id_fornecedor}?id_empresa=98765432-9876-5432-9876-543298765432"
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verificar chamadas aos serviços
        mock_service.return_value.get_fornecedor.assert_called_once()
        mock_service.return_value.remover_fornecedor.assert_called_once()
        mock_log_service.return_value.registrar_log.assert_called_once() 