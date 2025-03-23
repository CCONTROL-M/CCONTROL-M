"""Fixtures para testes de produtos."""
import pytest
from typing import AsyncGenerator
from uuid import uuid4
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.produto import Produto
from app.services.produto_service import ProdutoService
from app.services.auditoria_service import AuditoriaService


@pytest.fixture
async def produto_factory(session: AsyncSession) -> AsyncGenerator[Produto, None]:
    """Fixture factory para criar produtos para testes."""
    created_produtos = []

    async def create_produto(
        nome: str = "Produto Teste",
        descricao: str = "Descrição do produto teste",
        preco: Decimal = Decimal("99.99"),
        estoque: int = 10,
        codigo: str = None,
        unidade: str = "UN",
        categoria: str = "Teste",
        ativo: bool = True
    ) -> Produto:
        """Cria um produto para teste."""
        if codigo is None:
            codigo = f"PROD{str(uuid4())[:8].upper()}"

        service = ProdutoService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )

        produto = await service.create(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            codigo=codigo,
            unidade=unidade,
            categoria=categoria,
            ativo=ativo
        )
        created_produtos.append(produto)
        return produto

    yield create_produto

    # Cleanup
    for produto in created_produtos:
        await session.delete(produto)
    await session.commit()


@pytest.fixture
async def produto(produto_factory) -> Produto:
    """Fixture que retorna um produto para teste."""
    return await produto_factory()


@pytest.fixture
async def produtos_lista(produto_factory) -> list[Produto]:
    """Fixture que retorna uma lista de produtos para teste."""
    produtos = []
    categorias = ["Eletrônicos", "Móveis", "Eletrônicos", "Móveis", "Decoração"]
    
    for i in range(5):
        produto = await produto_factory(
            nome=f"Produto {i}",
            descricao=f"Descrição do produto {i}",
            preco=Decimal(str(100.00 * (i + 1))),
            estoque=10 * (i + 1),
            codigo=f"PROD{str(i+1).zfill(3)}",
            categoria=categorias[i],
            ativo=True if i < 4 else False
        )
        produtos.append(produto)
    return produtos 