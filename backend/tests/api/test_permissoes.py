"""Testes para os endpoints do módulo de permissões."""
import json
import pytest
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, List, Any
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.schemas.token import TokenPayload
from app.services.permissao_service import PermissaoService


@pytest.fixture
def valid_permissao_data():
    """Fixture que retorna dados válidos para criação de permissão."""
    return {
        "nome": "gerenciar_usuarios",
        "descricao": "Gerenciar usuários do sistema",
        "recursos": ["usuarios"],
        "acoes": ["criar", "editar", "visualizar", "listar", "excluir"],
        "id_empresa": str(uuid4())
    }


@pytest.fixture
def valid_permissao_usuario_data():
    """Fixture que retorna dados válidos para atribuição de permissão a usuário."""
    return {
        "usuario_id": str(uuid4()),
        "permissao_id": str(uuid4()),
        "id_empresa": str(uuid4())
    }


async def test_criar_permissao(client: TestClient, mock_auth, valid_permissao_data, monkeypatch):
    """Teste para criação de permissão."""
    # Mock do serviço de permissões
    async def mock_create(*args, **kwargs):
        return {
            "id": str(uuid4()),
            **valid_permissao_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(PermissaoService, "create", mock_create)
    
    # Realizar requisição
    response = client.post(
        "/api/v1/permissoes",
        json=valid_permissao_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "id" in data
    assert data["nome"] == valid_permissao_data["nome"]
    assert sorted(data["acoes"]) == sorted(valid_permissao_data["acoes"])


async def test_listar_permissoes(client: TestClient, mock_auth, monkeypatch):
    """Teste para listagem de permissões."""
    empresa_id = str(uuid4())
    
    # Mock do serviço de permissões
    async def mock_list(*args, **kwargs):
        permissoes = [
            {
                "id": str(uuid4()),
                "nome": "gerenciar_usuarios",
                "descricao": "Gerenciar usuários do sistema",
                "recursos": ["usuarios"],
                "acoes": ["criar", "editar", "visualizar", "listar", "excluir"],
                "id_empresa": empresa_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid4()),
                "nome": "gerenciar_financeiro",
                "descricao": "Gerenciar módulo financeiro",
                "recursos": ["contas", "lancamentos"],
                "acoes": ["criar", "editar", "visualizar", "listar"],
                "id_empresa": empresa_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        return permissoes, len(permissoes)
    
    monkeypatch.setattr(PermissaoService, "list", mock_list)
    
    # Realizar requisição
    response = client.get(
        f"/api/v1/permissoes?id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 2
    assert data["total"] == 2


async def test_obter_permissao_por_id(client: TestClient, mock_auth, monkeypatch):
    """Teste para obtenção de permissão por ID."""
    permissao_id = str(uuid4())
    empresa_id = str(uuid4())
    
    # Mock do serviço de permissões
    async def mock_get_by_id(*args, **kwargs):
        return {
            "id": permissao_id,
            "nome": "gerenciar_usuarios",
            "descricao": "Gerenciar usuários do sistema",
            "recursos": ["usuarios"],
            "acoes": ["criar", "editar", "visualizar", "listar", "excluir"],
            "id_empresa": empresa_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(PermissaoService, "get_by_id", mock_get_by_id)
    
    # Realizar requisição
    response = client.get(
        f"/api/v1/permissoes/{permissao_id}?id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == permissao_id
    assert data["id_empresa"] == empresa_id


async def test_atribuir_permissao_usuario(client: TestClient, mock_auth, valid_permissao_usuario_data, monkeypatch):
    """Teste para atribuir permissão a usuário."""
    # Mock do serviço de permissões
    async def mock_atribuir(*args, **kwargs):
        return {
            "id": str(uuid4()),
            **valid_permissao_usuario_data,
            "created_at": datetime.now().isoformat()
        }
    
    monkeypatch.setattr(PermissaoService, "atribuir_permissao_usuario", mock_atribuir)
    
    # Realizar requisição
    response = client.post(
        "/api/v1/permissoes/atribuir",
        json=valid_permissao_usuario_data,
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "id" in data
    assert data["usuario_id"] == valid_permissao_usuario_data["usuario_id"]
    assert data["permissao_id"] == valid_permissao_usuario_data["permissao_id"]


async def test_remover_permissao_usuario(client: TestClient, mock_auth, monkeypatch):
    """Teste para remover permissão de usuário."""
    usuario_id = str(uuid4())
    permissao_id = str(uuid4())
    empresa_id = str(uuid4())
    
    # Mock do serviço de permissões
    async def mock_remover(*args, **kwargs):
        return {"success": True, "message": "Permissão removida com sucesso"}
    
    monkeypatch.setattr(PermissaoService, "remover_permissao_usuario", mock_remover)
    
    # Realizar requisição
    response = client.delete(
        f"/api/v1/permissoes/remover?usuario_id={usuario_id}&permissao_id={permissao_id}&id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["success"] is True


async def test_listar_permissoes_usuario(client: TestClient, mock_auth, monkeypatch):
    """Teste para listar permissões de um usuário."""
    usuario_id = str(uuid4())
    empresa_id = str(uuid4())
    
    # Mock do serviço de permissões
    async def mock_listar_usuario(*args, **kwargs):
        return [
            {
                "id": str(uuid4()),
                "nome": "gerenciar_usuarios",
                "descricao": "Gerenciar usuários do sistema",
                "recursos": ["usuarios"],
                "acoes": ["criar", "editar", "visualizar", "listar", "excluir"],
                "id_empresa": empresa_id
            },
            {
                "id": str(uuid4()),
                "nome": "gerenciar_financeiro",
                "descricao": "Gerenciar módulo financeiro",
                "recursos": ["contas", "lancamentos"],
                "acoes": ["criar", "editar", "visualizar", "listar"],
                "id_empresa": empresa_id
            }
        ]
    
    monkeypatch.setattr(PermissaoService, "listar_permissoes_usuario", mock_listar_usuario)
    
    # Realizar requisição
    response = client.get(
        f"/api/v1/permissoes/usuario/{usuario_id}?id_empresa={empresa_id}",
        headers={"Authorization": f"Bearer {mock_auth}"}
    )
    
    # Validar resposta
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2 