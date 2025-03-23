"""Testes para os endpoints do módulo de parcelas."""
import json
import pytest
from uuid import uuid4, UUID
from datetime import date, datetime, timedelta
from typing import Dict, List, Any
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.schemas.token import TokenPayload
from app.services.parcela_service import ParcelaService


@pytest.fixture
def valid_parcela_data():
    """Fixture que retorna dados válidos para criação de parcela."""
    return {
        "numero": 1,
        "valor": 250.00,
        "data_vencimento": (date.today() + timedelta(days=30)).isoformat(),
        "status": "PENDENTE",
        "id_venda": str(uuid4()),
        "id_empresa": str(uuid4()),
        "forma_pagamento_id": str(uuid4())
    }


async def test_criar_parcela(client: TestClient, mock_auth, valid_parcela_data, monkeypatch):
    """Teste para criação de parcela."""
    # Mock do serviço de parcelas
    async def mock_create(*args, **kwargs):
        return {
            "id": str(uuid4()),
            **valid_parcela_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(ParcelaService, "create", mock_create)
    
    # Realizar requisição
    response = client.post(
        "/api/v1/parcelas",
        json=valid_parcela_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "id" in data
    assert data["valor"] == valid_parcela_data["valor"]
    assert data["status"] == valid_parcela_data["status"]


async def test_listar_parcelas(client: TestClient, mock_auth, monkeypatch):
    """Teste para listagem de parcelas."""
    empresa_id = str(uuid4())
    venda_id = str(uuid4())
    
    # Mock do serviço de parcelas
    async def mock_list(*args, **kwargs):
        parcelas = [
            {
                "id": str(uuid4()),
                "numero": 1,
                "valor": 250.00,
                "data_vencimento": (date.today() + timedelta(days=30)).isoformat(),
                "status": "PENDENTE",
                "id_venda": venda_id,
                "id_empresa": empresa_id,
                "forma_pagamento_id": str(uuid4()),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid4()),
                "numero": 2,
                "valor": 250.00,
                "data_vencimento": (date.today() + timedelta(days=60)).isoformat(),
                "status": "PENDENTE",
                "id_venda": venda_id,
                "id_empresa": empresa_id,
                "forma_pagamento_id": str(uuid4()),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        return parcelas, len(parcelas)
    
    monkeypatch.setattr(ParcelaService, "list", mock_list)
    
    # Realizar requisição
    response = client.get(
        f"/api/v1/parcelas?id_empresa={empresa_id}&id_venda={venda_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2
    assert data["total"] == 2


async def test_obter_parcela_por_id(client: TestClient, mock_auth, monkeypatch):
    """Teste para obtenção de parcela por ID."""
    parcela_id = str(uuid4())
    empresa_id = str(uuid4())
    
    # Mock do serviço de parcelas
    async def mock_get_by_id(*args, **kwargs):
        return {
            "id": parcela_id,
            "numero": 1,
            "valor": 250.00,
            "data_vencimento": (date.today() + timedelta(days=30)).isoformat(),
            "status": "PENDENTE",
            "id_venda": str(uuid4()),
            "id_empresa": empresa_id,
            "forma_pagamento_id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(ParcelaService, "get_by_id", mock_get_by_id)
    
    # Realizar requisição
    response = client.get(
        f"/api/v1/parcelas/{parcela_id}?id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == parcela_id
    assert data["id_empresa"] == empresa_id


async def test_registrar_pagamento_parcela(client: TestClient, mock_auth, monkeypatch):
    """Teste para registrar pagamento de parcela."""
    parcela_id = str(uuid4())
    empresa_id = str(uuid4())
    
    pagamento_data = {
        "data_pagamento": date.today().isoformat(),
        "valor_pago": 250.00,
        "forma_pagamento_id": str(uuid4()),
        "observacoes": "Pagamento realizado via PIX"
    }
    
    # Mock do serviço de parcelas
    async def mock_pagar(*args, **kwargs):
        return {
            "id": parcela_id,
            "numero": 1,
            "valor": 250.00,
            "data_vencimento": (date.today() - timedelta(days=5)).isoformat(),
            "data_pagamento": pagamento_data["data_pagamento"],
            "valor_pago": pagamento_data["valor_pago"],
            "status": "PAGO",
            "id_venda": str(uuid4()),
            "id_empresa": empresa_id,
            "forma_pagamento_id": pagamento_data["forma_pagamento_id"],
            "observacoes": pagamento_data["observacoes"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(ParcelaService, "registrar_pagamento", mock_pagar)
    
    # Realizar requisição
    response = client.post(
        f"/api/v1/parcelas/{parcela_id}/pagar?id_empresa={empresa_id}",
        json=pagamento_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "PAGO"
    assert data["data_pagamento"] == pagamento_data["data_pagamento"]
    assert data["valor_pago"] == pagamento_data["valor_pago"]


async def test_cancelar_parcela(client: TestClient, mock_auth, monkeypatch):
    """Teste para cancelar parcela."""
    parcela_id = str(uuid4())
    empresa_id = str(uuid4())
    
    cancelamento_data = {
        "motivo_cancelamento": "Cliente cancelou a compra",
        "observacoes": "Será emitido reembolso"
    }
    
    # Mock do serviço de parcelas
    async def mock_cancelar(*args, **kwargs):
        return {
            "id": parcela_id,
            "numero": 1,
            "valor": 250.00,
            "data_vencimento": (date.today() + timedelta(days=30)).isoformat(),
            "status": "CANCELADA",
            "id_venda": str(uuid4()),
            "id_empresa": empresa_id,
            "motivo_cancelamento": cancelamento_data["motivo_cancelamento"],
            "observacoes": cancelamento_data["observacoes"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(ParcelaService, "cancelar", mock_cancelar)
    
    # Realizar requisição
    response = client.post(
        f"/api/v1/parcelas/{parcela_id}/cancelar?id_empresa={empresa_id}",
        json=cancelamento_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "CANCELADA"
    assert data["motivo_cancelamento"] == cancelamento_data["motivo_cancelamento"] 