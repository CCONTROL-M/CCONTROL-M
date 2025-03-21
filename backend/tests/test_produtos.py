import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID

from app.main import app
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate
from app.services.produto_service import ProdutoService
from app.dependencies import get_current_user
from app.database import get_db
from tests.conftest import override_get_db

# Cliente de teste
client = TestClient(app)

# Mock de usuário autenticado para os testes
test_user = {
    "id_usuario": "12345678-1234-5678-1234-567812345678",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Teste Usuário",
    "email": "teste@exemplo.com",
    "tipo_usuario": "adm",
    "telas_permitidas": {"produtos": True}
}

# Sobrescrever a dependência de autenticação
app.dependency_overrides[get_current_user] = lambda: test_user
app.dependency_overrides[get_db] = override_get_db

# Fixture para criar um produto de teste
@pytest.fixture
def produto_teste(db_session: Session):
    produto_data = ProdutoCreate(
        id_empresa="98765432-9876-5432-9876-543298765432",
        nome="Produto Teste",
        codigo="PROD001",
        descricao="Um produto para testes",
        preco_venda=Decimal("99.99"),
        preco_custo=Decimal("50.00"),
        estoque_atual=Decimal("10.00"),
        estoque_minimo=Decimal("5.00"),
        categoria="Teste",
        ativo=True
    )
    
    produto = ProdutoService.create_produto(db_session, produto_data)
    
    yield produto
    
    # Cleanup - remover o produto após os testes
    db_session.query(Produto).filter(Produto.id_produto == produto.id_produto).delete()
    db_session.commit()

# Testes
def test_criar_produto():
    """Teste de criação de produto"""
    produto_data = {
        "nome": "Produto Novo",
        "codigo": "PROD002",
        "descricao": "Produto criado via API",
        "preco_venda": 149.99,
        "preco_custo": 75.50,
        "estoque_atual": 20,
        "estoque_minimo": 5,
        "categoria": "Teste",
        "ativo": True
    }
    
    response = client.post("/api/produtos/", json=produto_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["nome"] == produto_data["nome"]
    assert data["codigo"] == produto_data["codigo"]
    assert float(data["preco_venda"]) == produto_data["preco_venda"]
    assert data["id_produto"] is not None

def test_obter_produto(produto_teste):
    """Teste para obter um produto por ID"""
    produto_id = str(produto_teste.id_produto)
    response = client.get(f"/api/produtos/{produto_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == produto_teste.nome
    assert float(data["preco_venda"]) == float(produto_teste.preco_venda)

def test_listar_produtos(produto_teste):
    """Teste para listar produtos"""
    response = client.get("/api/produtos/")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # Verificar se o produto de teste está na lista
    produtos = data["items"]
    produto_ids = [p["id_produto"] for p in produtos]
    assert str(produto_teste.id_produto) in produto_ids

def test_atualizar_produto(produto_teste):
    """Teste para atualizar um produto"""
    update_data = {
        "nome": "Produto Atualizado",
        "preco_venda": 129.99
    }
    
    produto_id = str(produto_teste.id_produto)
    response = client.put(f"/api/produtos/{produto_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == update_data["nome"]
    assert float(data["preco_venda"]) == update_data["preco_venda"]
    assert data["codigo"] == produto_teste.codigo  # Campo não alterado

def test_atualizar_estoque(produto_teste):
    """Teste para atualizar o estoque de um produto"""
    estoque_inicial = float(produto_teste.estoque_atual)
    quantidade_adicionar = 5
    
    produto_id = str(produto_teste.id_produto)
    response = client.patch(
        f"/api/produtos/{produto_id}/estoque", 
        json={"quantidade": quantidade_adicionar}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert float(data["estoque_atual"]) == estoque_inicial + quantidade_adicionar

def test_excluir_produto(produto_teste):
    """Teste para excluir um produto"""
    produto_id = str(produto_teste.id_produto)
    response = client.delete(f"/api/produtos/{produto_id}")
    assert response.status_code == 204
    
    # Verificar se o produto foi excluído
    response = client.get(f"/api/produtos/{produto_id}")
    assert response.status_code == 404 