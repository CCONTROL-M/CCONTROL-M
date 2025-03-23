"""Fixtures para testes de clientes."""
import pytest
from typing import AsyncGenerator, Callable
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.empresa import Empresa
from app.schemas.cliente import ClienteCreate
from app.services.cliente_service import ClienteService
from app.services.auditoria_service import AuditoriaService

from tests.fixtures.empresa import empresa


@pytest.fixture
async def cliente_factory(
    session: AsyncSession,
    empresa: Empresa
) -> AsyncGenerator[Callable[..., AsyncGenerator[Cliente, None]], None]:
    """
    Fixture que cria uma factory para clientes.
    Permite criar clientes com dados customizados para testes.
    """
    clientes_criados = []

    async def create_cliente(
        *,
        empresa_id: uuid4 | None = None,
        empresa: Empresa | None = None,
        usuario_id: uuid4 | None = None,
        nome: str = "Cliente Teste",
        email: str = "cliente@teste.com",
        telefone: str = "(11) 99999-9999",
        cpf_cnpj: str = "123.456.789-00",
        endereco: str | None = None,
        observacao: str | None = None
    ) -> Cliente:
        """Cria um cliente com os dados fornecidos."""
        if empresa is not None:
            empresa_id = empresa.id_empresa
        if empresa_id is None:
            # Usa o fixture empresa por padrão
            empresa_id = empresa.id_empresa
        if usuario_id is None:
            usuario_id = uuid4()
        if endereco is None:
            endereco = "Rua Teste, 123"
        if observacao is None:
            observacao = "Cliente de teste"

        service = ClienteService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )
        cliente_data = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cpf_cnpj": cpf_cnpj,
            "endereco": endereco,
            "observacao": observacao
        }
        cliente_create = ClienteCreate(**cliente_data)
        cliente = await service.create(
            cliente_create,
            usuario_id,
            empresa_id
        )
        clientes_criados.append(cliente)
        return cliente

    yield create_cliente

    # Cleanup - remover clientes criados
    for cliente in clientes_criados:
        await session.delete(cliente)
    await session.commit()


@pytest.fixture
async def cliente(
    cliente_factory: Callable[..., AsyncGenerator[Cliente, None]]
) -> AsyncGenerator[Cliente, None]:
    """
    Fixture que cria um cliente padrão para testes.
    """
    cliente = await cliente_factory()
    yield cliente


@pytest.fixture
async def clientes_lista(
    cliente_factory: Callable[..., AsyncGenerator[Cliente, None]],
    empresa: Empresa
) -> AsyncGenerator[list[Cliente], None]:
    """
    Fixture que cria uma lista de clientes para testes.
    """
    clientes = []
    for i in range(5):
        cliente = await cliente_factory(
            empresa_id=empresa.id_empresa,
            nome=f"Cliente {i}",
            email=f"cliente{i}@teste.com",
            telefone=f"(11) 9{i}{i}{i}{i}-{i}{i}{i}{i}",
            cpf_cnpj=f"123.456.789-{i}{i}"
        )
        clientes.append(cliente)
    
    yield clientes 