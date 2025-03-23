"""Testes para os endpoints do módulo de compras."""
import json
import pytest
from uuid import uuid4, UUID
from datetime import date, datetime
from typing import Dict, List, Any
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.schemas.token import TokenPayload
from app.services.compra_service import CompraService


@pytest.fixture
def valid_compra_data():
    """Fixture que retorna dados válidos para criação de compra."""
    return {
        "data_compra": str(date.today()),
        "valor_total": 150.75,
        "status": "CONCLUIDA",
        "observacoes": "Compra de materiais de escritório",
        "fornecedor_id": str(uuid4()),
        "id_empresa": str(uuid4()),
        "itens": [
            {
                "produto_id": str(uuid4()),
                "quantidade": 2,
                "valor_unitario": 45.50,
                "desconto": 0,
                "valor_total": 91.00
            },
            {
                "produto_id": str(uuid4()),
                "quantidade": 3,
                "valor_unitario": 19.25,
                "desconto": 0,
                "valor_total": 57.75
            }
        ]
    }


async def test_criar_compra(client: TestClient, mock_auth, valid_compra_data, monkeypatch):
    """Teste para criação de compra."""
    # Mock do serviço de compras
    async def mock_create(*args, **kwargs):
        return {
            "id": str(uuid4()),
            **valid_compra_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(CompraService, "create", mock_create)
    
    # Realizar requisição
    response = client.post(
        "/api/v1/compras",
        json=valid_compra_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "id" in data
    assert data["valor_total"] == valid_compra_data["valor_total"]
    assert len(data["itens"]) == len(valid_compra_data["itens"])


async def test_listar_compras(client: TestClient, mock_auth, monkeypatch):
    """Teste para listagem de compras."""
    # Mock do serviço de compras
    async def mock_list(*args, **kwargs):
        compras = [
            {
                "id": str(uuid4()),
                "data_compra": str(date.today()),
                "valor_total": 150.75,
                "status": "CONCLUIDA",
                "observacoes": "Compra 1",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "fornecedor_id": str(uuid4()),
                "id_empresa": str(uuid4())
            },
            {
                "id": str(uuid4()),
                "data_compra": str(date.today()),
                "valor_total": 299.90,
                "status": "PENDENTE",
                "observacoes": "Compra 2",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "fornecedor_id": str(uuid4()),
                "id_empresa": str(uuid4())
            }
        ]
        return compras, len(compras)
    
    monkeypatch.setattr(CompraService, "list", mock_list)
    
    # Realizar requisição
    response = client.get(
        "/api/v1/compras?id_empresa=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2
    assert data["total"] == 2


async def test_obter_compra_por_id(client: TestClient, mock_auth, monkeypatch):
    """Teste para obtenção de compra por ID."""
    compra_id = str(uuid4())
    empresa_id = str(uuid4())
    
    # Mock do serviço de compras
    async def mock_get_by_id(*args, **kwargs):
        return {
            "id": compra_id,
            "data_compra": str(date.today()),
            "valor_total": 150.75,
            "status": "CONCLUIDA",
            "observacoes": "Compra de materiais",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "fornecedor_id": str(uuid4()),
            "id_empresa": empresa_id,
            "itens": [
                {
                    "id": str(uuid4()),
                    "produto_id": str(uuid4()),
                    "quantidade": 2,
                    "valor_unitario": 45.50,
                    "desconto": 0,
                    "valor_total": 91.00
                }
            ]
        }
    
    monkeypatch.setattr(CompraService, "get_by_id", mock_get_by_id)
    
    # Realizar requisição
    response = client.get(
        f"/api/v1/compras/{compra_id}?id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == compra_id
    assert data["id_empresa"] == empresa_id
    assert "itens" in data


async def test_atualizar_compra(client: TestClient, mock_auth, monkeypatch):
    """Teste para atualização de compra."""
    compra_id = str(uuid4())
    empresa_id = str(uuid4())
    
    update_data = {
        "status": "CANCELADA",
        "observacoes": "Compra cancelada por falta de estoque"
    }
    
    # Mock do serviço de compras
    async def mock_update(*args, **kwargs):
        return {
            "id": compra_id,
            "data_compra": str(date.today()),
            "valor_total": 150.75,
            "status": update_data["status"],
            "observacoes": update_data["observacoes"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "fornecedor_id": str(uuid4()),
            "id_empresa": empresa_id
        }
    
    monkeypatch.setattr(CompraService, "update", mock_update)
    
    # Realizar requisição
    response = client.put(
        f"/api/v1/compras/{compra_id}?id_empresa={empresa_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == update_data["status"]
    assert data["observacoes"] == update_data["observacoes"]


async def test_excluir_compra(client: TestClient, mock_auth, monkeypatch):
    """Teste para exclusão de compra."""
    compra_id = str(uuid4())
    empresa_id = str(uuid4())
    
    # Mock do serviço de compras
    async def mock_delete(*args, **kwargs):
        return True
    
    monkeypatch.setattr(CompraService, "delete", mock_delete)
    
    # Realizar requisição
    response = client.delete(
        f"/api/v1/compras/{compra_id}?id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["message"] == "Compra removida com sucesso" 