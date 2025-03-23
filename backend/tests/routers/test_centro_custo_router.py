"""
Testes para as rotas de Centro de Custo.

Verifica o comportamento das APIs para operações CRUD de centros de custo.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import UUID, uuid4
from unittest.mock import patch, AsyncMock, MagicMock
import json

from app.main import app
from app.schemas.centro_custo import CentroCusto, CentroCustoCreate, CentroCustoUpdate
from app.dependencies import get_current_user
from app.database import db_async_session


@pytest.fixture
def mock_current_user():
    """Mock para o usuário autenticado."""
    return {
        "sub": "12345678-1234-5678-1234-567812345678",
        "empresa_id": "98765432-9876-5432-9876-543298765432",
        "nome": "Usuário Teste",
        "email": "teste@exemplo.com",
        "tipo_usuario": "ADMIN",
        "permissions": {
            "centro_custos": ["listar", "visualizar", "criar", "editar", "excluir"]
        }
    }


@pytest.fixture
def client(mock_current_user):
    """Cliente de teste com dependências simuladas."""
    with patch('app.routers.centro_custo.get_current_user', return_value=AsyncMock(return_value=mock_current_user)), \
         patch('app.routers.centro_custo.db_async_session', return_value=AsyncMock()), \
         patch('app.dependencies.db_async_session', return_value=AsyncMock()), \
         patch('app.utils.permissions.verify_permission', return_value=AsyncMock(return_value=True)):
        client = TestClient(app)
        yield client


@pytest.fixture
def mock_centro_custo_service():
    """Fornece um mock para o CentroCustoService."""
    with patch('app.routers.centro_custo.CentroCustoService') as mock_service:
        centro_custo_service_instance = mock_service.return_value
        
        # Mock para o método de criação
        centro_custo_service_instance.criar_centro_custo = AsyncMock(return_value={
            "id_centro_custo": "12345678-1234-5678-1234-567812345678",
            "nome": "Centro de Custo Teste",
            "descricao": "Descrição de teste",
            "ativo": True,
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        })
        
        # Mock para o método de atualização
        centro_custo_service_instance.atualizar_centro_custo = AsyncMock(return_value={
            "id_centro_custo": "12345678-1234-5678-1234-567812345678",
            "nome": "Centro de Custo Atualizado",
            "descricao": "Descrição atualizada",
            "ativo": True,
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00"
        })
        
        # Mock para o método de busca por ID
        centro_custo_service_instance.get_centro_custo = AsyncMock(return_value={
            "id_centro_custo": "12345678-1234-5678-1234-567812345678",
            "nome": "Centro de Custo Teste",
            "descricao": "Descrição de teste",
            "ativo": True,
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        })
        
        # Mock para o método de listagem
        centro_custo_service_instance.listar_centros_custo = AsyncMock(return_value=(
            [{
                "id_centro_custo": "12345678-1234-5678-1234-567812345678",
                "nome": "Centro de Custo Teste",
                "descricao": "Descrição de teste",
                "ativo": True,
                "id_empresa": "98765432-9876-5432-9876-543298765432",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }],
            1
        ))
        
        # Mock para o método de remoção
        centro_custo_service_instance.remover_centro_custo = AsyncMock(return_value={
            "detail": "Centro de custo removido com sucesso"
        })
        
        # Mock para métodos de ativação/desativação
        centro_custo_service_instance.ativar_centro_custo = AsyncMock(return_value={
            "id_centro_custo": "12345678-1234-5678-1234-567812345678",
            "nome": "Centro de Custo Teste",
            "descricao": "Descrição de teste",
            "ativo": True,
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00"
        })
        
        centro_custo_service_instance.desativar_centro_custo = AsyncMock(return_value={
            "id_centro_custo": "12345678-1234-5678-1234-567812345678",
            "nome": "Centro de Custo Teste",
            "descricao": "Descrição de teste",
            "ativo": False,
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00"
        })
        
        yield centro_custo_service_instance


@pytest.fixture
def mock_log_service():
    """Fornece um mock para o LogSistemaService."""
    with patch('app.services.log_sistema_service.LogSistemaService') as mock:
        mock_instance = mock.return_value
        mock_instance.registrar_atividade = AsyncMock()
        yield mock_instance


class TestCentroCustoRouter:
    """Testes para as rotas de centro de custo."""
    
    def test_listar_centros_custo(self, client, mock_centro_custo_service):
        """Teste para a rota de listagem de centros de custo."""
        # Executa a requisição GET para listar centros de custo
        response = client.get("/api/v1/centro-custo")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["nome"] == "Centro de Custo Teste"
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.listar_centros_custo.assert_called_once()
    
    def test_obter_centro_custo(self, client, mock_centro_custo_service):
        """Teste para a rota de obtenção de um centro de custo por ID."""
        # Executa a requisição GET para obter um centro de custo específico
        centro_custo_id = "12345678-1234-5678-1234-567812345678"
        response = client.get(f"/api/v1/centro-custo/{centro_custo_id}")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["id_centro_custo"] == centro_custo_id
        assert data["nome"] == "Centro de Custo Teste"
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.get_centro_custo.assert_called_once_with(
            UUID(centro_custo_id), UUID("98765432-9876-5432-9876-543298765432")
        )
    
    def test_criar_centro_custo(self, client, mock_centro_custo_service, mock_log_service):
        """Teste para a rota de criação de centro de custo."""
        # Dados para criação do centro de custo
        centro_custo_data = {
            "nome": "Centro de Custo Teste",
            "descricao": "Descrição de teste",
            "id_empresa": "98765432-9876-5432-9876-543298765432"
        }
        
        # Executa a requisição POST para criar um centro de custo
        response = client.post(
            "/api/v1/centro-custo",
            json=centro_custo_data
        )
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["nome"] == "Centro de Custo Teste"
        assert "id_centro_custo" in data
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.criar_centro_custo.assert_called_once()
    
    def test_atualizar_centro_custo(self, client, mock_centro_custo_service, mock_log_service):
        """Teste para a rota de atualização de centro de custo."""
        # ID do centro de custo a ser atualizado
        centro_custo_id = "12345678-1234-5678-1234-567812345678"
        
        # Dados para atualização do centro de custo
        centro_custo_data = {
            "nome": "Centro de Custo Atualizado",
            "descricao": "Descrição atualizada"
        }
        
        # Executa a requisição PUT para atualizar um centro de custo
        response = client.put(
            f"/api/v1/centro-custo/{centro_custo_id}",
            json=centro_custo_data
        )
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["nome"] == "Centro de Custo Atualizado"
        assert data["descricao"] == "Descrição atualizada"
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.atualizar_centro_custo.assert_called_once()
    
    def test_remover_centro_custo(self, client, mock_centro_custo_service, mock_log_service):
        """Teste para a rota de remoção de centro de custo."""
        # ID do centro de custo a ser removido
        centro_custo_id = "12345678-1234-5678-1234-567812345678"
        
        # Executa a requisição DELETE para remover um centro de custo
        response = client.delete(f"/api/v1/centro-custo/{centro_custo_id}")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Centro de custo removido com sucesso"
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.remover_centro_custo.assert_called_once_with(
            UUID(centro_custo_id), 
            UUID("98765432-9876-5432-9876-543298765432"),
            UUID("12345678-1234-5678-1234-567812345678")
        )
    
    def test_ativar_centro_custo(self, client, mock_centro_custo_service):
        """Teste para a rota de ativação de centro de custo."""
        # ID do centro de custo a ser ativado
        centro_custo_id = "12345678-1234-5678-1234-567812345678"
        
        # Executa a requisição PATCH para ativar um centro de custo
        response = client.patch(f"/api/v1/centro-custo/{centro_custo_id}/ativar")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["ativo"] is True
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.ativar_centro_custo.assert_called_once()
    
    def test_desativar_centro_custo(self, client, mock_centro_custo_service):
        """Teste para a rota de desativação de centro de custo."""
        # ID do centro de custo a ser desativado
        centro_custo_id = "12345678-1234-5678-1234-567812345678"
        
        # Executa a requisição PATCH para desativar um centro de custo
        response = client.patch(f"/api/v1/centro-custo/{centro_custo_id}/desativar")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o conteúdo da resposta tem o formato esperado
        data = response.json()
        assert data["ativo"] is False
        
        # Verifica se o serviço foi chamado corretamente
        mock_centro_custo_service.desativar_centro_custo.assert_called_once()
    
    def test_filtrar_centros_custo_por_nome(self, client, mock_centro_custo_service):
        """Teste para a rota de listagem de centros de custo com filtro por nome."""
        # Executa a requisição GET para listar centros de custo com filtro
        response = client.get("/api/v1/centro-custo?nome=Teste")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o serviço foi chamado com os parâmetros corretos
        mock_centro_custo_service.listar_centros_custo.assert_called_once()
        
        # Extrai os argumentos da chamada do serviço e verifica o filtro
        args, kwargs = mock_centro_custo_service.listar_centros_custo.call_args
        assert 'nome' in kwargs
        assert kwargs['nome'] == 'Teste'
    
    def test_filtrar_centros_custo_por_status(self, client, mock_centro_custo_service):
        """Teste para a rota de listagem de centros de custo com filtro por status."""
        # Executa a requisição GET para listar centros de custo ativos
        response = client.get("/api/v1/centro-custo?ativo=true")
        
        # Verifica se a resposta foi bem-sucedida
        assert response.status_code == status.HTTP_200_OK
        
        # Verifica se o serviço foi chamado com os parâmetros corretos
        mock_centro_custo_service.listar_centros_custo.assert_called_once()
        
        # Extrai os argumentos da chamada do serviço e verifica o filtro
        args, kwargs = mock_centro_custo_service.listar_centros_custo.call_args
        assert 'ativo' in kwargs
        assert kwargs['ativo'] is True
    
    def test_centro_custo_permissao_negada(self, client, mock_centro_custo_service):
        """Teste para verificar comportamento quando a permissão é negada."""
        # Configura o mock para negar permissão
        with patch('app.utils.permissions.verify_permission', return_value=AsyncMock(return_value=False)):
            # Executa a requisição GET para listar centros de custo
            response = client.get("/api/v1/centro-custo")
            
            # Verifica se a resposta foi de acesso negado
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
            # Verifica se o serviço não foi chamado
            mock_centro_custo_service.listar_centros_custo.assert_not_called()
    
    def test_centro_custo_nao_encontrado(self, client, mock_centro_custo_service):
        """Teste para verificar comportamento quando o centro de custo não é encontrado."""
        # Configura o mock para lançar exceção de não encontrado
        mock_centro_custo_service.get_centro_custo.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Centro de custo não encontrado"
        )
        
        # Executa a requisição GET para obter um centro de custo inexistente
        centro_custo_id = "99999999-9999-9999-9999-999999999999"
        response = client.get(f"/api/v1/centro-custo/{centro_custo_id}")
        
        # Verifica se a resposta foi de não encontrado
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Centro de custo não encontrado" 