import pytest
import uuid
from uuid import UUID
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.fornecedor_service import FornecedorService
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate


@pytest.fixture
def fornecedor_service():
    """Fixture para criar uma instância do serviço de fornecedores."""
    return FornecedorService()


@pytest.fixture
def fornecedor_mock():
    """Fixture para simular um fornecedor no banco de dados."""
    return MagicMock(
        id_fornecedor=uuid.uuid4(),
        id_empresa=uuid.uuid4(),
        nome="Fornecedor Teste",
        cnpj="12345678000199",  # CNPJ válido
        telefone="11987654321",
        email="fornecedor@teste.com",
        endereco="Rua Teste, 123",
        observacao="Observação teste",
        avaliacao=4,
        ativo=True
    )


@pytest.fixture
def fornecedores_mock():
    """Fixture para simular uma lista de fornecedores."""
    return [
        MagicMock(
            id_fornecedor=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Fornecedor 1",
            cnpj="12345678000199",
            ativo=True,
            avaliacao=5
        ),
        MagicMock(
            id_fornecedor=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Fornecedor 2",
            cnpj="98765432000199",
            ativo=True,
            avaliacao=3
        ),
        MagicMock(
            id_fornecedor=uuid.uuid4(),
            id_empresa=uuid.uuid4(),
            nome="Fornecedor 3",
            cnpj="11222333000199",
            ativo=False,
            avaliacao=4
        ),
    ]


class TestFornecedorService:
    """Testes para o serviço de fornecedores."""

    @pytest.mark.asyncio
    async def test_get_fornecedor(self, fornecedor_service, fornecedor_mock):
        """Teste para obter um fornecedor pelo ID."""
        # Arrange
        id_fornecedor = fornecedor_mock.id_fornecedor
        id_empresa = fornecedor_mock.id_empresa

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.get_by_id.return_value = fornecedor_mock

        # Act
        fornecedor = await fornecedor_service.get_fornecedor(id_fornecedor, id_empresa)

        # Assert
        assert fornecedor is not None
        assert fornecedor.id_fornecedor == id_fornecedor
        assert fornecedor.id_empresa == id_empresa
        assert fornecedor.nome == "Fornecedor Teste"
        
        # Verificar chamada ao repositório
        fornecedor_service.get_repository.return_value.get_by_id.assert_called_once_with(
            id_fornecedor, id_empresa
        )

    @pytest.mark.asyncio
    async def test_get_fornecedor_not_found(self, fornecedor_service):
        """Teste para verificar exceção quando fornecedor não é encontrado."""
        # Arrange
        id_fornecedor = uuid.uuid4()
        id_empresa = uuid.uuid4()

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await fornecedor_service.get_fornecedor(id_fornecedor, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Fornecedor não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_listar_fornecedores(self, fornecedor_service, fornecedores_mock):
        """Teste para listar fornecedores com filtros."""
        # Arrange
        id_empresa = uuid.uuid4()
        skip = 0
        limit = 10
        
        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.list_with_filters.return_value = (
            fornecedores_mock, len(fornecedores_mock)
        )

        # Act
        fornecedores, total = await fornecedor_service.listar_fornecedores(
            id_empresa=id_empresa,
            skip=skip,
            limit=limit,
            nome="Fornecedor",
            cnpj="123",
            ativo=True,
            avaliacao=4
        )

        # Assert
        assert len(fornecedores) == len(fornecedores_mock)
        assert total == len(fornecedores_mock)
        
        # Verificar chamada ao repositório com filtros corretos
        fornecedor_service.get_repository.return_value.list_with_filters.assert_called_once()
        call_args = fornecedor_service.get_repository.return_value.list_with_filters.call_args[1]
        assert call_args["id_empresa"] == id_empresa
        assert call_args["skip"] == skip
        assert call_args["limit"] == limit

    @pytest.mark.asyncio
    async def test_criar_fornecedor(self, fornecedor_service, fornecedor_mock):
        """Teste para criar um novo fornecedor."""
        # Arrange
        fornecedor_data = FornecedorCreate(
            id_empresa=uuid.uuid4(),
            nome="Novo Fornecedor",
            cnpj="12345678000199",
            telefone="11987654321",
            email="novo@fornecedor.com",
            endereco="Rua Nova, 456",
            observacao="Nova observação",
            avaliacao=5,
            ativo=True
        )

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.create.return_value = fornecedor_mock

        # Act
        fornecedor = await fornecedor_service.criar_fornecedor(fornecedor_data)

        # Assert
        assert fornecedor is not None
        
        # Verificar chamada ao repositório
        fornecedor_service.get_repository.return_value.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_criar_fornecedor_cnpj_invalido(self, fornecedor_service):
        """Teste para verificar exceção ao criar fornecedor com CNPJ inválido."""
        # Arrange
        fornecedor_data = FornecedorCreate(
            id_empresa=uuid.uuid4(),
            nome="Fornecedor CNPJ Inválido",
            cnpj="12345",  # CNPJ inválido
            telefone="11987654321",
            email="fornecedor@teste.com",
            endereco="Rua Teste, 123",
            ativo=True
        )

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await fornecedor_service.criar_fornecedor(fornecedor_data)
        
        assert excinfo.value.status_code == 400
        assert "CNPJ inválido" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_criar_fornecedor_cnpj_duplicado(self, fornecedor_service, fornecedor_mock):
        """Teste para verificar exceção ao criar fornecedor com CNPJ duplicado."""
        # Arrange
        fornecedor_data = FornecedorCreate(
            id_empresa=fornecedor_mock.id_empresa,
            nome="Fornecedor Duplicado",
            cnpj=fornecedor_mock.cnpj,  # CNPJ já existente
            telefone="11987654321",
            email="duplicado@teste.com",
            ativo=True
        )

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.verificar_cnpj_duplicado.return_value = True

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await fornecedor_service.criar_fornecedor(fornecedor_data)
        
        assert excinfo.value.status_code == 400
        assert "já existe um fornecedor com este CNPJ" in excinfo.value.detail.lower()

    @pytest.mark.asyncio
    async def test_atualizar_fornecedor(self, fornecedor_service, fornecedor_mock):
        """Teste para atualizar um fornecedor existente."""
        # Arrange
        id_fornecedor = fornecedor_mock.id_fornecedor
        id_empresa = fornecedor_mock.id_empresa
        
        fornecedor_data = FornecedorUpdate(
            nome="Fornecedor Atualizado",
            telefone="11999999999",
            email="atualizado@fornecedor.com",
            avaliacao=5
        )

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.get_by_id.return_value = fornecedor_mock
        fornecedor_service.get_repository.return_value.update.return_value = MagicMock(
            id_fornecedor=id_fornecedor,
            id_empresa=id_empresa,
            nome="Fornecedor Atualizado",
            cnpj="12345678000199",
            telefone="11999999999",
            email="atualizado@fornecedor.com",
            avaliacao=5,
            ativo=True
        )

        # Act
        fornecedor_atualizado = await fornecedor_service.atualizar_fornecedor(
            id_fornecedor, fornecedor_data, id_empresa
        )

        # Assert
        assert fornecedor_atualizado is not None
        assert fornecedor_atualizado.nome == "Fornecedor Atualizado"
        assert fornecedor_atualizado.telefone == "11999999999"
        assert fornecedor_atualizado.email == "atualizado@fornecedor.com"
        assert fornecedor_atualizado.avaliacao == 5
        
        # Verificar chamadas ao repositório
        fornecedor_service.get_repository.return_value.get_by_id.assert_called_once_with(
            id_fornecedor, id_empresa
        )
        fornecedor_service.get_repository.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_atualizar_fornecedor_nao_encontrado(self, fornecedor_service):
        """Teste para verificar exceção ao atualizar fornecedor não encontrado."""
        # Arrange
        id_fornecedor = uuid.uuid4()
        id_empresa = uuid.uuid4()
        
        fornecedor_data = FornecedorUpdate(
            nome="Fornecedor Inexistente",
            telefone="11999999999",
            email="inexistente@fornecedor.com"
        )

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await fornecedor_service.atualizar_fornecedor(id_fornecedor, fornecedor_data, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Fornecedor não encontrado" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_remover_fornecedor(self, fornecedor_service, fornecedor_mock):
        """Teste para remover um fornecedor."""
        # Arrange
        id_fornecedor = fornecedor_mock.id_fornecedor
        id_empresa = fornecedor_mock.id_empresa

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.get_by_id.return_value = fornecedor_mock
        fornecedor_service.get_repository.return_value.delete.return_value = True

        # Act
        resultado = await fornecedor_service.remover_fornecedor(id_fornecedor, id_empresa)

        # Assert
        assert resultado is True
        
        # Verificar chamadas ao repositório
        fornecedor_service.get_repository.return_value.get_by_id.assert_called_once_with(
            id_fornecedor, id_empresa
        )
        fornecedor_service.get_repository.return_value.delete.assert_called_once_with(
            id_fornecedor, id_empresa
        )

    @pytest.mark.asyncio
    async def test_remover_fornecedor_nao_encontrado(self, fornecedor_service):
        """Teste para verificar exceção ao remover fornecedor não encontrado."""
        # Arrange
        id_fornecedor = uuid.uuid4()
        id_empresa = uuid.uuid4()

        # Mock do repositório
        fornecedor_service.get_repository = AsyncMock()
        fornecedor_service.get_repository.return_value.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await fornecedor_service.remover_fornecedor(id_fornecedor, id_empresa)
        
        assert excinfo.value.status_code == 404
        assert "Fornecedor não encontrado" in excinfo.value.detail 