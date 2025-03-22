import pytest
import uuid
from uuid import UUID
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.venda_service import VendaService
from app.schemas.venda import VendaCreate, VendaUpdate, VendaItemCreate


@pytest.fixture
def venda_service():
    """Fixture para criar uma instância do serviço de vendas."""
    return VendaService(AsyncMock())


@pytest.fixture
def cliente_mock():
    """Fixture para simular um cliente no banco de dados."""
    return MagicMock(
        id_cliente=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Cliente Teste",
        documento="12345678901",
        ativo=True
    )


@pytest.fixture
def forma_pagamento_mock():
    """Fixture para simular uma forma de pagamento."""
    return MagicMock(
        id_forma=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Cartão de Crédito",
        tipo="cartao_credito",
        parcelas_maximas=12,
        ativo=True
    )


@pytest.fixture
def produto_mock():
    """Fixture para simular um produto."""
    return MagicMock(
        id_produto=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Produto Teste",
        preco_venda=100.00,
        estoque_atual=50.0,
        ativo=True
    )


@pytest.fixture
def venda_item_mock(produto_mock):
    """Fixture para simular um item de venda."""
    return VendaItemCreate(
        id_produto=produto_mock.id_produto,
        quantidade=2,
        valor_unitario=100.00,
        desconto=0,
        valor_total=200.00
    )


@pytest.fixture
def venda_create_mock(cliente_mock, forma_pagamento_mock, venda_item_mock):
    """Fixture para simular dados de criação de venda."""
    return VendaCreate(
        id_empresa=cliente_mock.id_empresa,
        id_cliente=cliente_mock.id_cliente,
        id_forma_pagamento=forma_pagamento_mock.id_forma,
        descricao="Venda teste",
        data_venda=date.today(),
        valor_total=200.00,
        valor_desconto=0,
        valor_liquido=200.00,
        parcelado=False,
        total_parcelas=1,
        status="rascunho",
        observacao="Teste de venda",
        itens=[venda_item_mock]
    )


@pytest.fixture
def venda_mock(cliente_mock, forma_pagamento_mock):
    """Fixture para simular uma venda no banco de dados."""
    return MagicMock(
        id_venda=uuid.uuid4(),
        id_empresa=cliente_mock.id_empresa,
        id_cliente=cliente_mock.id_cliente,
        id_forma_pagamento=forma_pagamento_mock.id_forma,
        descricao="Venda teste",
        data_venda=date.today(),
        valor_total=200.00,
        valor_desconto=0,
        valor_liquido=200.00,
        parcelado=False,
        total_parcelas=1,
        status="rascunho",
        observacao="Teste de venda",
        itens=[
            MagicMock(
                id_item=uuid.uuid4(),
                id_venda=uuid.uuid4(),
                id_produto=uuid.uuid4(),
                quantidade=2,
                valor_unitario=100.00,
                desconto=0,
                valor_total=200.00
            )
        ],
        cliente=cliente_mock,
        forma_pagamento=forma_pagamento_mock
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
            status="rascunho"
        ),
        MagicMock(
            id_venda=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            descricao="Venda 2",
            data_venda=date.today(),
            valor_total=300.00,
            status="confirmada"
        ),
        MagicMock(
            id_venda=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            descricao="Venda 3",
            data_venda=date.today(),
            valor_total=150.00,
            status="cancelada"
        ),
    ]


class TestVendaService:
    """Testes para o serviço de vendas."""

    @pytest.mark.asyncio
    async def test_get_venda(self, venda_service, venda_mock):
        """Teste para obter uma venda pelo ID."""
        # Arrange
        id_venda = venda_mock.id_venda
        id_empresa = venda_mock.id_empresa

        # Mock do repositório
        venda_service.repository.get_by_id = AsyncMock(return_value=venda_mock)

        # Act
        venda = await venda_service.get_venda(id_venda, id_empresa)

        # Assert
        assert venda is not None
        assert venda.id_venda == id_venda
        assert venda.id_empresa == id_empresa
        assert venda.descricao == "Venda teste"
        
        # Verificar chamada ao repositório
        venda_service.repository.get_by_id.assert_called_once_with(id_venda, id_empresa)

    @pytest.mark.asyncio
    async def test_get_venda_not_found(self, venda_service):
        """Teste para verificar exceção quando venda não é encontrada."""
        # Arrange
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()

        # Mock do repositório
        venda_service.repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.get_venda(id_venda, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Venda não encontrada" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_get_venda_completa(self, venda_service, venda_mock):
        """Teste para obter uma venda com detalhes completos."""
        # Arrange
        id_venda = venda_mock.id_venda
        id_empresa = venda_mock.id_empresa

        # Mock do repositório
        venda_service.repository.get_venda_completa = AsyncMock(return_value=venda_mock)

        # Act
        venda = await venda_service.get_venda_completa(id_venda, id_empresa)

        # Assert
        assert venda is not None
        assert venda.id_venda == id_venda
        assert venda.cliente is not None
        assert venda.forma_pagamento is not None
        assert len(venda.itens) > 0
        
        # Verificar chamada ao repositório
        venda_service.repository.get_venda_completa.assert_called_once_with(id_venda, id_empresa)

    @pytest.mark.asyncio
    async def test_listar_vendas(self, venda_service, vendas_mock):
        """Teste para listar vendas com filtros."""
        # Arrange
        id_empresa = uuid.uuid4()
        skip = 0
        limit = 10
        
        # Mock do repositório
        venda_service.repository.get_by_empresa = AsyncMock(
            return_value=(vendas_mock, len(vendas_mock))
        )

        # Act
        vendas, total = await venda_service.listar_vendas(
            id_empresa=id_empresa,
            skip=skip,
            limit=limit,
            cliente="Cliente",
            data_inicio=date.today(),
            data_fim=date.today(),
            status="confirmada"
        )

        # Assert
        assert len(vendas) == len(vendas_mock)
        assert total == len(vendas_mock)
        
        # Verificar chamada ao repositório
        venda_service.repository.get_by_empresa.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_venda(self, venda_service, venda_create_mock, venda_mock, cliente_mock, forma_pagamento_mock, produto_mock):
        """Teste para criar uma nova venda."""
        # Arrange
        id_usuario = uuid.uuid4()
        
        # Mock dos repositórios
        venda_service.cliente_repository.get_by_id = AsyncMock(return_value=cliente_mock)
        venda_service.forma_pagamento_repository.get_by_id = AsyncMock(return_value=forma_pagamento_mock)
        venda_service.produto_repository.get_by_id = AsyncMock(return_value=produto_mock)
        venda_service.repository.create = AsyncMock(return_value=venda_mock)
        venda_service.repository.create_item = AsyncMock()

        # Act
        venda = await venda_service.criar_venda(venda_create_mock, id_usuario)

        # Assert
        assert venda is not None
        assert venda.id_venda == venda_mock.id_venda
        assert venda.descricao == venda_mock.descricao
        assert venda.valor_total == venda_mock.valor_total
        
        # Verificar chamadas aos repositórios
        venda_service.cliente_repository.get_by_id.assert_called_once()
        venda_service.forma_pagamento_repository.get_by_id.assert_called_once()
        venda_service.produto_repository.get_by_id.assert_called_once()
        venda_service.repository.create.assert_called_once()
        venda_service.repository.create_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_venda_cliente_inexistente(self, venda_service, venda_create_mock):
        """Teste para verificar exceção ao criar venda com cliente inexistente."""
        # Arrange
        id_usuario = uuid.uuid4()
        
        # Mock do repositório
        venda_service.cliente_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.criar_venda(venda_create_mock, id_usuario)
        
        assert excinfo.value.status_code == 404
        assert "Cliente não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_criar_venda_forma_pagamento_inexistente(self, venda_service, venda_create_mock, cliente_mock):
        """Teste para verificar exceção ao criar venda com forma de pagamento inexistente."""
        # Arrange
        id_usuario = uuid.uuid4()
        
        # Mock dos repositórios
        venda_service.cliente_repository.get_by_id = AsyncMock(return_value=cliente_mock)
        venda_service.forma_pagamento_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.criar_venda(venda_create_mock, id_usuario)
        
        assert excinfo.value.status_code == 404
        assert "Forma de pagamento não encontrada" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_confirmar_venda(self, venda_service, venda_mock):
        """Teste para confirmar uma venda em status rascunho."""
        # Arrange
        id_venda = venda_mock.id_venda
        id_empresa = venda_mock.id_empresa
        id_usuario = uuid.uuid4()
        
        # Mock dos repositórios
        venda_service.repository.get_by_id = AsyncMock(return_value=venda_mock)
        venda_service.repository.update = AsyncMock(return_value=MagicMock(
            **{**venda_mock.__dict__, "status": "confirmada"}
        ))
        venda_service.repository.get_venda_completa = AsyncMock(return_value=venda_mock)
        venda_service.lancamento_repository.create = AsyncMock()

        # Act
        venda_confirmada = await venda_service.confirmar_venda(id_venda, id_empresa, id_usuario)

        # Assert
        assert venda_confirmada is not None
        assert venda_confirmada.id_venda == id_venda
        
        # Verificar chamadas aos repositórios
        venda_service.repository.get_by_id.assert_called_once()
        venda_service.repository.update.assert_called_once()
        venda_service.repository.get_venda_completa.assert_called_once()
        venda_service.lancamento_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirmar_venda_nao_encontrada(self, venda_service):
        """Teste para verificar exceção ao confirmar venda não encontrada."""
        # Arrange
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        # Mock do repositório
        venda_service.repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.confirmar_venda(id_venda, id_empresa, id_usuario)
        
        assert excinfo.value.status_code == 404
        assert "Venda não encontrada" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_confirmar_venda_ja_confirmada(self, venda_service):
        """Teste para verificar exceção ao confirmar venda já confirmada."""
        # Arrange
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        venda_confirmada = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa,
            status="confirmada"
        )
        
        # Mock do repositório
        venda_service.repository.get_by_id = AsyncMock(return_value=venda_confirmada)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.confirmar_venda(id_venda, id_empresa, id_usuario)
        
        assert excinfo.value.status_code == 400
        assert "já está confirmada" in excinfo.value.detail.lower()

    @pytest.mark.asyncio
    async def test_cancelar_venda(self, venda_service, venda_mock):
        """Teste para cancelar uma venda."""
        # Arrange
        id_venda = venda_mock.id_venda
        id_empresa = venda_mock.id_empresa
        id_usuario = uuid.uuid4()
        
        # Alterar status para confirmada
        venda_confirmada = MagicMock(
            **{**venda_mock.__dict__, "status": "confirmada"}
        )
        
        # Mock dos repositórios
        venda_service.repository.get_by_id = AsyncMock(return_value=venda_confirmada)
        venda_service.repository.update = AsyncMock(return_value=MagicMock(
            **{**venda_confirmada.__dict__, "status": "cancelada"}
        ))
        venda_service.repository.get_venda_completa = AsyncMock(return_value=venda_confirmada)
        venda_service.lancamento_repository.get_by_venda = AsyncMock(return_value=[MagicMock()])
        venda_service.lancamento_repository.cancelar_lancamento = AsyncMock()

        # Act
        venda_cancelada = await venda_service.cancelar_venda(id_venda, id_empresa, id_usuario)

        # Assert
        assert venda_cancelada is not None
        assert venda_cancelada.id_venda == id_venda
        
        # Verificar chamadas aos repositórios
        venda_service.repository.get_by_id.assert_called_once()
        venda_service.repository.update.assert_called_once()
        venda_service.repository.get_venda_completa.assert_called_once()
        venda_service.lancamento_repository.get_by_venda.assert_called_once()
        venda_service.lancamento_repository.cancelar_lancamento.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancelar_venda_nao_encontrada(self, venda_service):
        """Teste para verificar exceção ao cancelar venda não encontrada."""
        # Arrange
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        # Mock do repositório
        venda_service.repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.cancelar_venda(id_venda, id_empresa, id_usuario)
        
        assert excinfo.value.status_code == 404
        assert "Venda não encontrada" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_cancelar_venda_ja_cancelada(self, venda_service):
        """Teste para verificar exceção ao cancelar venda já cancelada."""
        # Arrange
        id_venda = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        venda_cancelada = MagicMock(
            id_venda=id_venda,
            id_empresa=id_empresa,
            status="cancelada"
        )
        
        # Mock do repositório
        venda_service.repository.get_by_id = AsyncMock(return_value=venda_cancelada)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await venda_service.cancelar_venda(id_venda, id_empresa, id_usuario)
        
        assert excinfo.value.status_code == 400
        assert "já está cancelada" in excinfo.value.detail.lower() 