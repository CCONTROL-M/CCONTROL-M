import pytest
from uuid import UUID, uuid4
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.conta_bancaria import ContaBancaria
from app.repositories.conta_bancaria_repository import ContaBancariaRepository
from app.main import app
from app.dependencies import get_current_user, check_permission

# Fixture para criar uma conta bancária para testes
@pytest.fixture
def conta_bancaria_test_data():
    return {
        "banco": "Banco de Teste",
        "agencia": "1234",
        "numero": "12345-6",
        "tipo": "Corrente",
        "saldo_inicial": 1000.0
    }

# Fixture para simular autenticação no teste
@pytest.fixture
def authenticated_client(monkeypatch, test_user):
    # Sobrescrever a função de dependência para retornar um usuário de teste
    monkeypatch.setattr(app, "dependency_overrides", {
        get_current_user: lambda: test_user,
        check_permission: lambda permission: lambda: test_user
    })
    
    # Criar cliente de teste
    client = TestClient(app)
    
    # Retornar cliente e usuário de teste
    return client, test_user

# Testes do repositório
def test_create_conta_bancaria(db_session: Session, test_user, conta_bancaria_test_data):
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": test_user.id_empresa}
    
    # Criar conta bancária
    conta_bancaria = ContaBancariaRepository.create(db=db_session, conta_bancaria_data=conta_data)
    
    # Verificar se a conta bancária foi criada corretamente
    assert conta_bancaria is not None
    assert conta_bancaria.id_conta is not None
    assert isinstance(conta_bancaria.id_conta, UUID)
    assert conta_bancaria.banco == conta_data["banco"]
    assert conta_bancaria.id_empresa == test_user.id_empresa

def test_get_by_id_conta_bancaria(db_session: Session, test_user, conta_bancaria_test_data):
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": test_user.id_empresa}
    
    # Criar conta bancária
    conta_bancaria = ContaBancariaRepository.create(db=db_session, conta_bancaria_data=conta_data)
    
    # Buscar conta bancária por ID
    found_conta = ContaBancariaRepository.get_by_id(db=db_session, id_conta=conta_bancaria.id_conta)
    
    # Verificar se a conta bancária foi encontrada
    assert found_conta is not None
    assert found_conta.id_conta == conta_bancaria.id_conta
    assert found_conta.banco == conta_bancaria.banco

def test_get_by_empresa_conta_bancaria(db_session: Session, test_user, conta_bancaria_test_data):
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": test_user.id_empresa}
    
    # Criar conta bancária
    ContaBancariaRepository.create(db=db_session, conta_bancaria_data=conta_data)
    
    # Buscar contas bancárias da empresa
    contas, total = ContaBancariaRepository.get_by_empresa(
        db=db_session,
        id_empresa=test_user.id_empresa
    )
    
    # Verificar se pelo menos uma conta foi encontrada
    assert total > 0
    assert len(contas) > 0
    assert contas[0].id_empresa == test_user.id_empresa

def test_update_conta_bancaria(db_session: Session, test_user, conta_bancaria_test_data):
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": test_user.id_empresa}
    
    # Criar conta bancária
    conta_bancaria = ContaBancariaRepository.create(db=db_session, conta_bancaria_data=conta_data)
    
    # Atualizar conta bancária
    update_data = {"banco": "Banco Atualizado", "saldo_inicial": 2000.0}
    updated_conta = ContaBancariaRepository.update(
        db=db_session,
        id_conta=conta_bancaria.id_conta,
        conta_bancaria_data=update_data
    )
    
    # Verificar se a conta bancária foi atualizada
    assert updated_conta is not None
    assert updated_conta.id_conta == conta_bancaria.id_conta
    assert updated_conta.banco == "Banco Atualizado"
    assert updated_conta.saldo_inicial == 2000.0
    assert updated_conta.agencia == conta_bancaria.agencia  # Não alterado

def test_delete_conta_bancaria(db_session: Session, test_user, conta_bancaria_test_data):
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": test_user.id_empresa}
    
    # Criar conta bancária
    conta_bancaria = ContaBancariaRepository.create(db=db_session, conta_bancaria_data=conta_data)
    
    # Excluir conta bancária
    result = ContaBancariaRepository.delete(db=db_session, id_conta=conta_bancaria.id_conta)
    
    # Verificar se a exclusão foi bem-sucedida
    assert result is True
    
    # Tentar buscar a conta excluída
    deleted_conta = ContaBancariaRepository.get_by_id(db=db_session, id_conta=conta_bancaria.id_conta)
    
    # Verificar se a conta foi realmente excluída
    assert deleted_conta is None

# Testes de API
def test_create_conta_bancaria_api(authenticated_client, conta_bancaria_test_data):
    client, user = authenticated_client
    
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": str(user.id_empresa)}
    
    # Enviar requisição para criar conta bancária
    response = client.post("/api/contas-bancarias/", json=conta_data)
    
    # Verificar se a resposta está correta
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["banco"] == conta_data["banco"]
    assert data["id_empresa"] == conta_data["id_empresa"]
    assert "id_conta" in data

def test_get_contas_bancarias_api(authenticated_client, conta_bancaria_test_data):
    client, user = authenticated_client
    
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": str(user.id_empresa)}
    
    # Criar conta bancária via API
    create_response = client.post("/api/contas-bancarias/", json=conta_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Listar contas bancárias
    response = client.get("/api/contas-bancarias/")
    
    # Verificar se a resposta está correta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0

def test_get_conta_bancaria_by_id_api(authenticated_client, conta_bancaria_test_data):
    client, user = authenticated_client
    
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": str(user.id_empresa)}
    
    # Criar conta bancária via API
    create_response = client.post("/api/contas-bancarias/", json=conta_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    conta_id = create_response.json()["id_conta"]
    
    # Buscar conta bancária por ID
    response = client.get(f"/api/contas-bancarias/{conta_id}")
    
    # Verificar se a resposta está correta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id_conta"] == conta_id
    assert data["banco"] == conta_data["banco"]

def test_update_conta_bancaria_api(authenticated_client, conta_bancaria_test_data):
    client, user = authenticated_client
    
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": str(user.id_empresa)}
    
    # Criar conta bancária via API
    create_response = client.post("/api/contas-bancarias/", json=conta_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    conta_id = create_response.json()["id_conta"]
    
    # Atualizar conta bancária
    update_data = {"banco": "Banco Atualizado via API", "saldo_inicial": 3000.0}
    response = client.put(f"/api/contas-bancarias/{conta_id}", json=update_data)
    
    # Verificar se a resposta está correta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id_conta"] == conta_id
    assert data["banco"] == update_data["banco"]
    assert data["saldo_inicial"] == update_data["saldo_inicial"]
    assert data["agencia"] == conta_data["agencia"]  # Não alterado

def test_delete_conta_bancaria_api(authenticated_client, conta_bancaria_test_data):
    client, user = authenticated_client
    
    # Adicionar id_empresa aos dados da conta bancária
    conta_data = {**conta_bancaria_test_data, "id_empresa": str(user.id_empresa)}
    
    # Criar conta bancária via API
    create_response = client.post("/api/contas-bancarias/", json=conta_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    conta_id = create_response.json()["id_conta"]
    
    # Excluir conta bancária
    response = client.delete(f"/api/contas-bancarias/{conta_id}")
    
    # Verificar se a exclusão foi bem-sucedida
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Tentar buscar a conta excluída
    get_response = client.get(f"/api/contas-bancarias/{conta_id}")
    
    # Verificar se a conta foi realmente excluída
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_access(client):
    # Tentar acessar sem autenticação
    response = client.get("/api/contas-bancarias/")
    
    # Verificar se o acesso foi negado
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Cliente de teste
client = TestClient(app)

# Mock de usuário autenticado para os testes
test_user = {
    "id_usuario": "12345678-1234-5678-1234-567812345678",
    "id_empresa": "98765432-9876-5432-9876-543298765432",
    "nome": "Teste Usuário",
    "email": "teste@exemplo.com",
    "tipo_usuario": "adm",
    "telas_permitidas": {"contas_bancarias": True}
}

# Sobrescrever as dependências de autenticação e permissão
app.dependency_overrides[get_current_user] = lambda: test_user
app.dependency_overrides[check_permission] = lambda permission: lambda: True

# Fixture para criar uma conta bancária para teste
@pytest.fixture
def conta_bancaria_teste(db_session: Session):
    conta_data = {
        "banco": "Banco de Teste",
        "agencia": "1234",
        "numero": "12345-6",
        "tipo": "Corrente",
        "saldo_inicial": Decimal("1000.00"),
        "id_empresa": test_user["id_empresa"]
    }
    
    # Remover qualquer conta bancária com os mesmos dados para evitar conflitos
    conta_existente = db_session.query(ContaBancaria).filter(
        ContaBancaria.banco == conta_data["banco"],
        ContaBancaria.numero == conta_data["numero"],
        ContaBancaria.id_empresa == test_user["id_empresa"]
    ).first()
    
    if conta_existente:
        db_session.delete(conta_existente)
        db_session.commit()
    
    # Criar uma nova conta bancária
    conta = ContaBancaria(**conta_data)
    db_session.add(conta)
    db_session.commit()
    db_session.refresh(conta)
    
    yield conta
    
    # Limpeza após o teste
    try:
        c = db_session.query(ContaBancaria).filter(ContaBancaria.id_conta == conta.id_conta).first()
        if c:
            db_session.delete(c)
            db_session.commit()
    except:
        pass

# Testes de API
def test_listar_contas_bancarias(conta_bancaria_teste):
    """
    Teste para listar todas as contas bancárias com paginação, filtros e ordenação
    """
    # Teste de listagem básica
    response = client.get("/api/contas-bancarias/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    
    # Teste com filtros de busca
    response = client.get(f"/api/contas-bancarias/?banco={conta_bancaria_teste.banco}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    found = False
    for item in data["items"]:
        if item["banco"] == conta_bancaria_teste.banco and item["numero"] == conta_bancaria_teste.numero:
            found = True
            break
    assert found, "Conta bancária de teste não encontrada na filtragem por banco"
    
    # Teste com filtro de tipo
    response = client.get(f"/api/contas-bancarias/?tipo={conta_bancaria_teste.tipo}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    
    # Teste com paginação
    response = client.get("/api/contas-bancarias/?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5
    
    # Teste com ordenação
    response = client.get("/api/contas-bancarias/?order_by=banco&order_direction=asc")
    assert response.status_code == 200
    assert response.json()["items"] is not None

def test_obter_conta_bancaria_por_id(conta_bancaria_teste):
    """
    Teste para obter uma conta bancária específica por ID
    """
    response = client.get(f"/api/contas-bancarias/{conta_bancaria_teste.id_conta}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["banco"] == conta_bancaria_teste.banco
    assert data["agencia"] == conta_bancaria_teste.agencia
    assert data["numero"] == conta_bancaria_teste.numero
    assert data["tipo"] == conta_bancaria_teste.tipo
    assert float(data["saldo_inicial"]) == float(conta_bancaria_teste.saldo_inicial)
    
    # Teste com ID inválido
    response = client.get(f"/api/contas-bancarias/{uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_criar_conta_bancaria():
    """
    Teste para criar uma nova conta bancária
    """
    conta_data = {
        "banco": "Novo Banco",
        "agencia": "5678",
        "numero": "98765-4",
        "tipo": "Poupança",
        "saldo_inicial": 500.00,
        "id_empresa": test_user["id_empresa"]
    }
    
    # Teste de criação com dados válidos
    response = client.post("/api/contas-bancarias/", json=conta_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["banco"] == conta_data["banco"]
    assert data["agencia"] == conta_data["agencia"]
    assert data["numero"] == conta_data["numero"]
    assert data["tipo"] == conta_data["tipo"]
    assert float(data["saldo_inicial"]) == float(conta_data["saldo_inicial"])
    assert data["id_conta"] is not None
    
    # Limpar conta bancária criada
    conta_id = data["id_conta"]
    client.delete(f"/api/contas-bancarias/{conta_id}")
    
    # Teste de criação com dados inválidos (sem banco)
    invalid_data = conta_data.copy()
    invalid_data.pop("banco")
    response = client.post("/api/contas-bancarias/", json=invalid_data)
    assert response.status_code == 422
    
    # Teste de criação com dados inválidos (saldo inicial negativo)
    invalid_data = conta_data.copy()
    invalid_data["saldo_inicial"] = -100.00
    response = client.post("/api/contas-bancarias/", json=invalid_data)
    assert response.status_code == 422

def test_atualizar_conta_bancaria(conta_bancaria_teste):
    """
    Teste para atualizar uma conta bancária existente
    """
    update_data = {
        "banco": "Banco Atualizado",
        "agencia": "9999"
    }
    
    # Teste de atualização parcial válida
    response = client.put(f"/api/contas-bancarias/{conta_bancaria_teste.id_conta}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["banco"] == update_data["banco"]
    assert data["agencia"] == update_data["agencia"]
    assert data["numero"] == conta_bancaria_teste.numero  # Não deve alterar campo não especificado
    assert data["tipo"] == conta_bancaria_teste.tipo  # Não deve alterar campo não especificado
    
    # Teste de atualização com ID inexistente
    response = client.put(f"/api/contas-bancarias/{uuid4()}", json=update_data)
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Teste de atualização com dados inválidos
    invalid_data = {"saldo_inicial": -500.00}
    response = client.put(f"/api/contas-bancarias/{conta_bancaria_teste.id_conta}", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_excluir_conta_bancaria(conta_bancaria_teste):
    """
    Teste para excluir uma conta bancária
    """
    # Criar uma nova conta bancária para exclusão
    conta_data = {
        "banco": "Banco para Excluir",
        "agencia": "7777",
        "numero": "77777-7",
        "tipo": "Corrente",
        "saldo_inicial": 100.00,
        "id_empresa": test_user["id_empresa"]
    }
    
    response = client.post("/api/contas-bancarias/", json=conta_data)
    assert response.status_code == 201
    conta_id = response.json()["id_conta"]
    
    # Teste de exclusão bem-sucedida
    response = client.delete(f"/api/contas-bancarias/{conta_id}")
    assert response.status_code == 204
    
    # Verificar se foi realmente excluída
    response = client.get(f"/api/contas-bancarias/{conta_id}")
    assert response.status_code == 404
    
    # Teste de exclusão com ID inexistente
    response = client.delete(f"/api/contas-bancarias/{uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()
    
    # Teste com conta bancária vinculada a outros registros (simulação)
    # Supondo que exista uma verificação de uso vinculado
    # Como não temos acesso ao código completo para verificar a regra exata
    # de validação quando uma conta bancária está em uso, apenas testamos o caso
    # básico de exclusão bem-sucedida acima

def test_obter_saldo_conta_bancaria(conta_bancaria_teste):
    """
    Teste para obter o saldo atual de uma conta bancária
    """
    response = client.get(f"/api/contas-bancarias/{conta_bancaria_teste.id_conta}/saldo")
    assert response.status_code == 200
    
    data = response.json()
    assert "saldo_atual" in data
    assert isinstance(data["saldo_atual"], (int, float)) or isinstance(data["saldo_atual"], str)
    
    # Converter para float para comparação, se for string
    if isinstance(data["saldo_atual"], str):
        saldo_atual = float(data["saldo_atual"])
    else:
        saldo_atual = data["saldo_atual"]
    
    # O saldo atual deve ser pelo menos igual ao saldo inicial
    # (pode ter transações em testes anteriores)
    assert saldo_atual >= float(conta_bancaria_teste.saldo_inicial)
    
    # Teste com ID inválido
    response = client.get(f"/api/contas-bancarias/{uuid4()}/saldo")
    assert response.status_code == 404
    assert "detail" in response.json() 