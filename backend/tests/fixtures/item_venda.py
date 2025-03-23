"""Fixtures para testes de itens de venda."""
import pytest
from typing import AsyncGenerator
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item_venda import ItemVenda
from app.services.item_venda_service import ItemVendaService
from app.services.auditoria_service import AuditoriaService

from .venda import venda
from .produto import produto


@pytest.fixture
async def item_venda_factory(
    session: AsyncSession,
    venda: Venda,
    produto: Produto
) -> AsyncGenerator[ItemVenda, None]:
    """Fixture factory para criar itens de venda para testes."""
    created_itens = []

    async def create_item(
        id_venda: str = None,
        id_produto: str = None,
        quantidade: int = 1,
        preco_unitario: Decimal = None,
        desconto: Decimal = Decimal("0.00"),
        valor_total: Decimal = None
    ) -> ItemVenda:
        """Cria um item de venda para teste."""
        if id_venda is None:
            id_venda = str(venda.id_venda)
        if id_produto is None:
            id_produto = str(produto.id_produto)
        if preco_unitario is None:
            preco_unitario = produto.preco
        if valor_total is None:
            valor_total = (quantidade * preco_unitario) - desconto

        service = ItemVendaService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )

        item = await service.create(
            id_venda=id_venda,
            id_produto=id_produto,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            desconto=desconto,
            valor_total=valor_total
        )
        created_itens.append(item)
        return item

    yield create_item

    # Cleanup
    for item in created_itens:
        await session.delete(item)
    await session.commit()


@pytest.fixture
async def item_venda(item_venda_factory) -> ItemVenda:
    """Fixture que retorna um item de venda para teste."""
    return await item_venda_factory()


@pytest.fixture
async def itens_venda_lista(
    item_venda_factory,
    venda: Venda,
    produto: Produto
) -> list[ItemVenda]:
    """Fixture que retorna uma lista de itens de venda para teste."""
    itens = []
    
    for i in range(5):
        item = await item_venda_factory(
            id_venda=str(venda.id_venda),
            id_produto=str(produto.id_produto),
            quantidade=i + 1,
            preco_unitario=produto.preco,
            desconto=Decimal(str(10.00 * i)),
            valor_total=((i + 1) * produto.preco) - Decimal(str(10.00 * i))
        )
        itens.append(item)
    return itens 