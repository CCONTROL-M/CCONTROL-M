"""Fixtures para testes de auditoria."""
import pytest
from typing import AsyncGenerator
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auditoria import Auditoria
from app.services.auditoria_service import AuditoriaService

from .usuario import usuario


@pytest.fixture
async def auditoria_factory(
    session: AsyncSession,
    usuario: Usuario
) -> AsyncGenerator[Auditoria, None]:
    """Fixture factory para criar registros de auditoria para testes."""
    created_registros = []

    async def create_registro(
        id_usuario: str = None,
        entidade: str = "Cliente",
        operacao: str = "CREATE",
        valor_anterior: dict = None,
        valor_atual: dict = {"nome": "Cliente Teste"},
        data_hora: datetime = None
    ) -> Auditoria:
        """Cria um registro de auditoria para teste."""
        if id_usuario is None:
            id_usuario = str(usuario.id_usuario)
        if data_hora is None:
            data_hora = datetime.now()

        service = AuditoriaService(session=session)
        registro = await service.create(
            id_usuario=id_usuario,
            entidade=entidade,
            operacao=operacao,
            valor_anterior=valor_anterior,
            valor_atual=valor_atual
        )
        created_registros.append(registro)
        return registro

    yield create_registro

    # Cleanup
    for registro in created_registros:
        await session.delete(registro)
    await session.commit()


@pytest.fixture
async def auditoria(auditoria_factory) -> Auditoria:
    """Fixture que retorna um registro de auditoria para teste."""
    return await auditoria_factory()


@pytest.fixture
async def auditoria_lista(
    auditoria_factory,
    usuario: Usuario
) -> list[Auditoria]:
    """Fixture que retorna uma lista de registros de auditoria para teste."""
    registros = []
    operacoes = ["CREATE", "UPDATE", "DELETE", "READ", "UPDATE"]
    entidades = ["Cliente", "Produto", "Venda", "Usuario", "Empresa"]
    
    for i in range(5):
        registro = await auditoria_factory(
            id_usuario=str(usuario.id_usuario),
            entidade=entidades[i],
            operacao=operacoes[i],
            valor_anterior={"nome": f"Valor Anterior {i}"} if operacoes[i] == "UPDATE" else None,
            valor_atual={"nome": f"Valor Atual {i}"},
            data_hora=datetime.now()
        )
        registros.append(registro)
    return registros 