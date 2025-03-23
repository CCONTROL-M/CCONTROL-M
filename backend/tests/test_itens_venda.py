"""Testes para o serviço de itens de venda."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.item_venda import ItemVenda
from app.schemas.item_venda import ItemVendaCreate, ItemVendaUpdate
from app.services.item_venda_service import ItemVendaService
from app.services.auditoria_service import AuditoriaService

from .fixtures.item_venda import item_venda, item_venda_factory, itens_venda_lista
from .fixtures.venda import venda
from .fixtures.produto import produto


@pytest.mark.asyncio
async def test_criar_item_venda(
    session: AsyncSession,
    item_venda_factory: Callable[..., AsyncGenerator[ItemVenda, None]],
    venda: Venda,
    produto: Produto
):
    """Teste de criação de item de venda."""
    # Arrange
    quantidade = 2
    preco_unitario = produto.preco
    desconto = Decimal("10.00")
    valor_total = (quantidade * preco_unitario) - desconto
    
    # Act
    item = await item_venda_factory(
        id_venda=venda.id_venda,
        id_produto=produto.id_produto,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        desconto=desconto,
        valor_total=valor_total
    )
    
    # Assert
    assert item.id_item_venda is not None
    assert item.id_venda == venda.id_venda
    assert item.id_produto == produto.id_produto
    assert item.quantidade == quantidade
    assert item.preco_unitario == preco_unitario
    assert item.desconto == desconto
    assert item.valor_total == valor_total


@pytest.mark.asyncio
async def test_atualizar_item_venda(
    session: AsyncSession,
    item_venda: ItemVenda
):
    """Teste de atualização de item de venda."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    nova_quantidade = 3
    novo_desconto = Decimal("15.00")
    novo_valor_total = (nova_quantidade * item_venda.preco_unitario) - novo_desconto
    
    item_update = ItemVendaUpdate(
        quantidade=nova_quantidade,
        desconto=novo_desconto,
        valor_total=novo_valor_total
    )
    
    # Act
    item_atualizado = await service.update(
        item_venda.id_item_venda,
        item_update
    )
    
    # Assert
    assert item_atualizado.id_item_venda == item_venda.id_item_venda
    assert item_atualizado.quantidade == nova_quantidade
    assert item_atualizado.desconto == novo_desconto
    assert item_atualizado.valor_total == novo_valor_total


@pytest.mark.asyncio
async def test_buscar_item_venda(
    session: AsyncSession,
    item_venda: ItemVenda
):
    """Teste de busca de item de venda por ID."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    item_encontrado = await service.get_by_id(item_venda.id_item_venda)
    
    # Assert
    assert item_encontrado is not None
    assert item_encontrado.id_item_venda == item_venda.id_item_venda
    assert item_encontrado.id_venda == item_venda.id_venda
    assert item_encontrado.id_produto == item_venda.id_produto
    assert item_encontrado.quantidade == item_venda.quantidade
    assert item_encontrado.valor_total == item_venda.valor_total


@pytest.mark.asyncio
async def test_listar_itens_venda(
    session: AsyncSession,
    itens_venda_lista: list[ItemVenda]
):
    """Teste de listagem de itens de venda."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    resultado = await service.get_multi(
        skip=0,
        limit=10
    )
    
    # Assert
    assert resultado.total == 5
    assert len(resultado.items) == 5
    assert resultado.page == 1


@pytest.mark.asyncio
async def test_buscar_itens_por_venda(
    session: AsyncSession,
    itens_venda_lista: list[ItemVenda],
    venda: Venda
):
    """Teste de busca de itens por venda."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    itens = await service.get_by_venda(venda.id_venda)
    
    # Assert
    assert len(itens) > 0
    for item in itens:
        assert item.id_venda == venda.id_venda


@pytest.mark.asyncio
async def test_buscar_itens_por_produto(
    session: AsyncSession,
    itens_venda_lista: list[ItemVenda],
    produto: Produto
):
    """Teste de busca de itens por produto."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    itens = await service.get_by_produto(produto.id_produto)
    
    # Assert
    assert len(itens) > 0
    for item in itens:
        assert item.id_produto == produto.id_produto


@pytest.mark.asyncio
async def test_excluir_item_venda(
    session: AsyncSession,
    item_venda: ItemVenda
):
    """Teste de exclusão de item de venda."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    await service.delete(item_venda.id_item_venda)
    
    # Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_by_id(item_venda.id_item_venda)
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_criar_item_venda_sem_estoque(
    session: AsyncSession,
    item_venda_factory: Callable[..., AsyncGenerator[ItemVenda, None]],
    venda: Venda,
    produto: Produto
):
    """Teste de erro ao criar item de venda sem estoque suficiente."""
    # Arrange
    quantidade = produto.estoque + 1  # Quantidade maior que o estoque
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await item_venda_factory(
            id_venda=venda.id_venda,
            id_produto=produto.id_produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            valor_total=quantidade * produto.preco
        )
    assert excinfo.value.status_code == 400
    assert "estoque insuficiente" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_buscar_item_venda_inexistente(session: AsyncSession):
    """Teste de erro ao buscar item de venda inexistente."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_by_id(uuid4())
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_atualizar_item_venda_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar item de venda inexistente."""
    # Arrange
    service = ItemVendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    item_update = ItemVendaUpdate(quantidade=1)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.update(uuid4(), item_update)
    assert excinfo.value.status_code == 404
    assert "não encontrado" in str(excinfo.value.detail) 