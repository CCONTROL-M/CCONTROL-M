import pytest
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.models.forma_pagamento import FormaPagamento
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
    "telas_permitidas": {"formas_pagamento": True}
}

# Sobrescrever as dependências de autenticação e permissão
app.dependency_overrides[get_current_user] = lambda: test_user
app.dependency_overrides[check_permission] = lambda permission: lambda: True

# Fixture para criar uma forma de pagamento para teste
@pytest.fixture
def forma_pagamento_teste(db_session: Session):
    forma_pagamento_data = {
        "tipo": "Cartão de Crédito Teste",
        "taxas": 2.5,
        "prazo": 30,
        "id_empresa": test_user["id_empresa"]
    }
    
    # Remover qualquer forma de pagamento com o mesmo tipo para evitar conflitos
    forma_existente = db_session.query(FormaPagamento).filter(
        FormaPagamento.tipo == forma_pagamento_data["tipo"],
        FormaPagamento.id_empresa == test_user["id_empresa"]
    ).first()
    
    if forma_existente:
        db_session.delete(forma_existente)
        db_session.commit()
    
    # Criar uma nova forma de pagamento
    forma_pagamento = FormaPagamento(**forma_pagamento_data)
    db_session.add(forma_pagamento)
    db_session.commit()
    db_session.refresh(forma_pagamento)
    
    yield forma_pagamento
    
    # Limpeza após o teste
    try:
        forma = db_session.query(FormaPagamento).filter(FormaPagamento.id_forma == forma_pagamento.id_forma).first()
        if forma:
            db_session.delete(forma)
            db_session.commit()
    except:
        pass

# Testes para o repositório de formas de pagamento

def test_forma_pagamento_create(db_session: Session, empresa_teste_id: UUID):
    """Teste para criação de forma de pagamento"""
    forma_pagamento_data = {
        "tipo": "Boleto Bancário Teste",
        "taxas": 1.0,
        "prazo": 3,
        "id_empresa": empresa_teste_id
    }
    
    # Remover qualquer forma de pagamento com o mesmo tipo para evitar conflitos
    forma_existente = db_session.query(FormaPagamento).filter(
        FormaPagamento.tipo == forma_pagamento_data["tipo"],
        FormaPagamento.id_empresa == empresa_teste_id
    ).first()
    
    if forma_existente:
        db_session.delete(forma_existente)
        db_session.commit()
    
    forma_pagamento = FormaPagamentoRepository.create(db=db_session, forma_pagamento_data=forma_pagamento_data)
    
    assert forma_pagamento is not None
    assert forma_pagamento.tipo == forma_pagamento_data["tipo"]
    assert forma_pagamento.taxas == forma_pagamento_data["taxas"]
    assert forma_pagamento.prazo == forma_pagamento_data["prazo"]
    assert forma_pagamento.id_empresa == empresa_teste_id
    
    # Limpeza
    db_session.delete(forma_pagamento)
    db_session.commit()

def test_forma_pagamento_get_by_id(db_session: Session, forma_pagamento_teste):
    """Teste para buscar forma de pagamento por ID"""
    forma_pagamento = FormaPagamentoRepository.get_by_id(db=db_session, id_forma=forma_pagamento_teste.id_forma)
    
    assert forma_pagamento is not None
    assert forma_pagamento.id_forma == forma_pagamento_teste.id_forma
    assert forma_pagamento.tipo == forma_pagamento_teste.tipo

def test_forma_pagamento_get_by_tipo(db_session: Session, forma_pagamento_teste, empresa_teste_id: UUID):
    """Teste para buscar forma de pagamento por tipo"""
    forma_pagamento = FormaPagamentoRepository.get_by_tipo(
        db=db_session, 
        tipo=forma_pagamento_teste.tipo,
        id_empresa=empresa_teste_id
    )
    
    assert forma_pagamento is not None
    assert forma_pagamento.id_forma == forma_pagamento_teste.id_forma
    assert forma_pagamento.tipo == forma_pagamento_teste.tipo

def test_forma_pagamento_update(db_session: Session, forma_pagamento_teste):
    """Teste para atualizar forma de pagamento"""
    novo_tipo = "Cartão de Débito Teste Atualizado"
    novas_taxas = 1.8
    
    forma_pagamento_atualizada = FormaPagamentoRepository.update(
        db=db_session,
        id_forma=forma_pagamento_teste.id_forma,
        forma_pagamento_data={"tipo": novo_tipo, "taxas": novas_taxas}
    )
    
    assert forma_pagamento_atualizada is not None
    assert forma_pagamento_atualizada.id_forma == forma_pagamento_teste.id_forma
    assert forma_pagamento_atualizada.tipo == novo_tipo
    assert forma_pagamento_atualizada.taxas == novas_taxas

def test_forma_pagamento_delete(db_session: Session, empresa_teste_id: UUID):
    """Teste para excluir forma de pagamento"""
    # Criar uma forma de pagamento específica para teste de exclusão
    forma_pagamento_data = {
        "tipo": "Forma para Exclusão",
        "taxas": 0.0,
        "prazo": 0,
        "id_empresa": empresa_teste_id
    }
    
    forma_pagamento = FormaPagamentoRepository.create(db=db_session, forma_pagamento_data=forma_pagamento_data)
    assert forma_pagamento is not None
    
    # Executar a exclusão
    success = FormaPagamentoRepository.delete(db=db_session, id_forma=forma_pagamento.id_forma)
    assert success is True
    
    # Verificar se foi realmente excluído
    forma_verificacao = FormaPagamentoRepository.get_by_id(db=db_session, id_forma=forma_pagamento.id_forma)
    assert forma_verificacao is None

def test_forma_pagamento_get_by_empresa(db_session: Session, forma_pagamento_teste, empresa_teste_id: UUID):
    """Teste para listar formas de pagamento de uma empresa com paginação"""
    # Criando uma forma de pagamento adicional para teste de listagem
    forma_pagamento_data = {
        "tipo": "Dinheiro Teste",
        "taxas": 0.0,
        "prazo": 0,
        "id_empresa": empresa_teste_id
    }
    
    # Remover qualquer forma de pagamento com o mesmo tipo para evitar conflitos
    forma_existente = db_session.query(FormaPagamento).filter(
        FormaPagamento.tipo == forma_pagamento_data["tipo"],
        FormaPagamento.id_empresa == empresa_teste_id
    ).first()
    
    if forma_existente:
        db_session.delete(forma_existente)
        db_session.commit()
    
    forma_pagamento_extra = FormaPagamentoRepository.create(db=db_session, forma_pagamento_data=forma_pagamento_data)
    
    # Listar formas de pagamento
    formas_pagamento, total = FormaPagamentoRepository.get_by_empresa(
        db=db_session,
        id_empresa=empresa_teste_id,
        skip=0,
        limit=10
    )
    
    assert total >= 2  # Deve ter pelo menos as duas formas de pagamento criadas
    assert len(formas_pagamento) >= 2
    
    # Testar paginação
    formas_pagamento_pag, total_pag = FormaPagamentoRepository.get_by_empresa(
        db=db_session,
        id_empresa=empresa_teste_id,
        skip=0,
        limit=1
    )
    
    assert total_pag >= 2
    assert len(formas_pagamento_pag) == 1
    
    # Testar busca
    formas_pagamento_search, total_search = FormaPagamentoRepository.get_by_empresa(
        db=db_session,
        id_empresa=empresa_teste_id,
        search="Dinheiro"
    )
    
    assert any(fp.tipo == "Dinheiro Teste" for fp in formas_pagamento_search)
    
    # Limpeza
    db_session.delete(forma_pagamento_extra)
    db_session.commit()

# Testes de API
def test_listar_formas_pagamento(forma_pagamento_teste):
    """
    Teste para listar todas as formas de pagamento com paginação, filtros e ordenação
    """
    # Teste de listagem básica
    response = client.get("/api/formas-pagamento/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    
    # Teste com filtros de busca
    response = client.get(f"/api/formas-pagamento/?tipo={forma_pagamento_teste.tipo}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    found = False
    for item in data["items"]:
        if item["tipo"] == forma_pagamento_teste.tipo:
            found = True
            break
    assert found, "Forma de pagamento de teste não encontrada na filtragem por tipo"
    
    # Teste com paginação
    response = client.get("/api/formas-pagamento/?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5
    
    # Teste com ordenação
    response = client.get("/api/formas-pagamento/?order_by=tipo&order_direction=asc")
    assert response.status_code == 200
    assert response.json()["items"] is not None

def test_obter_forma_pagamento_por_id(forma_pagamento_teste):
    """
    Teste para obter uma forma de pagamento específica por ID
    """
    response = client.get(f"/api/formas-pagamento/{forma_pagamento_teste.id_forma}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["tipo"] == forma_pagamento_teste.tipo
    assert float(data["taxas"]) == float(forma_pagamento_teste.taxas)
    assert data["prazo"] == forma_pagamento_teste.prazo
    
    # Teste com ID inválido
    response = client.get(f"/api/formas-pagamento/{uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_criar_forma_pagamento():
    """
    Teste para criar uma nova forma de pagamento
    """
    forma_pagamento_data = {
        "tipo": "Nova Forma de Pagamento",
        "taxas": 1.5,
        "prazo": 15,
        "id_empresa": test_user["id_empresa"]
    }
    
    # Teste de criação com dados válidos
    response = client.post("/api/formas-pagamento/", json=forma_pagamento_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["tipo"] == forma_pagamento_data["tipo"]
    assert float(data["taxas"]) == float(forma_pagamento_data["taxas"])
    assert data["prazo"] == forma_pagamento_data["prazo"]
    assert data["id_forma"] is not None
    
    # Limpar forma de pagamento criada
    forma_id = data["id_forma"]
    client.delete(f"/api/formas-pagamento/{forma_id}")
    
    # Teste de criação com dados inválidos (sem tipo)
    invalid_data = forma_pagamento_data.copy()
    invalid_data.pop("tipo")
    response = client.post("/api/formas-pagamento/", json=invalid_data)
    assert response.status_code == 422
    
    # Teste de criação com dados inválidos (taxas negativas)
    invalid_data = forma_pagamento_data.copy()
    invalid_data["taxas"] = -5.0
    response = client.post("/api/formas-pagamento/", json=invalid_data)
    assert response.status_code == 422

def test_atualizar_forma_pagamento(forma_pagamento_teste):
    """
    Teste para atualizar uma forma de pagamento existente
    """
    update_data = {
        "tipo": "Forma de Pagamento Atualizada",
        "taxas": 3.0
    }
    
    # Teste de atualização parcial válida
    response = client.put(f"/api/formas-pagamento/{forma_pagamento_teste.id_forma}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tipo"] == update_data["tipo"]
    assert float(data["taxas"]) == float(update_data["taxas"])
    assert data["prazo"] == forma_pagamento_teste.prazo  # Não deve alterar campo não especificado
    
    # Teste de atualização com ID inexistente
    response = client.put(f"/api/formas-pagamento/{uuid4()}", json=update_data)
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Teste de atualização com dados inválidos
    invalid_data = {"taxas": -1.0}
    response = client.put(f"/api/formas-pagamento/{forma_pagamento_teste.id_forma}", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_excluir_forma_pagamento(forma_pagamento_teste):
    """
    Teste para excluir uma forma de pagamento
    """
    # Criar uma nova forma de pagamento para exclusão
    forma_pagamento_data = {
        "tipo": "Forma de Pagamento para Excluir",
        "taxas": 1.0,
        "prazo": 10,
        "id_empresa": test_user["id_empresa"]
    }
    
    response = client.post("/api/formas-pagamento/", json=forma_pagamento_data)
    assert response.status_code == 201
    forma_id = response.json()["id_forma"]
    
    # Teste de exclusão bem-sucedida
    response = client.delete(f"/api/formas-pagamento/{forma_id}")
    assert response.status_code == 204
    
    # Verificar se foi realmente excluída
    response = client.get(f"/api/formas-pagamento/{forma_id}")
    assert response.status_code == 404
    
    # Teste de exclusão com ID inexistente
    response = client.delete(f"/api/formas-pagamento/{uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Teste com forma de pagamento vinculada a outros registros (simulação)
    # Supondo que exista uma verificação de uso vinculado
    
    # Simulação: Como não temos acesso ao código completo para verificar a regra exata
    # de validação quando uma forma de pagamento está em uso, apenas testamos o caso
    # básico de exclusão bem-sucedida acima 