"""Testes para o serviço de fornecedores."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.fornecedor import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate
from app.services.fornecedor_service import FornecedorService
from app.services.auditoria_service import AuditoriaService

# Fixtures - definição de dados para testes
@pytest.fixture
async def fornecedor(session: AsyncSession) -> Fornecedor:
    """Cria um fornecedor para testes."""
    # Criar um fornecedor diretamente no banco
    fornecedor = Fornecedor(
        id=uuid4(),
        empresa_id=uuid4(),
        nome="Fornecedor Teste",
        cpf_cnpj="12345678901234",
        email="fornecedor@teste.com",
        telefone="1199999999",
        endereco="Rua de Teste, 123",
        cidade="São Paulo",
        estado="SP",
        cep="01234567",
        observacoes="Fornecedor para testes",
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(fornecedor)
    await session.commit()
    await session.refresh(fornecedor)
    
    return fornecedor

@pytest.fixture
async def fornecedor_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[Fornecedor, None]]:
    """Factory para criar fornecedores com parâmetros customizados."""
    async def _create_fornecedor(**kwargs) -> Fornecedor:
        default_empresa_id = uuid4()  # Geramos um UUID para empresa
        
        # Valores padrão para testes
        defaults = {
            "id": uuid4(),
            "empresa_id": default_empresa_id,
            "nome": f"Fornecedor {uuid4().hex[:8]}",
            "cpf_cnpj": "12345678901234",
            "email": f"fornecedor_{uuid4().hex[:8]}@teste.com",
            "telefone": "1199999999",
            "endereco": "Rua de Teste, 123",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234567",
            "observacoes": "Fornecedor para testes",
            "ativo": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        fornecedor = Fornecedor(**defaults)
        session.add(fornecedor)
        await session.commit()
        await session.refresh(fornecedor)
        
        return fornecedor
    
    return _create_fornecedor

@pytest.fixture
async def fornecedores_lista(session: AsyncSession, fornecedor_factory) -> list[Fornecedor]:
    """Cria uma lista de fornecedores para testes."""
    # ID da empresa comum para todos os fornecedores
    empresa_id = uuid4()
    
    # Criar 5 fornecedores
    fornecedores = []
    for i in range(5):
        fornecedor = await fornecedor_factory(
            empresa_id=empresa_id,
            nome=f"Fornecedor Teste {i+1}",
            cpf_cnpj=f"1234567890{i+1:04d}"
        )
        fornecedores.append(fornecedor)
    
    return fornecedores


# Testes do serviço de fornecedores
@pytest.mark.asyncio
async def test_criar_fornecedor(session: AsyncSession):
    """Teste de criação de fornecedor."""
    # Arrange
    service = FornecedorService(session)
    empresa_id = uuid4()
    
    dados_fornecedor = {
        "empresa_id": empresa_id,
        "nome": "Novo Fornecedor",
        "cpf_cnpj": "98765432109876",
        "email": "novo@fornecedor.com",
        "telefone": "1188888888",
        "endereco": "Rua Nova, 456",
        "cidade": "Rio de Janeiro",
        "estado": "RJ",
        "cep": "98765432",
        "observacoes": "Novo fornecedor para teste"
    }
    
    fornecedor_create = FornecedorCreate(**dados_fornecedor)
    
    # Act
    fornecedor = await service.create(fornecedor_create)
    
    # Assert
    assert fornecedor is not None
    assert fornecedor.id is not None
    assert fornecedor.nome == "Novo Fornecedor"
    assert fornecedor.cpf_cnpj == "98765432109876"
    assert fornecedor.email == "novo@fornecedor.com"
    assert fornecedor.empresa_id == empresa_id
    assert fornecedor.ativo == True


@pytest.mark.asyncio
async def test_buscar_fornecedor(session: AsyncSession, fornecedor: Fornecedor):
    """Teste de busca de fornecedor pelo ID."""
    # Arrange
    service = FornecedorService(session)
    
    # Act
    result = await service.get(fornecedor.id)
    
    # Assert
    assert result is not None
    assert result.id == fornecedor.id
    assert result.nome == fornecedor.nome
    assert result.cpf_cnpj == fornecedor.cpf_cnpj


@pytest.mark.asyncio
async def test_listar_fornecedores(session: AsyncSession, fornecedores_lista: list[Fornecedor]):
    """Teste de listagem de fornecedores."""
    # Arrange
    service = FornecedorService(session)
    empresa_id = fornecedores_lista[0].empresa_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 5
    assert total == 5
    assert all(f.empresa_id == empresa_id for f in result)


@pytest.mark.asyncio
async def test_atualizar_fornecedor(session: AsyncSession, fornecedor: Fornecedor):
    """Teste de atualização de fornecedor."""
    # Arrange
    service = FornecedorService(session)
    
    dados_atualizacao = {
        "nome": "Fornecedor Atualizado",
        "email": "atualizado@fornecedor.com",
        "telefone": "1177777777",
        "observacoes": "Fornecedor atualizado para teste"
    }
    
    fornecedor_update = FornecedorUpdate(**dados_atualizacao)
    
    # Act
    result = await service.update(
        id_fornecedor=fornecedor.id,
        fornecedor=fornecedor_update
    )
    
    # Assert
    assert result is not None
    assert result.id == fornecedor.id
    assert result.nome == "Fornecedor Atualizado"
    assert result.email == "atualizado@fornecedor.com"
    assert result.telefone == "1177777777"
    assert result.observacoes == "Fornecedor atualizado para teste"


@pytest.mark.asyncio
async def test_buscar_fornecedor_por_nome(session: AsyncSession, fornecedores_lista: list[Fornecedor]):
    """Teste de busca de fornecedor por nome."""
    # Arrange
    service = FornecedorService(session)
    empresa_id = fornecedores_lista[0].empresa_id
    
    # Act
    result, total = await service.search_by_name(
        empresa_id=empresa_id,
        nome="Fornecedor Teste 3",
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].nome == "Fornecedor Teste 3"


@pytest.mark.asyncio
async def test_desativar_fornecedor(session: AsyncSession, fornecedor: Fornecedor):
    """Teste de desativação de fornecedor."""
    # Arrange
    service = FornecedorService(session)
    
    # Act
    result = await service.toggle_active(
        id_fornecedor=fornecedor.id
    )
    
    # Assert
    assert result is not None
    assert result.ativo == False


@pytest.mark.asyncio
async def test_reativar_fornecedor(session: AsyncSession, fornecedor_factory):
    """Teste de reativação de fornecedor."""
    # Arrange
    service = FornecedorService(session)
    fornecedor = await fornecedor_factory(ativo=False)
    
    # Act
    result = await service.toggle_active(
        id_fornecedor=fornecedor.id
    )
    
    # Assert
    assert result is not None
    assert result.ativo == True


@pytest.mark.asyncio
async def test_erro_ao_buscar_fornecedor_inexistente(session: AsyncSession):
    """Teste de erro ao buscar fornecedor inexistente."""
    # Arrange
    service = FornecedorService(session)
    id_inexistente = uuid4()
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.get(id_inexistente)
    
    assert exc_info.value.status_code == 404
    assert "Fornecedor não encontrado" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_atualizar_fornecedor_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar fornecedor inexistente."""
    # Arrange
    service = FornecedorService(session)
    id_inexistente = uuid4()
    
    dados_atualizacao = {
        "nome": "Fornecedor Inexistente",
        "email": "inexistente@fornecedor.com"
    }
    
    fornecedor_update = FornecedorUpdate(**dados_atualizacao)
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_fornecedor=id_inexistente,
            fornecedor=fornecedor_update
        )
    
    assert exc_info.value.status_code == 404
    assert "Fornecedor não encontrado" in str(exc_info.value.detail) 