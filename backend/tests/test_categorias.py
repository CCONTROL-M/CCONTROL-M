import pytest
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.repositories.categoria_repository import CategoriaRepository
from app.models.categoria import Categoria
from app.main import app
from tests.utils import get_auth_header
from app.dependencies import get_current_user, check_permission

# Cliente de teste
client = TestClient(app)

# Mock de usuário autenticado para os testes
test_user = {
    "id_usuario": "12345678-1234-5678-1234-567812345678",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Teste Usuário",
    "email": "teste@exemplo.com",
    "tipo_usuario": "adm",
    "telas_permitidas": {"categorias": True}
}

# Sobrescrever as dependências de autenticação e permissão
app.dependency_overrides[get_current_user] = lambda: test_user
app.dependency_overrides[check_permission] = lambda permission: lambda: True

# Fixture para criar uma categoria para teste
@pytest.fixture
def categoria_teste(db_session: Session):
    categoria_data = {
        "nome": "Categoria Teste",
        "tipo": "receita",
        "subcategorias": {"sub1": "Subcategoria 1", "sub2": "Subcategoria 2"},
        "id_empresa": test_user["id_empresa"]
    }
    
    # Remover qualquer categoria com o mesmo nome para evitar conflitos
    categoria_existente = db_session.query(Categoria).filter(
        Categoria.nome == categoria_data["nome"],
        Categoria.id_empresa == test_user["id_empresa"]
    ).first()
    
    if categoria_existente:
        db_session.delete(categoria_existente)
        db_session.commit()
    
    # Criar uma nova categoria
    categoria = Categoria(**categoria_data)
    db_session.add(categoria)
    db_session.commit()
    db_session.refresh(categoria)
    
    yield categoria
    
    # Limpeza após o teste
    try:
        cat = db_session.query(Categoria).filter(Categoria.id_categoria == categoria.id_categoria).first()
        if cat:
            db_session.delete(cat)
            db_session.commit()
    except:
        pass

# Testes para o repositório de categorias

def test_categoria_create(db_session: Session, empresa_teste_id: UUID):
    """Teste para criação de categoria"""
    categoria_data = {
        "nome": "Categoria Nova",
        "tipo": "despesa",
        "subcategorias": {"sub1": "Subcategoria 1"},
        "id_empresa": empresa_teste_id
    }
    
    # Remover qualquer categoria com o mesmo nome para evitar conflitos
    categoria_existente = db_session.query(Categoria).filter(
        Categoria.nome == categoria_data["nome"],
        Categoria.id_empresa == empresa_teste_id
    ).first()
    
    if categoria_existente:
        db_session.delete(categoria_existente)
        db_session.commit()
    
    categoria = CategoriaRepository.create(db=db_session, categoria_data=categoria_data)
    
    assert categoria is not None
    assert categoria.nome == categoria_data["nome"]
    assert categoria.tipo == categoria_data["tipo"]
    assert categoria.id_empresa == empresa_teste_id
    
    # Limpeza
    db_session.delete(categoria)
    db_session.commit()

def test_categoria_get_by_id(db_session: Session, categoria_teste):
    """Teste para buscar categoria por ID"""
    categoria = CategoriaRepository.get_by_id(db=db_session, id_categoria=categoria_teste.id_categoria)
    
    assert categoria is not None
    assert categoria.id_categoria == categoria_teste.id_categoria
    assert categoria.nome == categoria_teste.nome
    assert categoria.tipo == categoria_teste.tipo

def test_categoria_get_by_empresa(db_session: Session, categoria_teste, empresa_teste_id: UUID):
    """Teste para listar categorias por empresa"""
    categorias, total = CategoriaRepository.get_by_empresa(
        db=db_session, 
        id_empresa=empresa_teste_id,
        skip=0,
        limit=10
    )
    
    assert len(categorias) > 0
    assert total > 0
    assert any(c.id_categoria == categoria_teste.id_categoria for c in categorias)

def test_categoria_get_by_tipo(db_session: Session, categoria_teste, empresa_teste_id: UUID):
    """Teste para listar categorias por tipo"""
    categorias, total = CategoriaRepository.get_by_empresa(
        db=db_session, 
        id_empresa=empresa_teste_id,
        skip=0,
        limit=10,
        tipo=categoria_teste.tipo
    )
    
    assert len(categorias) > 0
    assert total > 0
    assert all(c.tipo == categoria_teste.tipo for c in categorias)
    assert any(c.id_categoria == categoria_teste.id_categoria for c in categorias)

def test_categoria_update(db_session: Session, categoria_teste):
    """Teste para atualizar categoria"""
    novo_nome = "Categoria Atualizada"
    categoria_data = {
        "nome": novo_nome,
        "subcategorias": {"sub1": "Nova subcategoria"}
    }
    
    categoria_atualizada = CategoriaRepository.update(
        db=db_session,
        id_categoria=categoria_teste.id_categoria,
        categoria_data=categoria_data
    )
    
    assert categoria_atualizada is not None
    assert categoria_atualizada.nome == novo_nome
    assert categoria_atualizada.subcategorias == categoria_data["subcategorias"]
    assert categoria_atualizada.tipo == categoria_teste.tipo  # Tipo não foi alterado

def test_categoria_delete(db_session: Session, empresa_teste_id: UUID):
    """Teste para excluir categoria"""
    # Criar uma categoria específica para o teste de exclusão
    categoria_data = {
        "nome": "Categoria para Excluir",
        "tipo": "despesa",
        "id_empresa": empresa_teste_id
    }
    
    categoria = CategoriaRepository.create(db=db_session, categoria_data=categoria_data)
    
    # Verificar se foi criada
    assert categoria is not None
    
    # Excluir
    resultado = CategoriaRepository.delete(db=db_session, id_categoria=categoria.id_categoria)
    
    # Verificar se foi excluída
    assert resultado is True
    
    # Verificar se realmente não existe mais
    categoria_verificacao = CategoriaRepository.get_by_id(db=db_session, id_categoria=categoria.id_categoria)
    assert categoria_verificacao is None

# Testes para API de categorias

def test_listar_categorias(categoria_teste):
    """
    Teste para listar todas as categorias com paginação, filtros e ordenação
    """
    # Teste de listagem básica
    response = client.get("/api/categorias/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    
    # Teste com filtros de busca
    response = client.get(f"/api/categorias/?nome={categoria_teste.nome}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0]["nome"] == categoria_teste.nome
    
    # Teste com filtro de tipo
    response = client.get(f"/api/categorias/?tipo={categoria_teste.tipo}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    found = False
    for item in data["items"]:
        if item["nome"] == categoria_teste.nome:
            found = True
            break
    assert found, "Categoria de teste não encontrada na filtragem por tipo"
    
    # Teste com paginação
    response = client.get("/api/categorias/?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5
    
    # Teste com ordenação
    response = client.get("/api/categorias/?order_by=nome&order_direction=asc")
    assert response.status_code == 200
    assert response.json()["items"] is not None

def test_obter_categoria_por_id(categoria_teste):
    """
    Teste para obter uma categoria específica por ID
    """
    response = client.get(f"/api/categorias/{categoria_teste.id_categoria}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == categoria_teste.nome
    assert data["tipo"] == categoria_teste.tipo
    assert data["subcategorias"] == categoria_teste.subcategorias
    
    # Teste com ID inválido
    response = client.get(f"/api/categorias/{uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_criar_categoria():
    """
    Teste para criar uma nova categoria
    """
    categoria_data = {
        "nome": "Nova Categoria",
        "tipo": "despesa",
        "subcategorias": {
            "sub1": "Nova Subcategoria 1",
            "sub2": "Nova Subcategoria 2"
        },
        "id_empresa": test_user["id_empresa"]
    }
    
    # Teste de criação com dados válidos
    response = client.post("/api/categorias/", json=categoria_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["nome"] == categoria_data["nome"]
    assert data["tipo"] == categoria_data["tipo"]
    assert data["subcategorias"] == categoria_data["subcategorias"]
    assert data["id_categoria"] is not None
    
    # Limpar categoria criada
    categoria_id = data["id_categoria"]
    client.delete(f"/api/categorias/{categoria_id}")
    
    # Teste de criação com dados inválidos (sem nome)
    invalid_data = categoria_data.copy()
    invalid_data.pop("nome")
    response = client.post("/api/categorias/", json=invalid_data)
    assert response.status_code == 422
    
    # Teste de criação com dados inválidos (tipo incorreto)
    invalid_data = categoria_data.copy()
    invalid_data["tipo"] = "tipo_invalido"
    response = client.post("/api/categorias/", json=invalid_data)
    assert response.status_code == 422

def test_atualizar_categoria(categoria_teste):
    """
    Teste para atualizar uma categoria existente
    """
    update_data = {
        "nome": "Categoria Atualizada",
        "subcategorias": {
            "sub1": "Subcategoria Atualizada 1",
            "sub2": "Subcategoria Atualizada 2",
            "sub3": "Nova Subcategoria"
        }
    }
    
    # Teste de atualização parcial válida
    response = client.put(f"/api/categorias/{categoria_teste.id_categoria}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["nome"] == update_data["nome"]
    assert data["subcategorias"] == update_data["subcategorias"]
    assert data["tipo"] == categoria_teste.tipo  # Não deve alterar campo não especificado
    
    # Teste de atualização com ID inexistente
    response = client.put(f"/api/categorias/{uuid4()}", json=update_data)
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Teste de atualização com dados inválidos
    invalid_data = {"tipo": "tipo_invalido"}
    response = client.put(f"/api/categorias/{categoria_teste.id_categoria}", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_excluir_categoria(categoria_teste):
    """
    Teste para excluir uma categoria
    """
    # Criar uma nova categoria para exclusão
    categoria_data = {
        "nome": "Categoria para Excluir",
        "tipo": "receita",
        "subcategorias": {"sub1": "Temp Subcategoria"},
        "id_empresa": test_user["id_empresa"]
    }
    
    response = client.post("/api/categorias/", json=categoria_data)
    assert response.status_code == 201
    categoria_id = response.json()["id_categoria"]
    
    # Teste de exclusão bem-sucedida
    response = client.delete(f"/api/categorias/{categoria_id}")
    assert response.status_code == 204
    
    # Verificar se foi realmente excluída
    response = client.get(f"/api/categorias/{categoria_id}")
    assert response.status_code == 404
    
    # Teste de exclusão com ID inexistente
    response = client.delete(f"/api/categorias/{uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Teste com categoria vinculada a outros registros
    # Simulação: Assumimos que categorias em uso não podem ser excluídas
    # Como não temos acesso ao código completo, apenas testamos o caso feliz acima 