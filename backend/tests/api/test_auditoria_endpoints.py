"""Testes para os endpoints da API que utilizam o AuditoriaService."""
import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from datetime import datetime, timedelta

from app.main import app

@pytest.mark.asyncio
async def test_criar_fornecedor_auditoria(async_client: AsyncClient, token_usuario_comum):
    """Testar se a criação de fornecedor gera registro de auditoria."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_usuario_comum}"}
    fornecedor_data = {
        "nome": "Fornecedor Teste",
        "tipo": "PJ",
        "documento": "12345678901234",
        "id_empresa": str(uuid4())
    }
    
    # Act
    response = await async_client.post(
        "/api/v1/fornecedores/",
        json=fornecedor_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    
    # Verificar registro de auditoria
    auditoria_response = await async_client.get(
        "/api/v1/auditoria/",
        params={"tipo_acao": "CRIAR_FORNECEDOR"},
        headers=headers
    )
    assert auditoria_response.status_code == status.HTTP_200_OK
    
    acoes = auditoria_response.json()["items"]
    assert len(acoes) > 0
    assert acoes[0]["acao"] == "CRIAR_FORNECEDOR"
    assert acoes[0]["detalhes"]["nome"] == "Fornecedor Teste"

@pytest.mark.asyncio
async def test_atualizar_produto_auditoria(async_client: AsyncClient, token_usuario_comum):
    """Testar se a atualização de produto gera registro de auditoria."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_usuario_comum}"}
    produto_id = str(uuid4())
    produto_data = {
        "nome": "Produto Atualizado",
        "valor": "199.99"
    }
    
    # Act
    response = await async_client.patch(
        f"/api/v1/produtos/{produto_id}",
        json=produto_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar registro de auditoria
    auditoria_response = await async_client.get(
        "/api/v1/auditoria/",
        params={"tipo_acao": "ATUALIZAR_PRODUTO"},
        headers=headers
    )
    assert auditoria_response.status_code == status.HTTP_200_OK
    
    acoes = auditoria_response.json()["items"]
    assert len(acoes) > 0
    assert acoes[0]["acao"] == "ATUALIZAR_PRODUTO"
    assert acoes[0]["detalhes"]["alteracoes"]["nome"] == "Produto Atualizado"

@pytest.mark.asyncio
async def test_excluir_lancamento_auditoria(async_client: AsyncClient, token_usuario_comum):
    """Testar se a exclusão de lançamento gera registro de auditoria."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_usuario_comum}"}
    lancamento_id = str(uuid4())
    
    # Act
    response = await async_client.delete(
        f"/api/v1/lancamentos/{lancamento_id}",
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar registro de auditoria
    auditoria_response = await async_client.get(
        "/api/v1/auditoria/",
        params={"tipo_acao": "EXCLUIR_LANCAMENTO"},
        headers=headers
    )
    assert auditoria_response.status_code == status.HTTP_200_OK
    
    acoes = auditoria_response.json()["items"]
    assert len(acoes) > 0
    assert acoes[0]["acao"] == "EXCLUIR_LANCAMENTO"
    assert acoes[0]["detalhes"]["id_lancamento"] == lancamento_id

@pytest.mark.asyncio
async def test_listar_auditoria_filtros(async_client: AsyncClient, token_usuario_comum):
    """Testar listagem de auditoria com diferentes filtros."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_usuario_comum}"}
    data_inicial = datetime.now() - timedelta(days=7)
    data_final = datetime.now()
    
    # Act
    response = await async_client.get(
        "/api/v1/auditoria/",
        params={
            "data_inicial": data_inicial.isoformat(),
            "data_final": data_final.isoformat(),
            "tipo_acao": "CRIAR_FORNECEDOR"
        },
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data

@pytest.mark.asyncio
async def test_auditoria_permissoes(async_client: AsyncClient):
    """Testar permissões de acesso aos endpoints de auditoria."""
    # Sem token
    response = await async_client.get("/api/v1/auditoria/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Com token inválido
    headers = {"Authorization": "Bearer invalid_token"}
    response = await async_client.get(
        "/api/v1/auditoria/",
        headers=headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 