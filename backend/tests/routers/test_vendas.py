import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import date, datetime

from app.main import app
from app.schemas.venda import VendaCreate, VendaUpdate, VendaItemCreate
from app.services.venda_service import VendaService


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
def venda_mock():
    """Fixture para simular uma venda."""
    id_venda = uuid.uuid4()
    id_empresa = uuid.uuid4()
    id_cliente = uuid.uuid4()
    id_forma_pagamento = uuid.uuid4()
    
    return MagicMock(
        id_venda=id_venda,
        id_empresa=id_empresa,
        id_cliente=id_cliente,
        id_forma_pagamento=id_forma_pagamento,
        descricao="Venda teste",
        data_venda=date.today(),
        valor_total=200.00,
        valor_desconto=0,
        valor_liquido=200.00,
        parcelado=False,
        total_parcelas=1,
        status="rascunho",
        observacao="Teste de venda",
        cliente=MagicMock(
            id_cliente=id_cliente,
            nome="Cliente Teste"
        ),
        forma_pagamento=MagicMock(
            id_forma=id_forma_pagamento,
            nome="Cartão de Crédito"
        ),
        itens=[
            MagicMock(
                id_item=uuid.uuid4(),
                id_venda=id_venda,
                id_produto=uuid.uuid4(),
                quantidade=2,
                valor_unitario=100.00,
                desconto=0,
                valor_total=200.00,
                produto=MagicMock(
                    nome="Produto Teste"
                )
            )
        ]
    )


@pytest.fixture
def vendas_mock():
    """Fixture para simular uma lista de vendas."""
    return [
        MagicMock(
            id_venda=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            descricao="Venda 1",
            data_venda=date.today(),
            valor_total=200.00,
            status="rascunho",
            cliente=MagicMock(nome="Cliente 1")
        ),
        MagicMock(
            id_venda=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            descricao="Venda 2",
            data_venda=date.today(),
            valor_total=300.00,
            status="confirmada",
            cliente=MagicMock(nome="Cliente 2")
        ),
        MagicMock(
            id_venda=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            descricao="Venda 3",
            data_venda=date.today(),
            valor_total=150.00,
            status="cancelada",
            cliente=MagicMock(nome="Cliente 3")
        ),
    ]


@pytest.fixture
def venda_item_create_mock():
    """Fixture para simular um item de venda na criação."""
    return VendaItemCreate(
        id_produto=uuid.uuid4(),
        quantidade=2,
        valor_unitario=100.00,
        desconto=0,
        valor_total=200.00
    )


@pytest.fixture
def venda_create_mock(venda_item_create_mock):
    """Fixture para simular dados de criação de venda."""
    return VendaCreate(
        id_empresa=uuid.uuid4(),
        id_cliente=uuid.uuid4(),
        id_forma_pagamento=uuid.uuid4(),
        descricao="Venda teste",
        data_venda=date.today(),
        valor_total=200.00,
        valor_desconto=0,
        valor_liquido=200.00,
        parcelado=False,
        total_parcelas=1,
        status="rascunho",
        observacao="Teste de venda",
        itens=[venda_item_create_mock]
    )


class TestVendasRouter:
    """Testes para as rotas de vendas."""
    
    @patch("app.routers.vendas.VendaService")
    def test_listar_vendas(self, mock_service, cliente, mock_auth, mock_db_session, vendas_mock):
        """Teste para listar vendas com paginação."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.listar_vendas.return_value = (vendas_mock, len(vendas_mock))
        
        # Act
        response = cliente.get("/api/vendas?skip=0&limit=10")
        
        # Assert
        assert response.status_code == 200
        dados = response.json()
        assert "itens" in dados
        assert "total" in dados
        assert dados["total"] == len(vendas_mock)
        assert len(dados["itens"]) == len(vendas_mock)
        
        # Verificar chamada ao serviço
        service_instance.listar_vendas.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_obter_venda(self, mock_service, cliente, mock_auth, mock_db_session, venda_mock):
        """Teste para obter uma venda por ID."""
        # Arrange
        id_venda = venda_mock.id_venda
        service_instance = mock_service.return_value
        service_instance.get_venda_completa.return_value = venda_mock
        
        # Act
        response = cliente.get(f"/api/vendas/{id_venda}")
        
        # Assert
        assert response.status_code == 200
        venda = response.json()
        assert venda["id_venda"] == str(id_venda)
        assert venda["descricao"] == venda_mock.descricao
        assert "cliente" in venda
        assert "forma_pagamento" in venda
        assert "itens" in venda
        
        # Verificar chamada ao serviço
        service_instance.get_venda_completa.assert_called_once_with(
            uuid.UUID(str(id_venda)), mock_auth.return_value.id_empresa
        )
    
    @patch("app.routers.vendas.VendaService")
    def test_obter_venda_not_found(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando venda não é encontrada."""
        # Arrange
        id_venda = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.get_venda_completa.side_effect = HTTPException(
            status_code=404, detail="Venda não encontrada"
        )
        
        # Act
        response = cliente.get(f"/api/vendas/{id_venda}")
        
        # Assert
        assert response.status_code == 404
        dados = response.json()
        assert "detail" in dados
        assert "Venda não encontrada" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.get_venda_completa.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_criar_venda(self, mock_service, cliente, mock_auth, mock_db_session, venda_create_mock, venda_mock):
        """Teste para criar uma nova venda."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.criar_venda.return_value = venda_mock
        
        # Converter o objeto para dicionário para enviar na requisição
        venda_dict = venda_create_mock.model_dump()
        
        # Act
        response = cliente.post("/api/vendas", json=venda_dict)
        
        # Assert
        assert response.status_code == 201
        venda = response.json()
        assert venda["id_venda"] == str(venda_mock.id_venda)
        assert venda["descricao"] == venda_mock.descricao
        
        # Verificar chamada ao serviço
        service_instance.criar_venda.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_criar_venda_validation_error(self, mock_service, cliente, mock_auth, mock_db_session, venda_create_mock):
        """Teste para verificar resposta quando validação falha na criação de venda."""
        # Arrange
        service_instance = mock_service.return_value
        service_instance.criar_venda.side_effect = HTTPException(
            status_code=400, detail="Erro de validação"
        )
        
        # Converter o objeto para dicionário para enviar na requisição
        venda_dict = venda_create_mock.model_dump()
        
        # Act
        response = cliente.post("/api/vendas", json=venda_dict)
        
        # Assert
        assert response.status_code == 400
        dados = response.json()
        assert "detail" in dados
        assert "Erro de validação" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.criar_venda.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_atualizar_venda(self, mock_service, cliente, mock_auth, mock_db_session, venda_mock):
        """Teste para atualizar uma venda existente."""
        # Arrange
        id_venda = venda_mock.id_venda
        service_instance = mock_service.return_value
        service_instance.atualizar_venda.return_value = venda_mock
        
        venda_update = {
            "descricao": "Venda atualizada",
            "observacao": "Observação atualizada"
        }
        
        # Act
        response = cliente.patch(f"/api/vendas/{id_venda}", json=venda_update)
        
        # Assert
        assert response.status_code == 200
        venda = response.json()
        assert venda["id_venda"] == str(id_venda)
        
        # Verificar chamada ao serviço
        service_instance.atualizar_venda.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_atualizar_venda_not_found(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando venda a ser atualizada não é encontrada."""
        # Arrange
        id_venda = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.atualizar_venda.side_effect = HTTPException(
            status_code=404, detail="Venda não encontrada"
        )
        
        venda_update = {
            "descricao": "Venda atualizada",
            "observacao": "Observação atualizada"
        }
        
        # Act
        response = cliente.patch(f"/api/vendas/{id_venda}", json=venda_update)
        
        # Assert
        assert response.status_code == 404
        dados = response.json()
        assert "detail" in dados
        assert "Venda não encontrada" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.atualizar_venda.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_confirmar_venda(self, mock_service, cliente, mock_auth, mock_db_session, venda_mock):
        """Teste para confirmar uma venda."""
        # Arrange
        id_venda = venda_mock.id_venda
        service_instance = mock_service.return_value
        service_instance.confirmar_venda.return_value = MagicMock(
            **{**venda_mock.__dict__, "status": "confirmada"}
        )
        
        # Act
        response = cliente.post(f"/api/vendas/{id_venda}/confirmar")
        
        # Assert
        assert response.status_code == 200
        venda = response.json()
        assert venda["id_venda"] == str(id_venda)
        assert venda["status"] == "confirmada"
        
        # Verificar chamada ao serviço
        service_instance.confirmar_venda.assert_called_once_with(
            uuid.UUID(str(id_venda)), 
            mock_auth.return_value.id_empresa,
            mock_auth.return_value.id_usuario
        )
    
    @patch("app.routers.vendas.VendaService")
    def test_confirmar_venda_erro(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando confirmação de venda falha."""
        # Arrange
        id_venda = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.confirmar_venda.side_effect = HTTPException(
            status_code=400, detail="Erro ao confirmar venda"
        )
        
        # Act
        response = cliente.post(f"/api/vendas/{id_venda}/confirmar")
        
        # Assert
        assert response.status_code == 400
        dados = response.json()
        assert "detail" in dados
        assert "Erro ao confirmar venda" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.confirmar_venda.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_cancelar_venda(self, mock_service, cliente, mock_auth, mock_db_session, venda_mock):
        """Teste para cancelar uma venda."""
        # Arrange
        id_venda = venda_mock.id_venda
        service_instance = mock_service.return_value
        service_instance.cancelar_venda.return_value = MagicMock(
            **{**venda_mock.__dict__, "status": "cancelada"}
        )
        
        # Act
        response = cliente.post(f"/api/vendas/{id_venda}/cancelar")
        
        # Assert
        assert response.status_code == 200
        venda = response.json()
        assert venda["id_venda"] == str(id_venda)
        assert venda["status"] == "cancelada"
        
        # Verificar chamada ao serviço
        service_instance.cancelar_venda.assert_called_once_with(
            uuid.UUID(str(id_venda)), 
            mock_auth.return_value.id_empresa,
            mock_auth.return_value.id_usuario
        )
    
    @patch("app.routers.vendas.VendaService")
    def test_cancelar_venda_erro(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando cancelamento de venda falha."""
        # Arrange
        id_venda = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.cancelar_venda.side_effect = HTTPException(
            status_code=400, detail="Erro ao cancelar venda"
        )
        
        # Act
        response = cliente.post(f"/api/vendas/{id_venda}/cancelar")
        
        # Assert
        assert response.status_code == 400
        dados = response.json()
        assert "detail" in dados
        assert "Erro ao cancelar venda" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.cancelar_venda.assert_called_once()
    
    @patch("app.routers.vendas.VendaService")
    def test_remover_venda(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para remover uma venda."""
        # Arrange
        id_venda = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.remover_venda.return_value = True
        
        # Act
        response = cliente.delete(f"/api/vendas/{id_venda}")
        
        # Assert
        assert response.status_code == 204
        
        # Verificar chamada ao serviço
        service_instance.remover_venda.assert_called_once_with(
            uuid.UUID(str(id_venda)), mock_auth.return_value.id_empresa
        )
    
    @patch("app.routers.vendas.VendaService")
    def test_remover_venda_not_found(self, mock_service, cliente, mock_auth, mock_db_session):
        """Teste para verificar resposta quando venda a ser removida não é encontrada."""
        # Arrange
        id_venda = uuid.uuid4()
        service_instance = mock_service.return_value
        service_instance.remover_venda.side_effect = HTTPException(
            status_code=404, detail="Venda não encontrada"
        )
        
        # Act
        response = cliente.delete(f"/api/vendas/{id_venda}")
        
        # Assert
        assert response.status_code == 404
        dados = response.json()
        assert "detail" in dados
        assert "Venda não encontrada" in dados["detail"]
        
        # Verificar chamada ao serviço
        service_instance.remover_venda.assert_called_once() 