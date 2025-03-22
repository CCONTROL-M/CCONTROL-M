import pytest
import uuid
from uuid import UUID
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.cliente_service import ClienteService
from app.schemas.cliente import ClienteCreate, ClienteUpdate


@pytest.fixture
def cliente_service():
    """Fixture para criar uma instância do serviço de clientes."""
    return ClienteService()


@pytest.fixture
def cliente_mock():
    """Fixture para simular um cliente no banco de dados."""
    return MagicMock(
        id_cliente=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Cliente Teste",
        documento="12345678901",  # CPF válido
        telefone="11987654321",
        email="cliente@teste.com",
        ativo=True
    )


@pytest.fixture
def clientes_mock():
    """Fixture para simular uma lista de clientes."""
    return [
        MagicMock(
            id_cliente=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Cliente 1",
            documento="12345678901",
            ativo=True
        ),
        MagicMock(
            id_cliente=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Cliente 2",
            documento="98765432109",
            ativo=True
        ),
        MagicMock(
            id_cliente=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Cliente 3",
            documento="11122233344",
            ativo=False
        ),
    ]


class TestClienteService:
    """Testes para o serviço de clientes."""

    @pytest.mark.asyncio
    async def test_get_cliente(self, cliente_service, cliente_mock):
        """Teste para obter um cliente pelo ID."""
        # Arrange
        id_cliente = cliente_mock.id_cliente
        id_empresa = cliente_mock.id_empresa

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.get_by_id.return_value = cliente_mock

        # Act
        cliente = await cliente_service.get_cliente(id_cliente, id_empresa)

        # Assert
        assert cliente is not None
        assert cliente.id_cliente == id_cliente
        assert cliente.id_empresa == id_empresa
        assert cliente.nome == "Cliente Teste"
        
        # Verificar chamada ao repositório
        cliente_service.get_repository.return_value.get_by_id.assert_called_once_with(
            id_cliente, id_empresa
        )

    @pytest.mark.asyncio
    async def test_get_cliente_not_found(self, cliente_service):
        """Teste para verificar exceção quando cliente não é encontrado."""
        # Arrange
        id_cliente = uuid.uuid4()
        id_empresa = uuid.uuid4()

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await cliente_service.get_cliente(id_cliente, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Cliente não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_listar_clientes(self, cliente_service, clientes_mock):
        """Teste para listar clientes com filtros."""
        # Arrange
        id_empresa = uuid.uuid4()
        skip = 0
        limit = 10
        
        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.list_with_filters.return_value = (
            clientes_mock, len(clientes_mock)
        )

        # Act
        clientes, total = await cliente_service.listar_clientes(
            id_empresa=id_empresa,
            skip=skip,
            limit=limit,
            nome="Cliente",
            cpf_cnpj="123"
        )

        # Assert
        assert len(clientes) == len(clientes_mock)
        assert total == len(clientes_mock)
        
        # Verificar chamada ao repositório com filtros corretos
        cliente_service.get_repository.return_value.list_with_filters.assert_called_once()
        call_args = cliente_service.get_repository.return_value.list_with_filters.call_args[1]
        assert call_args["id_empresa"] == id_empresa
        assert call_args["skip"] == skip
        assert call_args["limit"] == limit
        assert "nome" in call_args
        assert "cpf_cnpj" in call_args

    @pytest.mark.asyncio
    async def test_criar_cliente(self, cliente_service, cliente_mock):
        """Teste para criar um novo cliente."""
        # Arrange
        cliente_data = ClienteCreate(
            id_empresa=uuid.uuid4(),
            nome="Novo Cliente",
            documento="11122233344",
            telefone="11987654321",
            email="novo@cliente.com",
            ativo=True
        )

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.create.return_value = cliente_mock

        # Act
        cliente = await cliente_service.criar_cliente(cliente_data)

        # Assert
        assert cliente is not None
        
        # Verificar chamada ao repositório
        cliente_service.get_repository.return_value.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_cliente_cpf_invalido(self, cliente_service):
        """Teste para verificar exceção ao criar cliente com CPF inválido."""
        # Arrange
        cliente_data = ClienteCreate(
            id_empresa=uuid.uuid4(),
            nome="Cliente CPF Inválido",
            documento="12345",  # CPF inválido
            telefone="11987654321",
            email="cliente@teste.com",
            ativo=True
        )

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await cliente_service.criar_cliente(cliente_data)
        
        assert excinfo.value.status_code == 400
        assert "CPF/CNPJ inválido" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_atualizar_cliente(self, cliente_service, cliente_mock):
        """Teste para atualizar um cliente existente."""
        # Arrange
        id_cliente = cliente_mock.id_cliente
        id_empresa = cliente_mock.id_empresa
        
        cliente_data = ClienteUpdate(
            nome="Cliente Atualizado",
            telefone="11999999999",
            email="atualizado@cliente.com"
        )

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.get_by_id.return_value = cliente_mock
        cliente_service.get_repository.return_value.update.return_value = MagicMock(
            id_cliente=id_cliente,
            id_empresa=id_empresa,
            nome="Cliente Atualizado",
            documento="12345678901",
            telefone="11999999999",
            email="atualizado@cliente.com",
            ativo=True
        )

        # Act
        cliente_atualizado = await cliente_service.atualizar_cliente(
            id_cliente, cliente_data, id_empresa
        )

        # Assert
        assert cliente_atualizado is not None
        assert cliente_atualizado.nome == "Cliente Atualizado"
        assert cliente_atualizado.telefone == "11999999999"
        assert cliente_atualizado.email == "atualizado@cliente.com"
        
        # Verificar chamadas ao repositório
        cliente_service.get_repository.return_value.get_by_id.assert_called_once_with(
            id_cliente, id_empresa
        )
        cliente_service.get_repository.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_atualizar_cliente_nao_encontrado(self, cliente_service):
        """Teste para verificar exceção ao atualizar cliente não encontrado."""
        # Arrange
        id_cliente = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        cliente_data = ClienteUpdate(
            nome="Cliente Inexistente",
            telefone="11999999999",
            email="inexistente@cliente.com"
        )

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await cliente_service.atualizar_cliente(id_cliente, cliente_data, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Cliente não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_remover_cliente(self, cliente_service, cliente_mock):
        """Teste para remover um cliente."""
        # Arrange
        id_cliente = cliente_mock.id_cliente
        id_empresa = cliente_mock.id_empresa

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.get_by_id.return_value = cliente_mock
        cliente_service.get_repository.return_value.delete.return_value = True

        # Act
        resultado = await cliente_service.remover_cliente(id_cliente, id_empresa)

        # Assert
        assert resultado is True
        
        # Verificar chamadas ao repositório
        cliente_service.get_repository.return_value.get_by_id.assert_called_once_with(
            id_cliente, id_empresa
        )
        cliente_service.get_repository.return_value.delete.assert_called_once_with(
            id_cliente, id_empresa
        )

    @pytest.mark.asyncio
    async def test_remover_cliente_nao_encontrado(self, cliente_service):
        """Teste para verificar exceção ao remover cliente não encontrado."""
        # Arrange
        id_cliente = uuid.uuid4()
        id_empresa = uuid.uuid4()

        # Mock do repositório
        cliente_service.get_repository = AsyncMock()
        cliente_service.get_repository.return_value.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await cliente_service.remover_cliente(id_cliente, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Cliente não encontrado" in excinfo.value.detail 