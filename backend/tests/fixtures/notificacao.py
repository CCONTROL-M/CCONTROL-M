"""Fixtures para testes de notificações."""
import pytest
from typing import AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notificacao import Notificacao
from app.services.notificacao_service import NotificacaoService
from app.services.auditoria_service import AuditoriaService

from .usuario import usuario


@pytest.fixture
async def notificacao_factory(
    session: AsyncSession,
    usuario: Usuario
) -> AsyncGenerator[Notificacao, None]:
    """Fixture factory para criar notificações para testes."""
    created_notificacoes = []

    async def create_notificacao(
        id_usuario: str = None,
        titulo: str = "Notificação de Teste",
        mensagem: str = "Esta é uma notificação de teste",
        tipo: str = "info",
        lida: bool = False,
        data_criacao: datetime = None,
        data_leitura: datetime = None
    ) -> Notificacao:
        """Cria uma notificação para teste."""
        if id_usuario is None:
            id_usuario = str(usuario.id_usuario)
        if data_criacao is None:
            data_criacao = datetime.now()

        service = NotificacaoService(
            session=session,
            auditoria_service=AuditoriaService(session=session)
        )
        notificacao = await service.create(
            id_usuario=id_usuario,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo
        )
        if lida:
            notificacao = await service.mark_as_read(notificacao.id_notificacao)
        created_notificacoes.append(notificacao)
        return notificacao

    yield create_notificacao

    # Cleanup
    for notificacao in created_notificacoes:
        await session.delete(notificacao)
    await session.commit()


@pytest.fixture
async def notificacao(notificacao_factory) -> Notificacao:
    """Fixture que retorna uma notificação para teste."""
    return await notificacao_factory()


@pytest.fixture
async def notificacoes_lista(
    notificacao_factory,
    usuario: Usuario
) -> list[Notificacao]:
    """Fixture que retorna uma lista de notificações para teste."""
    notificacoes = []
    tipos = ["info", "success", "warning", "error", "info"]
    lidas = [False, True, False, True, False]
    
    for i in range(5):
        notificacao = await notificacao_factory(
            id_usuario=str(usuario.id_usuario),
            titulo=f"Notificação {i}",
            mensagem=f"Esta é a notificação de teste número {i}",
            tipo=tipos[i],
            lida=lidas[i]
        )
        notificacoes.append(notificacao)
    return notificacoes 