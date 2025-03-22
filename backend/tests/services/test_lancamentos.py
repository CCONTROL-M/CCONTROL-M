import pytest
import uuid
from uuid import UUID
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.lancamento_service import LancamentoService
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate, LancamentoResponse


@pytest.fixture
def lancamento_service():
    """Fixture para criar uma instância do serviço de lançamentos financeiros."""
    return LancamentoService(AsyncMock())


@pytest.fixture
def conta_bancaria_mock():
    """Fixture para simular uma conta bancária."""
    return MagicMock(
        id_conta=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Conta Principal",
        tipo="corrente",
        saldo_atual=1000.00,
        ativo=True
    )


@pytest.fixture
def categoria_mock():
    """Fixture para simular uma categoria financeira."""
    return MagicMock(
        id_categoria=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Vendas",
        tipo="receita",
        ativo=True
    )


@pytest.fixture
def cliente_mock():
    """Fixture para simular um cliente."""
    return MagicMock(
        id_cliente=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Cliente Teste",
        documento="12345678901",
        ativo=True
    )


@pytest.fixture
def fornecedor_mock():
    """Fixture para simular um fornecedor."""
    return MagicMock(
        id_fornecedor=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Fornecedor Teste",
        cnpj="12345678000190",
        ativo=True
    )


@pytest.fixture
def venda_mock():
    """Fixture para simular uma venda."""
    return MagicMock(
        id_venda=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        descricao="Venda teste",
        valor_total=200.00,
        data_venda=date.today(),
        status="confirmada"
    )


@pytest.fixture
def lancamento_create_mock(categoria_mock, conta_bancaria_mock, cliente_mock):
    """Fixture para simular dados de criação de lançamento financeiro."""
    return LancamentoCreate(
        id_empresa=conta_bancaria_mock.id_empresa,
        tipo="receita",
        descricao="Pagamento Cliente",
        id_categoria=categoria_mock.id_categoria,
        id_conta=conta_bancaria_mock.id_conta,
        id_cliente=cliente_mock.id_cliente,
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
        observacao="Pagamento à vista"
    )


@pytest.fixture
def lancamento_mock(categoria_mock, conta_bancaria_mock, cliente_mock):
    """Fixture para simular um lançamento financeiro no banco de dados."""
    return MagicMock(
        id_lancamento=uuid.uuid4(),
        id_empresa=conta_bancaria_mock.id_empresa,
        tipo="receita",
        descricao="Pagamento Cliente",
        id_categoria=categoria_mock.id_categoria,
        id_conta=conta_bancaria_mock.id_conta,
        id_cliente=cliente_mock.id_cliente,
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
        categoria=categoria_mock,
        conta=conta_bancaria_mock,
        cliente=cliente_mock,
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
            status="confirmado"
        ),
        MagicMock(
            id_lancamento=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            tipo="despesa",
            descricao="Pagamento Fornecedor",
            valor=200.00,
            data_vencimento=date.today(),
            status="pendente"
        ),
        MagicMock(
            id_lancamento=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            tipo="receita",
            descricao="Venda à vista",
            valor=150.00,
            data_vencimento=date.today(),
            status="confirmado"
        ),
    ]


class TestLancamentoService:
    """Testes para o serviço de lançamentos financeiros."""

    @pytest.mark.asyncio
    async def test_get_lancamento(self, lancamento_service, lancamento_mock):
        """Teste para obter um lançamento pelo ID."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa

        # Mock do repositório
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_mock)

        # Act
        lancamento = await lancamento_service.get_lancamento(id_lancamento, id_empresa)

        # Assert
        assert lancamento is not None
        assert lancamento.id_lancamento == id_lancamento
        assert lancamento.id_empresa == id_empresa
        assert lancamento.descricao == "Pagamento Cliente"
        assert lancamento.valor == 100.00
        
        # Verificar chamada ao repositório
        lancamento_service.repository.get_by_id.assert_called_once_with(id_lancamento, id_empresa)

    @pytest.mark.asyncio
    async def test_get_lancamento_not_found(self, lancamento_service):
        """Teste para verificar exceção quando lançamento não é encontrado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        id_empresa = uuid.uuid4()

        # Mock do repositório
        lancamento_service.repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.get_lancamento(id_lancamento, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Lançamento não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_get_lancamento_completo(self, lancamento_service, lancamento_mock):
        """Teste para obter um lançamento com detalhes completos."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa

        # Mock do repositório
        lancamento_service.repository.get_lancamento_completo = AsyncMock(return_value=lancamento_mock)

        # Act
        lancamento = await lancamento_service.get_lancamento_completo(id_lancamento, id_empresa)

        # Assert
        assert lancamento is not None
        assert lancamento.id_lancamento == id_lancamento
        assert lancamento.categoria is not None
        assert lancamento.conta is not None
        assert lancamento.cliente is not None
        
        # Verificar chamada ao repositório
        lancamento_service.repository.get_lancamento_completo.assert_called_once_with(id_lancamento, id_empresa)

    @pytest.mark.asyncio
    async def test_listar_lancamentos(self, lancamento_service, lancamentos_mock):
        """Teste para listar lançamentos com filtros."""
        # Arrange
        id_empresa = uuid.uuid4()
        skip = 0
        limit = 10
        
        # Mock do repositório
        lancamento_service.repository.get_by_empresa = AsyncMock(
            return_value=(lancamentos_mock, len(lancamentos_mock))
        )

        # Act
        lancamentos, total = await lancamento_service.listar_lancamentos(
            id_empresa=id_empresa,
            skip=skip,
            limit=limit,
            tipo="receita",
            data_inicio=date.today(),
            data_fim=date.today(),
            status="confirmado"
        )

        # Assert
        assert len(lancamentos) == len(lancamentos_mock)
        assert total == len(lancamentos_mock)
        
        # Verificar chamada ao repositório
        lancamento_service.repository.get_by_empresa.assert_called_once()

    @pytest.mark.asyncio
    async def test_calcular_totais(self, lancamento_service):
        """Teste para calcular totais de lançamentos."""
        # Arrange
        id_empresa = uuid.uuid4()
        
        # Mock do repositório
        lancamento_service.repository.get_totais = AsyncMock(
            return_value={
                "receitas": 1000.00,
                "despesas": 500.00,
                "saldo": 500.00
            }
        )

        # Act
        totais = await lancamento_service.calcular_totais(
            id_empresa=id_empresa,
            data_inicio=date.today(),
            data_fim=date.today(),
            status="confirmado"
        )

        # Assert
        assert totais is not None
        assert totais["receitas"] == 1000.00
        assert totais["despesas"] == 500.00
        assert totais["saldo"] == 500.00
        
        # Verificar chamada ao repositório
        lancamento_service.repository.get_totais.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_lancamento(self, lancamento_service, lancamento_create_mock, lancamento_mock, categoria_mock, conta_bancaria_mock, cliente_mock):
        """Teste para criar um novo lançamento."""
        # Arrange
        id_usuario = uuid.uuid4()
        
        # Mock dos repositórios
        lancamento_service.categoria_repository.get_by_id = AsyncMock(return_value=categoria_mock)
        lancamento_service.conta_repository.get_by_id = AsyncMock(return_value=conta_bancaria_mock)
        lancamento_service.cliente_repository.get_by_id = AsyncMock(return_value=cliente_mock)
        lancamento_service.repository.create = AsyncMock(return_value=lancamento_mock)
        lancamento_service.conta_repository.atualizar_saldo = AsyncMock()

        # Act
        lancamento = await lancamento_service.criar_lancamento(lancamento_create_mock, id_usuario)

        # Assert
        assert lancamento is not None
        assert lancamento.id_lancamento == lancamento_mock.id_lancamento
        assert lancamento.descricao == lancamento_mock.descricao
        assert lancamento.valor == lancamento_mock.valor
        
        # Verificar chamadas aos repositórios
        lancamento_service.categoria_repository.get_by_id.assert_called_once()
        lancamento_service.conta_repository.get_by_id.assert_called_once()
        lancamento_service.cliente_repository.get_by_id.assert_called_once()
        lancamento_service.repository.create.assert_called_once()
        
        # Em lançamentos confirmados, deve atualizar o saldo da conta
        if lancamento_create_mock.status == "confirmado":
            lancamento_service.conta_repository.atualizar_saldo.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_lancamento_categoria_inexistente(self, lancamento_service, lancamento_create_mock):
        """Teste para verificar exceção ao criar lançamento com categoria inexistente."""
        # Arrange
        id_usuario = uuid.uuid4()
        
        # Mock do repositório
        lancamento_service.categoria_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.criar_lancamento(lancamento_create_mock, id_usuario)
        
        assert excinfo.value.status_code == 404
        assert "Categoria não encontrada" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_criar_lancamento_conta_inexistente(self, lancamento_service, lancamento_create_mock, categoria_mock):
        """Teste para verificar exceção ao criar lançamento com conta inexistente."""
        # Arrange
        id_usuario = uuid.uuid4()
        
        # Mock dos repositórios
        lancamento_service.categoria_repository.get_by_id = AsyncMock(return_value=categoria_mock)
        lancamento_service.conta_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.criar_lancamento(lancamento_create_mock, id_usuario)
        
        assert excinfo.value.status_code == 404
        assert "Conta bancária não encontrada" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_confirmar_lancamento(self, lancamento_service, lancamento_mock, conta_bancaria_mock):
        """Teste para confirmar um lançamento pendente."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa
        id_usuario = uuid.uuid4()
        
        # Alterar status para pendente
        lancamento_pendente = MagicMock(
            **{**lancamento_mock.__dict__, "status": "pendente", "data_pagamento": None}
        )
        
        # Mock dos repositórios
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_pendente)
        lancamento_service.repository.update = AsyncMock(return_value=MagicMock(
            **{**lancamento_pendente.__dict__, "status": "confirmado", "data_pagamento": date.today()}
        ))
        lancamento_service.conta_repository.get_by_id = AsyncMock(return_value=conta_bancaria_mock)
        lancamento_service.conta_repository.atualizar_saldo = AsyncMock()

        # Act
        lancamento_confirmado = await lancamento_service.confirmar_lancamento(
            id_lancamento, id_empresa, date.today(), id_usuario
        )

        # Assert
        assert lancamento_confirmado is not None
        assert lancamento_confirmado.id_lancamento == id_lancamento
        assert lancamento_confirmado.status == "confirmado"
        assert lancamento_confirmado.data_pagamento is not None
        
        # Verificar chamadas aos repositórios
        lancamento_service.repository.get_by_id.assert_called_once()
        lancamento_service.repository.update.assert_called_once()
        lancamento_service.conta_repository.get_by_id.assert_called_once()
        lancamento_service.conta_repository.atualizar_saldo.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirmar_lancamento_nao_encontrado(self, lancamento_service):
        """Teste para verificar exceção ao confirmar lançamento não encontrado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        # Mock do repositório
        lancamento_service.repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.confirmar_lancamento(
                id_lancamento, id_empresa, date.today(), id_usuario
            )
        
        assert excinfo.value.status_code == 404
        assert "Lançamento não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_confirmar_lancamento_ja_confirmado(self, lancamento_service, lancamento_mock):
        """Teste para verificar exceção ao confirmar lançamento já confirmado."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa
        id_usuario = uuid.uuid4()
        
        # Já está com status confirmado
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_mock)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.confirmar_lancamento(
                id_lancamento, id_empresa, date.today(), id_usuario
            )
        
        assert excinfo.value.status_code == 400
        assert "já está confirmado" in excinfo.value.detail.lower()

    @pytest.mark.asyncio
    async def test_cancelar_lancamento(self, lancamento_service, lancamento_mock, conta_bancaria_mock):
        """Teste para cancelar um lançamento confirmado."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa
        id_usuario = uuid.uuid4()
        
        # Mock dos repositórios
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_mock)
        lancamento_service.repository.update = AsyncMock(return_value=MagicMock(
            **{**lancamento_mock.__dict__, "status": "cancelado"}
        ))
        lancamento_service.conta_repository.get_by_id = AsyncMock(return_value=conta_bancaria_mock)
        lancamento_service.conta_repository.atualizar_saldo = AsyncMock()

        # Act
        lancamento_cancelado = await lancamento_service.cancelar_lancamento(
            id_lancamento, id_empresa, id_usuario
        )

        # Assert
        assert lancamento_cancelado is not None
        assert lancamento_cancelado.id_lancamento == id_lancamento
        assert lancamento_cancelado.status == "cancelado"
        
        # Verificar chamadas aos repositórios
        lancamento_service.repository.get_by_id.assert_called_once()
        lancamento_service.repository.update.assert_called_once()
        lancamento_service.conta_repository.get_by_id.assert_called_once()
        lancamento_service.conta_repository.atualizar_saldo.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancelar_lancamento_nao_encontrado(self, lancamento_service):
        """Teste para verificar exceção ao cancelar lançamento não encontrado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        # Mock do repositório
        lancamento_service.repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.cancelar_lancamento(
                id_lancamento, id_empresa, id_usuario
            )
        
        assert excinfo.value.status_code == 404
        assert "Lançamento não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_cancelar_lancamento_ja_cancelado(self, lancamento_service):
        """Teste para verificar exceção ao cancelar lançamento já cancelado."""
        # Arrange
        id_lancamento = uuid.uuid4()
        id_empresa = uuid.uuid4()
        id_usuario = uuid.uuid4()
        
        lancamento_cancelado = MagicMock(
            id_lancamento=id_lancamento,
            id_empresa=id_empresa,
            status="cancelado"
        )
        
        # Mock do repositório
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_cancelado)

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await lancamento_service.cancelar_lancamento(
                id_lancamento, id_empresa, id_usuario
            )
        
        assert excinfo.value.status_code == 400
        assert "já está cancelado" in excinfo.value.detail.lower()

    @pytest.mark.asyncio
    async def test_atualizar_lancamento(self, lancamento_service, lancamento_mock, categoria_mock):
        """Teste para atualizar um lançamento."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa
        id_usuario = uuid.uuid4()
        
        # Dados de atualização - mudando apenas a categoria
        dados_atualizacao = LancamentoUpdate(
            descricao="Descrição atualizada",
            id_categoria=categoria_mock.id_categoria
        )
        
        # Mock dos repositórios
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_mock)
        lancamento_service.categoria_repository.get_by_id = AsyncMock(return_value=categoria_mock)
        lancamento_service.repository.update = AsyncMock(return_value=MagicMock(
            **{**lancamento_mock.__dict__, "descricao": "Descrição atualizada"}
        ))

        # Act
        lancamento_atualizado = await lancamento_service.atualizar_lancamento(
            id_lancamento, id_empresa, dados_atualizacao, id_usuario
        )

        # Assert
        assert lancamento_atualizado is not None
        assert lancamento_atualizado.id_lancamento == id_lancamento
        assert lancamento_atualizado.descricao == "Descrição atualizada"
        
        # Verificar chamadas aos repositórios
        lancamento_service.repository.get_by_id.assert_called_once()
        lancamento_service.categoria_repository.get_by_id.assert_called_once()
        lancamento_service.repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_remover_lancamento(self, lancamento_service, lancamento_mock):
        """Teste para remover um lançamento."""
        # Arrange
        id_lancamento = lancamento_mock.id_lancamento
        id_empresa = lancamento_mock.id_empresa
        
        # Mock do repositório
        lancamento_service.repository.get_by_id = AsyncMock(return_value=lancamento_mock)
        lancamento_service.repository.delete = AsyncMock()

        # Act
        result = await lancamento_service.remover_lancamento(id_lancamento, id_empresa)

        # Assert
        assert result is True
        
        # Verificar chamadas ao repositório
        lancamento_service.repository.get_by_id.assert_called_once()
        lancamento_service.repository.delete.assert_called_once() 