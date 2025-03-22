"""
Testes para o serviço de fornecedores.

Verifica o comportamento do FornecedorService que contém a lógica de negócio.
"""
import pytest
import uuid
from fastapi import HTTPException, status
from unittest.mock import patch, AsyncMock, MagicMock
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate
from app.services.fornecedor_service import FornecedorService
from app.repositories.fornecedor_repository import FornecedorRepository


@pytest.fixture
def mock_repository():
    """Mock para o repositório de fornecedores."""
    with patch('app.services.fornecedor_service.FornecedorRepository') as mock:
        repository_instance = mock.return_value
        
        # Mock para get_by_id
        repository_instance.get_by_id = AsyncMock()
        
        # Mock para create
        repository_instance.create = AsyncMock()
        
        # Mock para update
        repository_instance.update = AsyncMock()
        
        # Mock para delete
        repository_instance.delete = AsyncMock()
        
        # Mock para list_with_filters
        repository_instance.list_with_filters = AsyncMock()
        
        # Mock para get_by_cnpj_empresa
        repository_instance.get_by_cnpj_empresa = AsyncMock(return_value=None)
        
        yield repository_instance


@pytest.fixture
def mock_db_session():
    """Mock para a sessão do banco de dados."""
    async_session = AsyncMock(spec=AsyncSession)
    async_session.__aenter__.return_value = async_session
    async_session.__aexit__.return_value = None
    return async_session


@pytest.fixture
def test_fornecedor_data():
    """Dados de exemplo para um fornecedor."""
    return {
        "id_fornecedor": uuid.uuid4(),
        "id_empresa": uuid.uuid4(),
        "nome": "Fornecedor Teste",
        "cnpj": "12345678000199",
        "email": "contato@fornecedor.com",
        "telefone": "11999887766",
        "endereco": "Rua Teste, 123",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234567",
        "contato": "João Silva",
        "avaliacao": 4,
        "ativo": True
    }


class TestFornecedorService:
    """Testes para o serviço de fornecedores."""
    
    @pytest.mark.asyncio
    async def test_get_fornecedor_existente(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para obter um fornecedor existente."""
        # Configurar mock
        mock_repository.get_by_id.return_value = test_fornecedor_data
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch o db_session para retornar nosso mock
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository):
            # Executar o método
            fornecedor = await service.get_fornecedor(
                id_fornecedor=test_fornecedor_data["id_fornecedor"],
                id_empresa=test_fornecedor_data["id_empresa"]
            )
            
            # Verificar resultado
            assert fornecedor == test_fornecedor_data
            
            # Verificar chamada do repositório
            mock_repository.get_by_id.assert_awaited_once_with(
                test_fornecedor_data["id_fornecedor"],
                test_fornecedor_data["id_empresa"]
            )
    
    @pytest.mark.asyncio
    async def test_get_fornecedor_inexistente(self, mock_repository, mock_db_session):
        """Teste para obter um fornecedor inexistente."""
        # Configurar mock para retornar None
        mock_repository.get_by_id.return_value = None
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch o db_session para retornar nosso mock
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository):
            # Executar o método e verificar se levanta a exceção correta
            with pytest.raises(HTTPException) as excinfo:
                await service.get_fornecedor(
                    id_fornecedor=uuid.uuid4(),
                    id_empresa=uuid.uuid4()
                )
            
            # Verificar detalhe da exceção
            assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
            assert excinfo.value.detail == "Fornecedor não encontrado"
    
    @pytest.mark.asyncio
    async def test_listar_fornecedores(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para listar fornecedores."""
        # Configurar mock
        mock_repository.list_with_filters.return_value = ([test_fornecedor_data], 1)
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch o db_session para retornar nosso mock
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository):
            # Executar o método
            fornecedores, total = await service.listar_fornecedores(
                id_empresa=test_fornecedor_data["id_empresa"],
                skip=0,
                limit=10,
                nome="Teste",
                cnpj="12345678000199",
                ativo=True
            )
            
            # Verificar resultado
            assert len(fornecedores) == 1
            assert fornecedores[0] == test_fornecedor_data
            assert total == 1
            
            # Verificar chamada do repositório
            mock_repository.list_with_filters.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_criar_fornecedor(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para criar um fornecedor."""
        # Configurar mock
        mock_repository.create.return_value = test_fornecedor_data
        
        # Criar dados para o novo fornecedor
        fornecedor_create = FornecedorCreate(
            id_empresa=test_fornecedor_data["id_empresa"],
            nome=test_fornecedor_data["nome"],
            cnpj=test_fornecedor_data["cnpj"],
            email=test_fornecedor_data["email"],
            telefone=test_fornecedor_data["telefone"],
            endereco=test_fornecedor_data["endereco"],
            cidade=test_fornecedor_data["cidade"],
            estado=test_fornecedor_data["estado"],
            cep=test_fornecedor_data["cep"],
            contato=test_fornecedor_data["contato"],
            avaliacao=test_fornecedor_data["avaliacao"],
            ativo=test_fornecedor_data["ativo"]
        )
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch funções necessárias
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository), \
             patch('app.services.fornecedor_service.validar_cnpj', return_value=True):  # Simulando validação de CNPJ
            # Executar o método
            fornecedor = await service.criar_fornecedor(fornecedor_create)
            
            # Verificar resultado
            assert fornecedor == test_fornecedor_data
            
            # Verificar chamada do repositório
            mock_repository.create.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_criar_fornecedor_cnpj_invalido(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para criar um fornecedor com CNPJ inválido."""
        # Criar dados para o novo fornecedor
        fornecedor_create = FornecedorCreate(
            id_empresa=test_fornecedor_data["id_empresa"],
            nome=test_fornecedor_data["nome"],
            cnpj="12345678901234",  # CNPJ inválido
            email=test_fornecedor_data["email"]
        )
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch funções necessárias
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository), \
             patch('app.services.fornecedor_service.validar_cnpj', return_value=False):  # Simulando CNPJ inválido
            # Executar o método e verificar se levanta a exceção correta
            with pytest.raises(HTTPException) as excinfo:
                await service.criar_fornecedor(fornecedor_create)
            
            # Verificar detalhe da exceção
            assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "CNPJ inválido" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_criar_fornecedor_duplicado(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para tentar criar um fornecedor com CNPJ já existente."""
        # Configurar mock para simular fornecedor existente
        mock_repository.get_by_cnpj_empresa.return_value = test_fornecedor_data
        
        # Criar dados para o novo fornecedor
        fornecedor_create = FornecedorCreate(
            id_empresa=test_fornecedor_data["id_empresa"],
            nome="Outro Fornecedor",
            cnpj=test_fornecedor_data["cnpj"],  # CNPJ já existente
            email="outro@fornecedor.com"
        )
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch funções necessárias
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository), \
             patch('app.services.fornecedor_service.validar_cnpj', return_value=True):  # Simulando CNPJ válido
            # Executar o método e verificar se levanta a exceção correta
            with pytest.raises(HTTPException) as excinfo:
                await service.criar_fornecedor(fornecedor_create)
            
            # Verificar detalhe da exceção
            assert excinfo.value.status_code == status.HTTP_409_CONFLICT
            assert "CNPJ já cadastrado" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_atualizar_fornecedor(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para atualizar um fornecedor."""
        # Preparar dados atualizados
        fornecedor_atualizado = dict(test_fornecedor_data)
        fornecedor_atualizado["nome"] = "Fornecedor Atualizado"
        fornecedor_atualizado["avaliacao"] = 5
        
        # Configurar mocks
        mock_repository.get_by_id.return_value = test_fornecedor_data
        mock_repository.update.return_value = fornecedor_atualizado
        
        # Criar dados para atualização
        fornecedor_update = FornecedorUpdate(
            nome="Fornecedor Atualizado",
            avaliacao=5
        )
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch funções necessárias
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository):
            # Executar o método
            fornecedor = await service.atualizar_fornecedor(
                id_fornecedor=test_fornecedor_data["id_fornecedor"],
                fornecedor=fornecedor_update,
                id_empresa=test_fornecedor_data["id_empresa"]
            )
            
            # Verificar resultado
            assert fornecedor["nome"] == "Fornecedor Atualizado"
            assert fornecedor["avaliacao"] == 5
            
            # Verificar chamada do repositório
            mock_repository.update.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_remover_fornecedor(self, mock_repository, mock_db_session, test_fornecedor_data):
        """Teste para remover um fornecedor."""
        # Configurar mocks
        mock_repository.get_by_id.return_value = test_fornecedor_data
        mock_repository.delete.return_value = {"detail": "Fornecedor removido com sucesso"}
        
        # Criar instância do serviço
        service = FornecedorService()
        
        # Patch funções necessárias
        with patch('app.services.fornecedor_service.db_async_session', return_value=mock_db_session), \
             patch('app.services.fornecedor_service.FornecedorRepository', return_value=mock_repository):
            # Executar o método
            resultado = await service.remover_fornecedor(
                id_fornecedor=test_fornecedor_data["id_fornecedor"],
                id_empresa=test_fornecedor_data["id_empresa"]
            )
            
            # Verificar resultado
            assert resultado["detail"] == "Fornecedor removido com sucesso"
            
            # Verificar chamada do repositório
            mock_repository.delete.assert_awaited_once_with(test_fornecedor_data["id_fornecedor"]) 