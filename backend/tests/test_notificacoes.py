"""Testes para o serviço de notificações."""
import pytest
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.notificacao_service import NotificacaoService
from app.services.auditoria_service import AuditoriaService

from .fixtures.notificacao import notificacao, notificacoes_lista
from .fixtures.usuario import usuario


@pytest.mark.asyncio
async def test_criar_notificacao(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a criação de uma notificação."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    notificacao = await service.create(
        id_usuario=str(usuario.id_usuario),
        titulo="Teste de Notificação",
        mensagem="Esta é uma notificação de teste",
        tipo="info"
    )
    
    assert notificacao.id_notificacao is not None
    assert notificacao.id_usuario == str(usuario.id_usuario)
    assert notificacao.titulo == "Teste de Notificação"
    assert notificacao.mensagem == "Esta é uma notificação de teste"
    assert notificacao.tipo == "info"
    assert notificacao.lida is False
    assert isinstance(notificacao.data_criacao, datetime)


@pytest.mark.asyncio
async def test_marcar_notificacao_como_lida(
    session: AsyncSession,
    notificacao: Notificacao
):
    """Testa marcar uma notificação como lida."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    notificacao_atualizada = await service.mark_as_read(notificacao.id_notificacao)
    
    assert notificacao_atualizada.id_notificacao == notificacao.id_notificacao
    assert notificacao_atualizada.lida is True
    assert isinstance(notificacao_atualizada.data_leitura, datetime)


@pytest.mark.asyncio
async def test_buscar_notificacao(
    session: AsyncSession,
    notificacao: Notificacao
):
    """Testa a busca de uma notificação por ID."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    notificacao_encontrada = await service.get_by_id(notificacao.id_notificacao)
    
    assert notificacao_encontrada.id_notificacao == notificacao.id_notificacao
    assert notificacao_encontrada.id_usuario == notificacao.id_usuario
    assert notificacao_encontrada.titulo == notificacao.titulo
    assert notificacao_encontrada.mensagem == notificacao.mensagem
    assert notificacao_encontrada.tipo == notificacao.tipo
    assert notificacao_encontrada.lida == notificacao.lida
    assert notificacao_encontrada.data_criacao == notificacao.data_criacao


@pytest.mark.asyncio
async def test_listar_notificacoes_usuario(
    session: AsyncSession,
    notificacoes_lista: list[Notificacao],
    usuario: Usuario
):
    """Testa a listagem de notificações de um usuário."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    notificacoes = await service.list_by_user(str(usuario.id_usuario))
    
    assert len(notificacoes) >= len(notificacoes_lista)
    for notificacao in notificacoes_lista:
        assert any(n.id_notificacao == notificacao.id_notificacao for n in notificacoes)


@pytest.mark.asyncio
async def test_listar_notificacoes_nao_lidas(
    session: AsyncSession,
    notificacoes_lista: list[Notificacao],
    usuario: Usuario
):
    """Testa a listagem de notificações não lidas de um usuário."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    notificacoes = await service.list_unread(str(usuario.id_usuario))
    
    assert all(not n.lida for n in notificacoes)
    assert len(notificacoes) <= len(notificacoes_lista)


@pytest.mark.asyncio
async def test_marcar_todas_notificacoes_como_lidas(
    session: AsyncSession,
    notificacoes_lista: list[Notificacao],
    usuario: Usuario
):
    """Testa marcar todas as notificações de um usuário como lidas."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    await service.mark_all_as_read(str(usuario.id_usuario))
    
    notificacoes = await service.list_by_user(str(usuario.id_usuario))
    assert all(n.lida for n in notificacoes)
    assert all(isinstance(n.data_leitura, datetime) for n in notificacoes)


@pytest.mark.asyncio
async def test_deletar_notificacao(
    session: AsyncSession,
    notificacao: Notificacao
):
    """Testa a deleção de uma notificação."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    await service.delete(notificacao.id_notificacao)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(notificacao.id_notificacao)
    
    assert exc_info.value.status_code == 404
    assert "Notificação não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_buscar_notificacao_inexistente(session: AsyncSession):
    """Testa o erro ao buscar uma notificação inexistente."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(str(uuid4()))
    
    assert exc_info.value.status_code == 404
    assert "Notificação não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_marcar_notificacao_inexistente_como_lida(session: AsyncSession):
    """Testa o erro ao marcar uma notificação inexistente como lida."""
    service = NotificacaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.mark_as_read(str(uuid4()))
    
    assert exc_info.value.status_code == 404
    assert "Notificação não encontrada" in str(exc_info.value.detail) 