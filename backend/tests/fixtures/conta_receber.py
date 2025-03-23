"""Fixtures para testes de contas a receber."""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal
from typing import Callable, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conta_receber import ContaReceber
from app.schemas.conta_receber import ContaReceberCreate, StatusContaReceber
from app.services.conta_receber_service import ContaReceberService
from app.services.auditoria_service import AuditoriaService
from .cliente import cliente


@pytest.fixture
async def conta_receber_factory(
    session: AsyncSession,
    cliente: Cliente
) -> AsyncGenerator[ContaReceber, None]:
    """Fixture factory para criar contas a receber para testes."""
    created_contas = []

    async def create_conta(
        id_cliente: str = None,
        descricao: str = "Conta teste",
        valor: Decimal = Decimal("1000.00"),
        data_vencimento: date = None,
        observacao: str = "Observação teste",
        status: str = "pendente",
        data_recebimento: date = None,
        valor_recebido: Decimal = None
    ) -> ContaReceber:
        """Cria uma conta a receber para teste."""
        if id_cliente is None:
            id_cliente = str(cliente.id_cliente)
        if data_vencimento is None:
            data_vencimento = date.today() + timedelta(days=30)

        service = ContaReceberService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )

        conta = await service.create(
            id_cliente=id_cliente,
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            observacao=observacao,
            status=status,
            data_recebimento=data_recebimento,
            valor_recebido=valor_recebido
        )
        created_contas.append(conta)
        return conta

    yield create_conta

    # Cleanup
    for conta in created_contas:
        await session.delete(conta)
    await session.commit()


@pytest.fixture
async def conta_receber(conta_receber_factory) -> ContaReceber:
    """Fixture que retorna uma conta a receber para teste."""
    return await conta_receber_factory()


@pytest.fixture
async def contas_receber_lista(
    conta_receber_factory,
    cliente: Cliente
) -> list[ContaReceber]:
    """Fixture que retorna uma lista de contas a receber para teste."""
    contas = []
    status_list = ["pendente", "recebido", "pendente", "recebido", "cancelado"]
    
    for i in range(5):
        conta = await conta_receber_factory(
            id_cliente=str(cliente.id_cliente),
            descricao=f"Conta {i}",
            valor=Decimal(str(1000.00 * (i + 1))),
            data_vencimento=date.today() + timedelta(days=(i + 1) * 10),
            observacao=f"Observação da conta {i}",
            status=status_list[i],
            data_recebimento=date.today() if status_list[i] == "recebido" else None,
            valor_recebido=Decimal(str(1000.00 * (i + 1))) if status_list[i] == "recebido" else None
        )
        contas.append(conta)
    return contas 