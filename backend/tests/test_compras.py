"""Testes para o serviço de compras."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.compra import Compra
from app.models.fornecedor import Fornecedor
from app.models.produto import Produto
from app.schemas.compra import CompraCreate, CompraUpdate, StatusCompra
from app.services.compra_service import CompraService

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
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(fornecedor)
    await session.commit()
    await session.refresh(fornecedor)
    
    return fornecedor

@pytest.fixture
async def produto(session: AsyncSession, fornecedor: Fornecedor) -> Produto:
    """Cria um produto para testes."""
    # Criar um produto diretamente no banco
    produto = Produto(
        id=uuid4(),
        empresa_id=fornecedor.empresa_id,
        nome="Produto Teste",
        descricao="Produto para testes",
        preco_custo=Decimal("50.00"),
        preco_venda=Decimal("100.00"),
        estoque=10,
        codigo="PROD001",
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(produto)
    await session.commit()
    await session.refresh(produto)
    
    return produto

@pytest.fixture
async def compra(session: AsyncSession, fornecedor: Fornecedor) -> Compra:
    """Cria uma compra para testes."""
    # Criar uma compra diretamente no banco
    compra = Compra(
        id=uuid4(),
        empresa_id=fornecedor.empresa_id,
        fornecedor_id=fornecedor.id,
        usuario_id=uuid4(),
        data=date.today(),
        valor_total=Decimal("500.00"),
        status=StatusCompra.aberta,
        observacao="Compra para testes",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    session.add(compra)
    await session.commit()
    await session.refresh(compra)
    
    return compra

@pytest.fixture
async def compra_factory(session: AsyncSession) -> Callable[..., AsyncGenerator[Compra, None]]:
    """Factory para criar compras com parâmetros customizados."""
    async def _create_compra(**kwargs) -> Compra:
        default_empresa_id = uuid4()  # Geramos um UUID para empresa
        
        # Se não for fornecido fornecedor_id, criamos um fornecedor
        if "fornecedor_id" not in kwargs:
            fornecedor = Fornecedor(
                id=uuid4(),
                empresa_id=kwargs.get("empresa_id", default_empresa_id),
                nome="Fornecedor Auto",
                cpf_cnpj="98765432109876",
                email="fornecedor.auto@teste.com",
                ativo=True
            )
            session.add(fornecedor)
            await session.commit()
            await session.refresh(fornecedor)
            fornecedor_id = fornecedor.id
        else:
            fornecedor_id = kwargs["fornecedor_id"]
        
        # Valores padrão para testes
        defaults = {
            "id": uuid4(),
            "empresa_id": kwargs.get("empresa_id", default_empresa_id),
            "fornecedor_id": fornecedor_id,
            "usuario_id": uuid4(),
            "data": date.today(),
            "valor_total": Decimal("500.00"),
            "status": StatusCompra.aberta,
            "observacao": "Compra automática para testes",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Sobrescrever valores padrão com valores fornecidos
        defaults.update(kwargs)
        
        compra = Compra(**defaults)
        session.add(compra)
        await session.commit()
        await session.refresh(compra)
        
        return compra
    
    return _create_compra

@pytest.fixture
async def compras_lista(session: AsyncSession, fornecedor: Fornecedor) -> list[Compra]:
    """Cria uma lista de compras para testes."""
    
    # Criar 5 compras
    compras = []
    
    hoje = date.today()
    
    for i in range(5):
        status = StatusCompra.aberta if i < 2 else StatusCompra.finalizada
        
        compra = Compra(
            id=uuid4(),
            empresa_id=fornecedor.empresa_id,
            fornecedor_id=fornecedor.id,
            usuario_id=uuid4(),
            data=hoje - timedelta(days=i),
            valor_total=Decimal(f"{(i+1)*100}.00"),
            status=status,
            observacao=f"Compra teste {i+1}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        session.add(compra)
        await session.commit()
        await session.refresh(compra)
        
        compras.append(compra)
    
    return compras


# Testes do serviço de compras
@pytest.mark.asyncio
async def test_criar_compra(session: AsyncSession, fornecedor: Fornecedor):
    """Teste de criação de compra."""
    # Arrange
    service = CompraService(session)
    
    dados_compra = {
        "empresa_id": fornecedor.empresa_id,
        "fornecedor_id": fornecedor.id,
        "usuario_id": uuid4(),
        "data": date.today(),
        "valor_total": Decimal("500.00"),
        "observacao": "Nova compra para teste"
    }
    
    compra_create = CompraCreate(**dados_compra)
    
    # Act
    compra = await service.create(compra_create)
    
    # Assert
    assert compra is not None
    assert compra.id is not None
    assert compra.fornecedor_id == fornecedor.id
    assert compra.valor_total == Decimal("500.00")
    assert compra.status == StatusCompra.aberta
    assert compra.observacao == "Nova compra para teste"


@pytest.mark.asyncio
async def test_buscar_compra(session: AsyncSession, compra: Compra):
    """Teste de busca de compra pelo ID."""
    # Arrange
    service = CompraService(session)
    
    # Act
    result = await service.get(compra.id)
    
    # Assert
    assert result is not None
    assert result.id == compra.id
    assert result.fornecedor_id == compra.fornecedor_id
    assert result.valor_total == compra.valor_total
    assert result.status == compra.status


@pytest.mark.asyncio
async def test_listar_compras(session: AsyncSession, compras_lista: list[Compra]):
    """Teste de listagem de compras."""
    # Arrange
    service = CompraService(session)
    empresa_id = compras_lista[0].empresa_id
    
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
async def test_listar_compras_por_status(session: AsyncSession, compras_lista: list[Compra]):
    """Teste de listagem de compras por status."""
    # Arrange
    service = CompraService(session)
    empresa_id = compras_lista[0].empresa_id
    
    # Act - Buscar compras abertas
    result_abertas, total_abertas = await service.list(
        empresa_id=empresa_id,
        status=StatusCompra.aberta,
        skip=0,
        limit=10
    )
    
    # Act - Buscar compras finalizadas
    result_finalizadas, total_finalizadas = await service.list(
        empresa_id=empresa_id,
        status=StatusCompra.finalizada,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result_abertas) == 2
    assert total_abertas == 2
    assert all(c.status == StatusCompra.aberta for c in result_abertas)
    
    assert len(result_finalizadas) == 3
    assert total_finalizadas == 3
    assert all(c.status == StatusCompra.finalizada for c in result_finalizadas)


@pytest.mark.asyncio
async def test_listar_compras_por_fornecedor(session: AsyncSession, compras_lista: list[Compra]):
    """Teste de listagem de compras por fornecedor."""
    # Arrange
    service = CompraService(session)
    empresa_id = compras_lista[0].empresa_id
    fornecedor_id = compras_lista[0].fornecedor_id
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        fornecedor_id=fornecedor_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 5
    assert total == 5
    assert all(c.fornecedor_id == fornecedor_id for c in result)


@pytest.mark.asyncio
async def test_listar_compras_por_periodo(session: AsyncSession, compras_lista: list[Compra]):
    """Teste de listagem de compras por período."""
    # Arrange
    service = CompraService(session)
    empresa_id = compras_lista[0].empresa_id
    
    hoje = date.today()
    data_inicio = hoje - timedelta(days=2)
    data_fim = hoje
    
    # Act
    result, total = await service.list(
        empresa_id=empresa_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=0,
        limit=10
    )
    
    # Assert
    assert len(result) == 3
    assert total == 3
    assert all(data_inicio <= c.data <= data_fim for c in result)


@pytest.mark.asyncio
async def test_atualizar_compra(session: AsyncSession, compra: Compra):
    """Teste de atualização de compra."""
    # Arrange
    service = CompraService(session)
    
    dados_atualizacao = {
        "valor_total": Decimal("600.00"),
        "observacao": "Compra atualizada para teste"
    }
    
    compra_update = CompraUpdate(**dados_atualizacao)
    
    # Act
    result = await service.update(
        id_compra=compra.id,
        compra=compra_update
    )
    
    # Assert
    assert result is not None
    assert result.id == compra.id
    assert result.valor_total == Decimal("600.00")
    assert result.observacao == "Compra atualizada para teste"


@pytest.mark.asyncio
async def test_finalizar_compra(session: AsyncSession, compra: Compra):
    """Teste de finalização de compra."""
    # Arrange
    service = CompraService(session)
    
    # Act
    result = await service.finalizar(
        id_compra=compra.id
    )
    
    # Assert
    assert result is not None
    assert result.id == compra.id
    assert result.status == StatusCompra.finalizada


@pytest.mark.asyncio
async def test_cancelar_compra(session: AsyncSession, compra: Compra):
    """Teste de cancelamento de compra."""
    # Arrange
    service = CompraService(session)
    
    # Act
    result = await service.cancelar(
        id_compra=compra.id
    )
    
    # Assert
    assert result is not None
    assert result.id == compra.id
    assert result.status == StatusCompra.cancelada


@pytest.mark.asyncio
async def test_erro_ao_buscar_compra_inexistente(session: AsyncSession):
    """Teste de erro ao buscar compra inexistente."""
    # Arrange
    service = CompraService(session)
    id_inexistente = uuid4()
    
    # Act
    result = await service.get(id_inexistente)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_erro_ao_atualizar_compra_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar compra inexistente."""
    # Arrange
    service = CompraService(session)
    id_inexistente = uuid4()
    
    dados_atualizacao = {
        "valor_total": Decimal("700.00"),
        "observacao": "Compra inexistente"
    }
    
    compra_update = CompraUpdate(**dados_atualizacao)
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_compra=id_inexistente,
            compra=compra_update
        )
    
    assert exc_info.value.status_code == 404
    assert "Compra não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_finalizar_compra_ja_finalizada(session: AsyncSession, compra_factory):
    """Teste de erro ao finalizar uma compra já finalizada."""
    # Arrange
    service = CompraService(session)
    
    # Criar uma compra já finalizada
    compra = await compra_factory(
        status=StatusCompra.finalizada
    )
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.finalizar(
            id_compra=compra.id
        )
    
    assert exc_info.value.status_code == 400
    assert "já está finalizada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_cancelar_compra_ja_cancelada(session: AsyncSession, compra_factory):
    """Teste de erro ao cancelar uma compra já cancelada."""
    # Arrange
    service = CompraService(session)
    
    # Criar uma compra já cancelada
    compra = await compra_factory(
        status=StatusCompra.cancelada
    )
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.cancelar(
            id_compra=compra.id
        )
    
    assert exc_info.value.status_code == 400
    assert "já está cancelada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_finalizar_compra_cancelada(session: AsyncSession, compra_factory):
    """Teste de erro ao finalizar uma compra cancelada."""
    # Arrange
    service = CompraService(session)
    
    # Criar uma compra cancelada
    compra = await compra_factory(
        status=StatusCompra.cancelada
    )
    
    # Act e Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.finalizar(
            id_compra=compra.id
        )
    
    assert exc_info.value.status_code == 400
    assert "não pode ser finalizada" in str(exc_info.value.detail) 