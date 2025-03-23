"""Fixtures para testes de contas a pagar."""
import pytest
from typing import AsyncGenerator
from uuid import uuid4
from decimal import Decimal
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conta_pagar import ContaPagar
from app.services.conta_pagar_service import ContaPagarService
from app.services.auditoria_service import AuditoriaService


@pytest.fixture
async def conta_pagar_factory(session: AsyncSession) -> AsyncGenerator[ContaPagar, None]:
    """Fixture factory para criar contas a pagar para testes."""
    created_contas = []

    async def create_conta(
        descricao: str = "Conta teste",
        valor: Decimal = Decimal("1000.00"),
        data_vencimento: date = None,
        observacao: str = "Observação teste",
        status: str = "pendente",
        data_pagamento: date = None,
        valor_pago: Decimal = None
    ) -> ContaPagar:
        """Cria uma conta a pagar para teste."""
        if data_vencimento is None:
            data_vencimento = date.today() + timedelta(days=30)

        service = ContaPagarService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )

        conta = await service.create(
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            observacao=observacao,
            status=status,
            data_pagamento=data_pagamento,
            valor_pago=valor_pago
        )
        created_contas.append(conta)
        return conta

    yield create_conta

    # Cleanup
    for conta in created_contas:
        await session.delete(conta)
    await session.commit()


@pytest.fixture
async def conta_pagar(conta_pagar_factory) -> ContaPagar:
    """Fixture que retorna uma conta a pagar para teste."""
    return await conta_pagar_factory()


@pytest.fixture
async def contas_pagar_lista(conta_pagar_factory) -> list[ContaPagar]:
    """Fixture que retorna uma lista de contas a pagar para teste."""
    contas = []
    status_list = ["pendente", "pago", "pendente", "pago", "cancelado"]
    
    for i in range(5):
        conta = await conta_pagar_factory(
            descricao=f"Conta {i}",
            valor=Decimal(str(1000.00 * (i + 1))),
            data_vencimento=date.today() + timedelta(days=(i + 1) * 10),
            observacao=f"Observação da conta {i}",
            status=status_list[i],
            data_pagamento=date.today() if status_list[i] == "pago" else None,
            valor_pago=Decimal(str(1000.00 * (i + 1))) if status_list[i] == "pago" else None
        )
        contas.append(conta)
    return contas 