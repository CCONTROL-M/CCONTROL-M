"""
Testes para as rotas de Cliente com validação avançada.

Verifica o comportamento das APIs para operações CRUD de clientes.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
import json
from datetime import date, datetime

from app.main import app
from app.schemas.cliente_validado import ClienteResponse, SituacaoCliente


@pytest.fixture
def mock_db():
    """Mock para a sessão do banco de dados."""
    return AsyncMock()


@pytest.fixture
def mock_current_user():
    """Mock para o usuário autenticado."""
    user = MagicMock()
    user.id = 1
    user.email = "teste@exemplo.com"
    user.nome = "Usuário Teste"
    user.empresa_id = 1
    return user


@pytest.fixture
def auth_client(mock_db, mock_current_user):
    """Cliente de teste com autenticação simulada."""
    client = TestClient(app)
    
    # Patch para simular autenticação e dependências
    with patch('app.routers.clientes_router.get_db', return_value=mock_db), \
         patch('app.routers.clientes_router.get_current_user_with_permissions', 
               return_value=lambda perms: lambda: mock_current_user), \
         patch('app.routers.clientes_router.log_sensitive_operation', new_callable=AsyncMock):
        yield client


class TestClientesRouter:
    """Testes para o router de clientes."""

    def test_criar_cliente_valido(self, auth_client):
        """Testa a criação de cliente com dados válidos."""
        cliente_data = {
            "tipo": "pessoa_fisica",
            "nome": "João da Silva",
            "documento": "123.456.789-00",
            "data_nascimento": "1990-01-01",
            "limite_credito": 1000.0,
            "situacao": "ativo",
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True
                },
                {
                    "tipo": "email",
                    "valor": "joao@exemplo.com",
                    "principal": False
                }
            ]
        }
        
        response = auth_client.post("/api/v1/clientes", json=cliente_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["nome"] == "João da Silva"
        assert data["documento"] == "123.456.789-00"
        assert data["tipo"] == "pessoa_fisica"
        assert len(data["enderecos"]) == 1
        assert len(data["contatos"]) == 2

    def test_criar_cliente_invalido(self, auth_client):
        """Testa a criação de cliente com dados inválidos."""
        # Cliente com documento inválido
        cliente_data = {
            "tipo": "pessoa_fisica",
            "nome": "João da Silva",
            "documento": "123.456.789-XX",  # CPF inválido
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True
                }
            ]
        }
        
        response = auth_client.post("/api/v1/clientes", json=cliente_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_criar_cliente_com_ataque(self, auth_client):
        """Testa a criação de cliente com tentativa de ataque."""
        cliente_data = {
            "tipo": "pessoa_fisica",
            "nome": "Cliente<script>alert('XSS')</script>",  # XSS no nome
            "documento": "123.456.789-00",
            "enderecos": [
                {
                    "logradouro": "Rua de Teste",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "uf": "SP",
                    "cep": "01234567",
                    "principal": True
                }
            ],
            "contatos": [
                {
                    "tipo": "celular",
                    "valor": "(11) 98765-4321",
                    "principal": True
                }
            ]
        }
        
        response = auth_client.post("/api/v1/clientes", json=cliente_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        # Verifica se o XSS foi sanitizado
        assert data["nome"] == "Clientescriptalertxssscript"
        assert "<script>" not in data["nome"]

    def test_listar_clientes(self, auth_client):
        """Testa a listagem de clientes."""
        response = auth_client.get("/api/v1/clientes")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "nome" in data[0]
        assert "documento" in data[0]
        assert "tipo" in data[0]

    def test_listar_clientes_com_filtro(self, auth_client):
        """Testa a listagem de clientes com filtros."""
        response = auth_client.get("/api/v1/clientes?situacao=ativo&nome=teste")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)

    def test_obter_cliente(self, auth_client):
        """Testa a obtenção de um cliente específico."""
        cliente_id = 1
        response = auth_client.get(f"/api/v1/clientes/{cliente_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == cliente_id
        assert "nome" in data
        assert "documento" in data
        assert "enderecos" in data
        assert "contatos" in data

    def test_atualizar_cliente(self, auth_client):
        """Testa a atualização de um cliente."""
        cliente_id = 1
        update_data = {
            "nome": "João da Silva Atualizado",
            "situacao": "inadimplente"
        }
        
        response = auth_client.put(f"/api/v1/clientes/{cliente_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == cliente_id
        assert data["nome"] == "João da Silva Atualizado"
        assert data["situacao"] == "inadimplente"

    def test_atualizar_cliente_invalido(self, auth_client):
        """Testa a atualização de um cliente com dados inválidos."""
        cliente_id = 1
        update_data = {
            "nome": "Jo",  # Nome muito curto
            "situacao": "invalido"  # Situação inválida
        }
        
        response = auth_client.put(f"/api/v1/clientes/{cliente_id}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_excluir_cliente(self, auth_client):
        """Testa a exclusão de um cliente."""
        cliente_id = 1
        response = auth_client.delete(f"/api/v1/clientes/{cliente_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT 