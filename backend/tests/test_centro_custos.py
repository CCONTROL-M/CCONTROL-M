"""Testes para o serviço de centro de custos."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.centro_custo import CentroCusto
from app.schemas.centro_custo import CentroCustoCreate, CentroCustoUpdate
from app.services.centro_custo_service import CentroCustoService
from app.services.auditoria_service import AuditoriaService

# Fixtures - definição de dados para testes
@pytest.fixture
async def centro_custo(session: AsyncSession) -> CentroCusto:
    """Cria um centro de custo para testes."""
    # Criar um centro de custo diretamente no banco
    centro_custo = CentroCusto(
        id=uuid4(),
        empresa_id=uuid4(),
        nome="Centro de Custo Teste",
        descricao="Centro de Custo para testes",
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(centro_custo)
    await session.commit()
    await session.refresh(centro_custo)
    
    return centro_custo

@pytest.fixture
async def centro_custo_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[CentroCusto, None]]:
    """Factory para criar centros de custo com parâmetros customizados."""
    async def _create_centro_custo(**kwargs) -> CentroCusto:
        default_empresa_id = uuid4()  # Geramos um UUID para empresa
        
        # Valores padrão para testes
        defaults = {
            "id": uuid4(),
            "empresa_id": default_empresa_id,
            "nome": f"Centro de Custo {uuid4().hex[:8]}",
            "descricao": "Centro de Custo para testes",
            "ativo": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        centro_custo = CentroCusto(**defaults)
        session.add(centro_custo)
        await session.commit()
        await session.refresh(centro_custo)
        
        return centro_custo
    
    return _create_centro_custo

@pytest.fixture
async def centros_custo_lista(session: AsyncSession, centro_custo_factory) -> list[CentroCusto]:
    """Cria uma lista de centros de custo para testes."""
    # ID da empresa comum para todos os centros de custo
    empresa_id = uuid4()
    
    # Criar 5 centros de custo
    centros = []
    for i in range(5):
        centro_custo = await centro_custo_factory(
            empresa_id=empresa_id,
            nome=f"Centro de Custo Teste {i+1}",
            descricao=f"Descrição do Centro de Custo {i+1}"
        )
        centros.append(centro_custo)
    
    return centros


# Testes do serviço de centro de custos
@pytest.mark.asyncio
async def test_criar_centro_custo(session: AsyncSession):
    """Teste de criação de centro de custo."""
    # Arrange
    service = CentroCustoService(session)
    empresa_id = uuid4()
    
    dados_centro_custo = {
        "empresa_id": empresa_id,
        "nome": "Novo Centro de Custo",
        "descricao": "Descrição do novo centro de custo"
    }
    
    centro_custo_create = CentroCustoCreate(**dados_centro_custo)
    
    # Act
    centro_custo = await service.create(centro_custo_create)
    
    # Assert
    assert centro_custo is not None
    assert centro_custo.id is not None
    assert centro_custo.nome == "Novo Centro de Custo"
    assert centro_custo.descricao == "Descrição do novo centro de custo"
    assert centro_custo.empresa_id == empresa_id
    assert centro_custo.ativo == True


@pytest.mark.asyncio
async def test_buscar_centro_custo(session: AsyncSession, centro_custo: CentroCusto):
    """Teste de busca de centro de custo pelo ID."""
    # Arrange
    service = CentroCustoService(session)
    
    # Act
    result = await service.get(centro_custo.id)
    
    # Assert
    assert result is not None
    assert result.id == centro_custo.id
    assert result.nome == centro_custo.nome
    assert result.descricao == centro_custo.descricao


@pytest.mark.asyncio
async def test_listar_centros_custo(session: AsyncSession, centros_custo_lista: list[CentroCusto]):
    """Teste de listagem de centros de custo."""
    # Arrange
    service = CentroCustoService(session)
    empresa_id = centros_custo_lista[0].empresa_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 5
    assert total == 5
    assert all(c.empresa_id == empresa_id for c in result)


@pytest.mark.asyncio
async def test_atualizar_centro_custo(session: AsyncSession, centro_custo: CentroCusto):
    """Teste de atualização de centro de custo."""
    # Arrange
    service = CentroCustoService(session)
    
    dados_atualizacao = {
        "nome": "Centro de Custo Atualizado",
        "descricao": "Descrição atualizada para teste"
    }
    
    centro_custo_update = CentroCustoUpdate(**dados_atualizacao)
    
    # Act
    result = await service.update(
        id_centro_custo=centro_custo.id,
        centro_custo=centro_custo_update
    )
    
    # Assert
    assert result is not None
    assert result.id == centro_custo.id
    assert result.nome == "Centro de Custo Atualizado"
    assert result.descricao == "Descrição atualizada para teste"


@pytest.mark.asyncio
async def test_buscar_centro_custo_por_nome(session: AsyncSession, centros_custo_lista: list[CentroCusto]):
    """Teste de busca de centro de custo por nome."""
    # Arrange
    service = CentroCustoService(session)
    empresa_id = centros_custo_lista[0].empresa_id
    
    # Act
    result, total = await service.search_by_name(
        empresa_id=empresa_id,
        nome="Centro de Custo Teste 3",
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].nome == "Centro de Custo Teste 3"


@pytest.mark.asyncio
async def test_desativar_centro_custo(session: AsyncSession, centro_custo: CentroCusto):
    """Teste de desativação de centro de custo."""
    # Arrange
    service = CentroCustoService(session)
    
    # Act
    result = await service.toggle_active(
        id_centro_custo=centro_custo.id
    )
    
    # Assert
    assert result is not None
    assert result.ativo == False


@pytest.mark.asyncio
async def test_reativar_centro_custo(session: AsyncSession, centro_custo_factory):
    """Teste de reativação de centro de custo."""
    # Arrange
    service = CentroCustoService(session)
    centro_custo = await centro_custo_factory(ativo=False)
    
    # Act
    result = await service.toggle_active(
        id_centro_custo=centro_custo.id
    )
    
    # Assert
    assert result is not None
    assert result.ativo == True


@pytest.mark.asyncio
async def test_erro_ao_buscar_centro_custo_inexistente(session: AsyncSession):
    """Teste de erro ao buscar centro de custo inexistente."""
    # Arrange
    service = CentroCustoService(session)
    id_inexistente = uuid4()
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.get(id_inexistente)
    
    assert exc_info.value.status_code == 404
    assert "Centro de custo não encontrado" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_atualizar_centro_custo_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar centro de custo inexistente."""
    # Arrange
    service = CentroCustoService(session)
    id_inexistente = uuid4()
    
    dados_atualizacao = {
        "nome": "Centro de Custo Inexistente",
        "descricao": "Descrição atualizada"
    }
    
    centro_custo_update = CentroCustoUpdate(**dados_atualizacao)
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_centro_custo=id_inexistente,
            centro_custo=centro_custo_update
        )
    
    assert exc_info.value.status_code == 404
    assert "Centro de custo não encontrado" in str(exc_info.value.detail) 