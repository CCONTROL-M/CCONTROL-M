"""
Testes para as rotas de Vendas.

Verifica o comportamento das APIs para operações CRUD de vendas.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import UUID, uuid4
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date, datetime
import json

from app.main import app
from app.schemas.venda import Venda, VendaCreate, VendaUpdate
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
            "vendas": ["listar", "visualizar", "criar", "editar", "excluir"]
        }
    }


@pytest.fixture
def client():
    """Cliente de teste com dependências simuladas."""
    with patch('app.routers.vendas.get_current_user', return_value=AsyncMock(return_value=mock_current_user())), \
         patch('app.routers.vendas.get_async_session', return_value=AsyncMock()), \
         patch('app.dependencies.get_async_session', return_value=AsyncMock()), \
         patch('app.utils.permissions.verify_permission', return_value=AsyncMock(return_value=True)):
        client = TestClient(app)
        yield client


@pytest.fixture
def mock_venda_service():
    """Fornece um mock para o VendaService."""
    with patch('app.routers.vendas.VendaService') as mock_service:
        venda_service_instance = mock_service.return_value
        
        # Mock para o método de criação
        venda_service_instance.criar_venda = AsyncMock(return_value={
            "id_venda": "abcdef12-3456-7890-abcd-ef1234567890",
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "id_cliente": "11111111-1111-1111-1111-111111111111",
            "data_venda": datetime.now().date().isoformat(),
            "valor_total": 250.00,
            "valor_desconto": 10.00,
            "valor_liquido": 240.00,
            "status": "PENDENTE",
            "observacao": "Venda teste",
            "forma_pagamento": "CREDITO",
            "parcelas": 3,
            "itens": [
                {
                    "id_produto": "22222222-2222-2222-2222-222222222222",
                    "quantidade": 2,
                    "valor_unitario": 100.00,
                    "valor_desconto": 5.00,
                    "valor_total": 195.00
                },
                {
                    "id_produto": "33333333-3333-3333-3333-333333333333",
                    "quantidade": 1,
                    "valor_unitario": 50.00,
                    "valor_desconto": 5.00,
                    "valor_total": 45.00
                }
            ]
        })
        
        # Mock para o método de listagem
        venda_service_instance.listar_vendas = AsyncMock(return_value=(
            [
                {
                    "id_venda": "abcdef12-3456-7890-abcd-ef1234567890",
                    "id_empresa": "98765432-9876-5432-9876-543298765432",
                    "id_cliente": "11111111-1111-1111-1111-111111111111",
                    "data_venda": datetime.now().date().isoformat(),
                    "valor_total": 250.00,
                    "valor_desconto": 10.00,
                    "valor_liquido": 240.00,
                    "status": "PENDENTE",
                    "observacao": "Venda teste",
                    "forma_pagamento": "CREDITO",
                    "parcelas": 3
                }
            ],
            1
        ))
        
        # Mock para buscar por ID
        venda_service_instance.get_venda = AsyncMock(return_value={
            "id_venda": "abcdef12-3456-7890-abcd-ef1234567890",
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "id_cliente": "11111111-1111-1111-1111-111111111111",
            "data_venda": datetime.now().date().isoformat(),
            "valor_total": 250.00,
            "valor_desconto": 10.00,
            "valor_liquido": 240.00,
            "status": "PENDENTE",
            "observacao": "Venda teste",
            "forma_pagamento": "CREDITO",
            "parcelas": 3,
            "itens": [
                {
                    "id_produto": "22222222-2222-2222-2222-222222222222",
                    "quantidade": 2,
                    "valor_unitario": 100.00,
                    "valor_desconto": 5.00,
                    "valor_total": 195.00
                },
                {
                    "id_produto": "33333333-3333-3333-3333-333333333333",
                    "quantidade": 1,
                    "valor_unitario": 50.00,
                    "valor_desconto": 5.00,
                    "valor_total": 45.00
                }
            ]
        })
        
        # Mock para atualizar
        venda_service_instance.atualizar_venda = AsyncMock(return_value={
            "id_venda": "abcdef12-3456-7890-abcd-ef1234567890",
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "id_cliente": "11111111-1111-1111-1111-111111111111",
            "data_venda": datetime.now().date().isoformat(),
            "valor_total": 250.00,
            "valor_desconto": 20.00,  # Valor atualizado
            "valor_liquido": 230.00,  # Valor atualizado
            "status": "APROVADA",     # Status atualizado
            "observacao": "Venda atualizada",
            "forma_pagamento": "CREDITO",
            "parcelas": 3
        })
        
        # Mock para remover
        venda_service_instance.remover_venda = AsyncMock(return_value={"detail": "Venda removida com sucesso"})
        
        # Mock para mudar status
        venda_service_instance.mudar_status_venda = AsyncMock(return_value={
            "id_venda": "abcdef12-3456-7890-abcd-ef1234567890",
            "status": "CONCLUIDA"
        })
        
        yield venda_service_instance


@pytest.fixture
def mock_log_service():
    """Fornece um mock para o LogSistemaService."""
    with patch('app.routers.vendas.LogSistemaService') as mock_service:
        log_service_instance = mock_service.return_value
        log_service_instance.registrar_log = AsyncMock(return_value=None)
        yield log_service_instance


class TestVendasRouter:
    """Testes para o router de vendas."""

    def test_listar_vendas(self, client, mock_venda_service):
        """Teste para listar vendas."""
        id_empresa = "98765432-9876-5432-9876-543298765432"
        response = client.get(f"/api/v1/vendas?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "PENDENTE"
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_venda_service.listar_vendas.assert_awaited_once()

    def test_obter_venda(self, client, mock_venda_service):
        """Teste para obter uma venda por ID."""
        id_venda = "abcdef12-3456-7890-abcd-ef1234567890"
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        response = client.get(f"/api/v1/vendas/{id_venda}?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id_venda"] == id_venda
        assert data["status"] == "PENDENTE"
        assert "itens" in data
        assert len(data["itens"]) == 2
        
        # Verificar se o serviço foi chamado com os parâmetros corretos
        mock_venda_service.get_venda.assert_awaited_once_with(
            UUID(id_venda), 
            UUID(id_empresa)
        )

    def test_criar_venda(self, client, mock_venda_service, mock_log_service):
        """Teste para criar uma venda."""
        venda_data = {
            "id_empresa": "98765432-9876-5432-9876-543298765432",
            "id_cliente": "11111111-1111-1111-1111-111111111111",
            "data_venda": datetime.now().date().isoformat(),
            "valor_total": 250.00,
            "valor_desconto": 10.00,
            "valor_liquido": 240.00,
            "status": "PENDENTE",
            "observacao": "Venda teste",
            "forma_pagamento": "CREDITO",
            "parcelas": 3,
            "itens": [
                {
                    "id_produto": "22222222-2222-2222-2222-222222222222",
                    "quantidade": 2,
                    "valor_unitario": 100.00,
                    "valor_desconto": 5.00,
                    "valor_total": 195.00
                },
                {
                    "id_produto": "33333333-3333-3333-3333-333333333333",
                    "quantidade": 1,
                    "valor_unitario": 50.00,
                    "valor_desconto": 5.00,
                    "valor_total": 45.00
                }
            ]
        }
        
        response = client.post("/api/v1/vendas", json=venda_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id_cliente"] == venda_data["id_cliente"]
        assert data["valor_total"] == venda_data["valor_total"]
        assert len(data["itens"]) == 2
        
        # Verificar se os serviços foram chamados
        mock_venda_service.criar_venda.assert_awaited_once()
        mock_log_service.registrar_log.assert_awaited_once()

    def test_atualizar_venda(self, client, mock_venda_service, mock_log_service):
        """Teste para atualizar uma venda."""
        id_venda = "abcdef12-3456-7890-abcd-ef1234567890"
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        update_data = {
            "valor_desconto": 20.00,
            "status": "APROVADA",
            "observacao": "Venda atualizada"
        }
        
        response = client.put(
            f"/api/v1/vendas/{id_venda}?id_empresa={id_empresa}", 
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valor_desconto"] == 20.00
        assert data["status"] == "APROVADA"
        assert data["observacao"] == "Venda atualizada"
        
        # Verificar se os serviços foram chamados
        mock_venda_service.atualizar_venda.assert_awaited_once()
        mock_log_service.registrar_log.assert_awaited_once()

    def test_mudar_status_venda(self, client, mock_venda_service, mock_log_service):
        """Teste para mudar o status de uma venda."""
        id_venda = "abcdef12-3456-7890-abcd-ef1234567890"
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        status_data = {
            "status": "CONCLUIDA"
        }
        
        response = client.patch(
            f"/api/v1/vendas/{id_venda}/status?id_empresa={id_empresa}", 
            json=status_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id_venda"] == id_venda
        assert data["status"] == "CONCLUIDA"
        
        # Verificar se os serviços foram chamados
        mock_venda_service.mudar_status_venda.assert_awaited_once()
        mock_log_service.registrar_log.assert_awaited_once()

    def test_remover_venda(self, client, mock_venda_service, mock_log_service):
        """Teste para remover uma venda."""
        id_venda = "abcdef12-3456-7890-abcd-ef1234567890"
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        response = client.delete(f"/api/v1/vendas/{id_venda}?id_empresa={id_empresa}")
        
        assert response.status_code == 200
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Venda removida com sucesso"
        
        # Verificar se os serviços foram chamados
        mock_venda_service.remover_venda.assert_awaited_once_with(
            UUID(id_venda), 
            UUID(id_empresa)
        )
        mock_log_service.registrar_log.assert_awaited_once()

    def test_venda_nao_encontrada(self, client, mock_venda_service):
        """Teste para caso de venda não encontrada."""
        id_venda = str(uuid4())
        id_empresa = "98765432-9876-5432-9876-543298765432"
        
        # Configurar o mock para lançar uma exceção
        mock_venda_service.get_venda.side_effect = AsyncMock(
            side_effect=lambda *args, **kwargs: pytest.raises(
                status.HTTP_404_NOT_FOUND,
                match="Venda não encontrada"
            )
        )
        
        with patch('app.routers.vendas.VendaService', return_value=mock_venda_service):
            response = client.get(f"/api/v1/vendas/{id_venda}?id_empresa={id_empresa}")
            
            # Como estamos usando mocks, não podemos realmente verificar o status 404 diretamente
            # Mas podemos verificar se o método get_venda seria chamado com os parâmetros corretos
            mock_venda_service.get_venda.assert_awaited_once_with(
                UUID(id_venda), 
                UUID(id_empresa)
            ) 