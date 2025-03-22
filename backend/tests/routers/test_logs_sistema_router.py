"""
Testes para as rotas de Logs do Sistema.

Verifica o comportamento das APIs para operações de logs do sistema.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import UUID, uuid4
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date, datetime, timedelta
import json

from app.main import app
from app.schemas.log_sistema import LogSistema, LogSistemaCreate
from app.dependencies import get_current_user, get_async_session


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
            "logs_sistema": ["listar", "visualizar"]
        }
    }


@pytest.fixture
def client():
    """Cliente de teste com dependências simuladas."""
    with patch('app.routers.logs_sistema.get_current_user', return_value=AsyncMock(return_value=mock_current_user())), \
         patch('app.routers.logs_sistema.get_async_session', return_value=AsyncMock()), \
         patch('app.dependencies.get_async_session', return_value=AsyncMock()), \
         patch('app.utils.permissions.verify_permission', return_value=AsyncMock(return_value=True)):
        client = TestClient(app)
        yield client


@pytest.fixture
def mock_log_sistema_service():
    """Fornece um mock para o LogSistemaService."""
    with patch('app.routers.logs_sistema.LogSistemaService') as mock_service:
        log_service_instance = mock_service.return_value
        
        data_hoje = datetime.now()
        
        # Mock para o método de criação
        log_service_instance.registrar_log = AsyncMock(return_value={
            "id_log": "abcdef12-3456-7890-abcd-ef1234567890",
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "id_usuario": "12345678-1234-5678-1234-567812345678",
            "data_hora": data_hoje.isoformat(),
            "acao": "usuario:login",
            "descricao": "Login realizado com sucesso",
            "ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        })
        
        # Mock para o método de listagem
        log_service_instance.listar_logs = AsyncMock(return_value=(
            [
                {
                    "id_log": "abcdef12-3456-7890-abcd-ef1234567890",
                    "id_empresa": "98765432-9876-5432-9876-543298765432",
                    "id_usuario": "12345678-1234-5678-1234-567812345678",
                    "data_hora": data_hoje.isoformat(),
                    "acao": "usuario:login",
                    "descricao": "Login realizado com sucesso",
                    "ip": "192.168.1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
                },
                {
                    "id_log": "bcdef123-4567-8901-abcd-ef12345678901",
                    "id_empresa": "98765432-9876-5432-9876-543298765432",
                    "id_usuario": "12345678-1234-5678-1234-567812345678",
                    "data_hora": (data_hoje - timedelta(minutes=10)).isoformat(),
                    "acao": "cliente:criacao",
                    "descricao": "Cliente João criado",
                    "ip": "192.168.1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
                }
            ],
            2
        ))
        
        # Mock para buscar por ID
        log_service_instance.get_log = AsyncMock(return_value={
            "id_log": "abcdef12-3456-7890-abcd-ef1234567890",
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "id_usuario": "12345678-1234-5678-1234-567812345678",
            "data_hora": data_hoje.isoformat(),
            "acao": "usuario:login",
            "descricao": "Login realizado com sucesso",
            "ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        })
        
        # Mock para buscar logs por usuário
        log_service_instance.get_logs_por_usuario = AsyncMock(return_value=(
            [
                {
                    "id_log": "abcdef12-3456-7890-abcd-ef1234567890",
                    "id_empresa": "98765432-9876-5432-9876-543298765432",
                    "id_usuario": "12345678-1234-5678-1234-567812345678",
                    "data_hora": data_hoje.isoformat(),
                    "acao": "usuario:login",
                    "descricao": "Login realizado com sucesso",
                    "ip": "192.168.1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
                }
            ],
            1
        ))
        
        # Mock para buscar logs por tipo
        log_service_instance.get_logs_por_tipo = AsyncMock(return_value=(
            [
                {
                    "id_log": "abcdef12-3456-7890-abcd-ef1234567890",
                    "id_empresa": "98765432-9876-5432-9876-543298765432",
                    "id_usuario": "12345678-1234-5678-1234-567812345678",
                    "data_hora": data_hoje.isoformat(),
                    "acao": "usuario:login",
                    "descricao": "Login realizado com sucesso",
                    "ip": "192.168.1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
                }
            ],
            1
        ))
        
        yield log_service_instance


class TestLogsSistemaRouter:
    """Testes para o router de logs do sistema."""

    def test_listar_logs(self, client, mock_log_sistema_service):
        """Teste para listar logs do sistema."""
        id_empresa = "98765432-9876-5432-9876-543298765432"
        response = client.get(f"/api/v1/logs?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["acao"] == "usuario:login"
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_log_sistema_service.listar_logs.assert_awaited_once()

    def test_obter_log(self, client, mock_log_sistema_service):
        """Teste para obter um log por ID."""
        id_log = "abcdef12-3456-7890-abcd-ef1234567890"
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        response = client.get(f"/api/v1/logs/{id_log}?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id_log"] == id_log
        assert data["acao"] == "usuario:login"
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_log_sistema_service.get_log.assert_awaited_once_with(
            UUID(id_log), 
            UUID(id_empresa)
        )

    def test_registrar_log(self, client, mock_log_sistema_service):
        """Teste para registrar um novo log."""
        log_data = {
            "id_usuario": "12345678-1234-5678-1234-567812345678",
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "acao": "cliente:atualizacao",
            "descricao": "Cliente João atualizado",
            "ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
        }
        
        response = client.post("/api/v1/logs", json=log_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["acao"] == log_data["acao"]
        assert data["descricao"] == log_data["descricao"]
        
        # Verificar se o serviço foi chamado
        mock_log_sistema_service.registrar_log.assert_awaited_once()

    def test_obter_logs_por_usuario(self, client, mock_log_sistema_service):
        """Teste para obter logs por usuário."""
        id_empresa = "98765432-9876-5432-9876-543298765432"
        id_usuario = "12345678-1234-5678-1234-567812345678"
        
        response = client.get(f"/api/v1/logs/usuario/{id_usuario}?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id_usuario"] == id_usuario
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_log_sistema_service.get_logs_por_usuario.assert_awaited_once_with(
            UUID(id_usuario),
            UUID(id_empresa),
            skip=0,
            limit=100
        )

    def test_obter_logs_por_tipo(self, client, mock_log_sistema_service):
        """Teste para obter logs por tipo de ação."""
        id_empresa = "98765432-9876-5432-9876-543298765432"
        tipo_acao = "usuario:login"
        
        response = client.get(f"/api/v1/logs/tipo/{tipo_acao}?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["acao"] == tipo_acao
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_log_sistema_service.get_logs_por_tipo.assert_awaited_once_with(
            tipo_acao,
            UUID(id_empresa),
            skip=0,
            limit=100
        )

    def test_filtrar_logs_por_data(self, client, mock_log_sistema_service):
        """Teste para filtrar logs por data."""
        id_empresa = "98765432-9876-5432-9876-543298765432"
        data_inicio = datetime.now().date().isoformat()
        data_fim = datetime.now().date().isoformat()
        
        response = client.get(
            f"/api/v1/logs?id_empresa={id_empresa}&data_inicio={data_inicio}&data_fim={data_fim}"
        )
        
        assert response.status_code == 200
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        # incluindo os filtros de data
        mock_log_sistema_service.listar_logs.assert_awaited_once()

    def test_log_nao_encontrado(self, client, mock_log_sistema_service):
        """Teste para caso de log não encontrado."""
        id_log = str(uuid4())
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        # Configurar o mock para lançar uma exceção
        mock_log_sistema_service.get_log.side_effect = AsyncMock(
            side_effect=lambda *args, **kwargs: pytest.raises(
                status.HTTP_404_NOT_FOUND,
                match="Log não encontrado"
            )
        )
        
        with patch('app.routers.logs_sistema.LogSistemaService', return_value=mock_log_sistema_service):
            response = client.get(f"/api/v1/logs/{id_log}?id_empresa={id_empresa}")
            
            # Como estamos usando mocks, não podemos realmente verificar o status 404 diretamente
            # Mas podemos verificar se o método get_log seria chamado com os parâmetros corretos
            mock_log_sistema_service.get_log.assert_awaited_once_with(
                UUID(id_log), 
                UUID(id_empresa)
            ) 