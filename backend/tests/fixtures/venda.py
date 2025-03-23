"""Fixtures para testes de vendas."""
import pytest
from typing import AsyncGenerator
from uuid import uuid4
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.venda import Venda
from app.services.venda_service import VendaService
from app.services.auditoria_service import AuditoriaService

from .cliente import cliente
from .usuario import usuario


@pytest.fixture
async def venda_factory(
    session: AsyncSession,
    cliente: Cliente,
    usuario: Usuario
) -> AsyncGenerator[Venda, None]:
    """Fixture factory para criar vendas para testes."""
    created_vendas = []

    async def create_venda(
        id_cliente: str = None,
        id_usuario: str = None,
        valor_total: float = 100.00,
        desconto: float = 0.00,
        valor_final: float = None,
        forma_pagamento: str = "dinheiro",
        parcelas: int = 1,
        observacao: str = "Venda teste",
        status: str = "pendente",
        data_venda: datetime = None
    ) -> Venda:
        """Cria uma venda para teste."""
        if id_cliente is None:
            id_cliente = str(cliente.id_cliente)
        if id_usuario is None:
            id_usuario = str(usuario.id_usuario)
        if valor_final is None:
            valor_final = valor_total - desconto
        if data_venda is None:
            data_venda = datetime.now()

        service = VendaService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )

        venda = await service.create(
            id_cliente=id_cliente,
            id_usuario=id_usuario,
            valor_total=valor_total,
            desconto=desconto,
            valor_final=valor_final,
            forma_pagamento=forma_pagamento,
            parcelas=parcelas,
            observacao=observacao,
            status=status,
            data_venda=data_venda
        )
        created_vendas.append(venda)
        return venda

    yield create_venda

    # Cleanup
    for venda in created_vendas:
        await session.delete(venda)
    await session.commit()


@pytest.fixture
async def venda(venda_factory) -> Venda:
    """Fixture que retorna uma venda para teste."""
    return await venda_factory()


@pytest.fixture
async def vendas_lista(venda_factory) -> list[Venda]:
    """Fixture que retorna uma lista de vendas para teste."""
    vendas = []
    status_list = ["pendente", "finalizada", "pendente", "finalizada", "cancelada"]
    
    for i in range(5):
        venda = await venda_factory(
            valor_total=100.00 * (i + 1),
            desconto=10.00 * i,
            valor_final=100.00 * (i + 1) - (10.00 * i),
            forma_pagamento="dinheiro" if i % 2 == 0 else "cartao",
            parcelas=1 if i % 2 == 0 else 2,
            status=status_list[i],
            data_venda=datetime.now() - timedelta(days=i)
        )
        vendas.append(venda)
    return vendas 