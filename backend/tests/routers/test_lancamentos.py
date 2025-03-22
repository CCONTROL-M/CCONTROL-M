import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import date, datetime

from app.main import app
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate
from app.services.lancamento_service import LancamentoService


@pytest.fixture
def cliente():
    """Fixture para instância do cliente de teste FastAPI."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_auth():
    """Fixture para simular autenticação."""
    with patch("app.dependencies.auth.get_current_user") as mock:
        mock.return_value = MagicMock(
            id_usuario=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Usuário Teste",
            email="teste@example.com",
            admin=True,
            ativo=True
        )
        yield mock


@pytest.fixture
def mock_db_session():
    """Fixture para simular a sessão do banco de dados."""
    with patch("app.dependencies.db.get_db") as mock:
        mock.return_value = AsyncMock()
        yield mock


@pytest.fixture
def lancamento_mock():
    """Fixture para simular um lançamento financeiro."""
    id_lancamento = uuid.uuid4()
    id_empresa = uuid.uuid4()
    id_categoria = uuid.uuid4()
    id_conta = uuid.uuid4()
    id_cliente = uuid.uuid4()
    
    return MagicMock(
        id_lancamento=id_lancamento,
        id_empresa=id_empresa,
        tipo="receita",
        descricao="Pagamento Cliente",
        id_categoria=id_categoria,
        id_conta=id_conta,
        id_cliente=id_cliente,
        id_fornecedor=None,
        id_venda=None,
        valor=100.00,
        data_vencimento=date.today(),
        data_pagamento=date.today(),
        forma_pagamento="dinheiro",
        status="confirmado",
        recorrente=False,
        total_parcelas=1,
        parcela_atual=1,
        observacao="Pagamento à vista",
        categoria=MagicMock(
            id_categoria=id_categoria,
            nome="Vendas"
        ),
        conta=MagicMock(
            id_conta=id_conta,
            nome="Conta Principal"
        ),
        cliente=MagicMock(
            id_cliente=id_cliente,
            nome="Cliente Teste"
        ),
        fornecedor=None,
        venda=None
    )


@pytest.fixture
def lancamentos_mock():
    """Fixture para simular uma lista de lançamentos financeiros."""
    return [
        MagicMock(
            id_lancamento=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            tipo="receita",
            descricao="Pagamento Cliente 1",
            valor=100.00,
            data_vencimento=date.today(),
            status="confirmado",
            categoria=MagicMock(nome="Vendas"),
            conta=MagicMock(nome="Conta Principal"),
            cliente=MagicMock(nome="Cliente 1")
        ),
        MagicMock(
            id_lancamento=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            tipo="despesa",
            descricao="Pagamento Fornecedor",
            valor=200.00,
            data_vencimento=date.today(),
            status="pendente",
            categoria=MagicMock(nome="Compras"),
            conta=MagicMock(nome="Conta Principal"),
            fornecedor=MagicMock(nome="Fornecedor 1")
        ),
        MagicMock(
            id_lancamento=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            tipo="receita",
            descricao="Venda à vista",
            valor=150.00,
            data_vencimento=date.today(),
            status="confirmado",
            categoria=MagicMock(nome="Vendas"),
            conta=MagicMock(nome="Conta Secundária"),
            cliente=MagicMock(nome="Cliente 2")
        ),
    ]


@pytest.fixture
def lancamento_create_mock():
    """Fixture para simular dados de criação de lançamento financeiro."""
    return LancamentoCreate(
        id_empresa=uuid.uuid4(),
        tipo="receita",
        descricao="Novo Lançamento",
        id_categoria=uuid.uuid4(),
        id_conta=uuid.uuid4(),
        id_cliente=uuid.uuid4(),
        id_fornecedor=None,
        id_venda=None,
        valor=150.00,
        data_vencimento=date.today(),
        data_pagamento=date.today(),
        forma_pagamento="dinheiro",
        status="confirmado",
        recorrente=False,
        total_parcelas=1,
        parcela_atual=1,
        observacao="Novo lançamento de teste"
    )


class TestLancamentosRouter:
    """Testes para as rotas de lançamentos financeiros."""
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_listar_lancamentos(self, mock_service, cliente, mock_auth, mock_db_session, lancamentos_mock):
        """Teste para listar lançamentos financeiros com paginação."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.listar_lancamentos.return_value = (lancamentos_mock, len(lancamentos_mock))
        
        # Act
        response = cliente.get("/api/lancamentos?skip=0&limit=10")
        
        # Assert
        assert response.status_code == 200
        dados = response.json()
        assert "itens" in dados
        assert "total" in dados
        assert dados["total"] == len(lancamentos_mock)
        assert len(dados["itens"]) == len(lancamentos_mock)
        
        # Verificar chamada ao serviço
        service_instance.listar_lancamentos.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_obter_lancamento(self, mock_service, cliente, mock_auth, mock_db_session, lancamento_mock):
        """Teste para obter um lançamento financeiro por ID."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        service_instance = mock_service.return_value
        service_instance.get_lancamento_completo.return_value = lancamento_mock
        
        # Act
        response = cliente.get(f"/api/lancamentos/{id_lancamento}")
        
        # Assert
        assert response.status_code == 200
        lancamento = response.json()
        assert lancamento["id_lancamento"] == str(id_lancamento)
        assert lancamento["descricao"] == lancamento_mock.descricao
        assert "categoria" in lancamento
        assert "conta" in lancamento
        
        # Verificar chamada ao serviço
        service_instance.get_lancamento_completo.assert_called_once_with(
            uuid.UUID(str(id_lancamento)), mock_auth.return_value.id_empresa
        )
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_obter_lancamento_not_found(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando lançamento não é encontrado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.get_lancamento_completo.side_effect = HTTPException(
            status_code=404, detail="Lançamento não encontrado"
        )
        
        # Act
        response = cliente.get(f"/api/lancamentos/{id_lancamento}")
        
        # Assert
        assert response.status_code == 404
        dados = response.json()
        assert "detail" in dados
        assert "Lançamento não encontrado" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.get_lancamento_completo.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_criar_lancamento(self, mock_service, cliente, mock_auth, mock_db_session, lancamento_create_mock, lancamento_mock):
        """Teste para criar um novo lançamento financeiro."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.criar_lancamento.return_value = lancamento_mock
        
        # Converter o objeto para dicionário para enviar na requisição
        lancamento_dict = lancamento_create_mock.model_dump()
        
        # Act
        response = cliente.post("/api/lancamentos", json=lancamento_dict)
        
        # Assert
        assert response.status_code == 201
        lancamento = response.json()
        assert lancamento["id_lancamento"] == str(lancamento_mock.id_lancamento)
        assert lancamento["descricao"] == lancamento_mock.descricao
        
        # Verificar chamada ao serviço
        service_instance.criar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_criar_lancamento_validation_error(self, mock_service, cliente, mock_auth, mock_db_session, lancamento_create_mock):
        """Teste para verificar resposta quando validação falha na criação de lançamento."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.criar_lancamento.side_effect = HTTPException(
            status_code=400, detail="Erro de validação"
        )
        
        # Converter o objeto para dicionário para enviar na requisição
        lancamento_dict = lancamento_create_mock.model_dump()
        
        # Act
        response = cliente.post("/api/lancamentos", json=lancamento_dict)
        
        # Assert
        assert response.status_code == 400
        dados = response.json()
        assert "detail" in dados
        assert "Erro de validação" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.criar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_atualizar_lancamento(self, mock_service, cliente, mock_auth, mock_db_session, lancamento_mock):
        """Teste para atualizar um lançamento financeiro existente."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        service_instance = mock_service.return_value
        service_instance.atualizar_lancamento.return_value = lancamento_mock
        
        lancamento_update = {
            "descricao": "Lançamento atualizado",
            "observacao": "Observação atualizada"
        }
        
        # Act
        response = cliente.patch(f"/api/lancamentos/{id_lancamento}", json=lancamento_update)
        
        # Assert
        assert response.status_code == 200
        lancamento = response.json()
        assert lancamento["id_lancamento"] == str(id_lancamento)
        
        # Verificar chamada ao serviço
        service_instance.atualizar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_atualizar_lancamento_not_found(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando lançamento a ser atualizado não é encontrado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.atualizar_lancamento.side_effect = HTTPException(
            status_code=404, detail="Lançamento não encontrado"
        )
        
        lancamento_update = {
            "descricao": "Lançamento atualizado",
            "observacao": "Observação atualizada"
        }
        
        # Act
        response = cliente.patch(f"/api/lancamentos/{id_lancamento}", json=lancamento_update)
        
        # Assert
        assert response.status_code == 404
        dados = response.json()
        assert "detail" in dados
        assert "Lançamento não encontrado" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.atualizar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_confirmar_lancamento(self, mock_service, cliente, mock_auth, mock_db_session, lancamento_mock):
        """Teste para confirmar um lançamento financeiro."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        service_instance = mock_service.return_value
        service_instance.confirmar_lancamento.return_value = MagicMock(
            **{**lancamento_mock.__dict__, "status": "confirmado"}
        )
        
        data_pagamento = str(date.today())
        
        # Act
        response = cliente.post(
            f"/api/lancamentos/{id_lancamento}/confirmar",
            json={"data_pagamento": data_pagamento}
        )
        
        # Assert
        assert response.status_code == 200
        lancamento = response.json()
        assert lancamento["id_lancamento"] == str(id_lancamento)
        assert lancamento["status"] == "confirmado"
        
        # Verificar chamada ao serviço
        service_instance.confirmar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_confirmar_lancamento_erro(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando confirmação de lançamento falha."""
        # Arrange
        id_lancamento = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.confirmar_lancamento.side_effect = HTTPException(
            status_code=400, detail="Erro ao confirmar lançamento"
        )
        
        data_pagamento = str(date.today())
        
        # Act
        response = cliente.post(
            f"/api/lancamentos/{id_lancamento}/confirmar",
            json={"data_pagamento": data_pagamento}
        )
        
        # Assert
        assert response.status_code == 400
        dados = response.json()
        assert "detail" in dados
        assert "Erro ao confirmar lançamento" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.confirmar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_cancelar_lancamento(self, mock_service, cliente, mock_auth, mock_db_session, lancamento_mock):
        """Teste para cancelar um lançamento financeiro."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        service_instance = mock_service.return_value
        service_instance.cancelar_lancamento.return_value = MagicMock(
            **{**lancamento_mock.__dict__, "status": "cancelado"}
        )
        
        # Act
        response = cliente.post(f"/api/lancamentos/{id_lancamento}/cancelar")
        
        # Assert
        assert response.status_code == 200
        lancamento = response.json()
        assert lancamento["id_lancamento"] == str(id_lancamento)
        assert lancamento["status"] == "cancelado"
        
        # Verificar chamada ao serviço
        service_instance.cancelar_lancamento.assert_called_once_with(
            uuid.UUID(str(id_lancamento)), 
            mock_auth.return_value.id_empresa,
            mock_auth.return_value.id_usuario
        )
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_cancelar_lancamento_erro(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando cancelamento de lançamento falha."""
        # Arrange
        id_lancamento = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.cancelar_lancamento.side_effect = HTTPException(
            status_code=400, detail="Erro ao cancelar lançamento"
        )
        
        # Act
        response = cliente.post(f"/api/lancamentos/{id_lancamento}/cancelar")
        
        # Assert
        assert response.status_code == 400
        dados = response.json()
        assert "detail" in dados
        assert "Erro ao cancelar lançamento" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.cancelar_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_remover_lancamento(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para remover um lançamento financeiro."""
        # Arrange
        id_lancamento = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.remover_lancamento.return_value = True
        
        # Act
        response = cliente.delete(f"/api/lancamentos/{id_lancamento}")
        
        # Assert
        assert response.status_code == 204
        
        # Verificar chamada ao serviço
        service_instance.remover_lancamento.assert_called_once_with(
            uuid.UUID(str(id_lancamento)), mock_auth.return_value.id_empresa
        )
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_remover_lancamento_not_found(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando lançamento a ser removido não é encontrado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.remover_lancamento.side_effect = HTTPException(
            status_code=404, detail="Lançamento não encontrado"
        )
        
        # Act
        response = cliente.delete(f"/api/lancamentos/{id_lancamento}")
        
        # Assert
        assert response.status_code == 404
        dados = response.json()
        assert "detail" in dados
        assert "Lançamento não encontrado" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.remover_lancamento.assert_called_once()
    
    @patch("app.routers.lancamentos.LancamentoService")
    def test_calcular_totais(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para calcular totais de lançamentos financeiros."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.calcular_totais.return_value = {
            "receitas": 1000.00,
            "despesas": 500.00,
            "saldo": 500.00
        }
        
        # Act
        response = cliente.get("/api/lancamentos/totais")
        
        # Assert
        assert response.status_code == 200
        totais = response.json()
        assert "receitas" in totais
        assert "despesas" in totais
        assert "saldo" in totais
        assert totais["receitas"] == 1000.00
        assert totais["despesas"] == 500.00
        assert totais["saldo"] == 500.00
        
        # Verificar chamada ao serviço
        service_instance.calcular_totais.assert_called_once() 