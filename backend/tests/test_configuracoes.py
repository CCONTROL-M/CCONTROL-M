"""Testes para o serviço de configurações."""
import pytest
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.configuracao_service import ConfiguracaoService
from app.services.auditoria_service import AuditoriaService

from .fixtures.configuracao import configuracao, configuracoes_lista
from .fixtures.usuario import usuario


@pytest.mark.asyncio
async def test_criar_configuracao(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a criação de uma configuração."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    configuracao = await service.create(
        chave="TAXA_JUROS",
        valor="2.5",
        descricao="Taxa de juros padrão",
        tipo="decimal"
    )
    
    assert configuracao.id_configuracao is not None
    assert configuracao.chave == "TAXA_JUROS"
    assert configuracao.valor == "2.5"
    assert configuracao.descricao == "Taxa de juros padrão"
    assert configuracao.tipo == "decimal"


@pytest.mark.asyncio
async def test_atualizar_configuracao(
    session: AsyncSession,
    configuracao: Configuracao
):
    """Testa a atualização de uma configuração."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    configuracao_atualizada = await service.update(
        id_configuracao=configuracao.id_configuracao,
        valor="3.0",
        descricao="Nova descrição"
    )
    
    assert configuracao_atualizada.id_configuracao == configuracao.id_configuracao
    assert configuracao_atualizada.chave == configuracao.chave
    assert configuracao_atualizada.valor == "3.0"
    assert configuracao_atualizada.descricao == "Nova descrição"
    assert configuracao_atualizada.tipo == configuracao.tipo


@pytest.mark.asyncio
async def test_buscar_configuracao(
    session: AsyncSession,
    configuracao: Configuracao
):
    """Testa a busca de uma configuração por ID."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    configuracao_encontrada = await service.get_by_id(configuracao.id_configuracao)
    
    assert configuracao_encontrada.id_configuracao == configuracao.id_configuracao
    assert configuracao_encontrada.chave == configuracao.chave
    assert configuracao_encontrada.valor == configuracao.valor
    assert configuracao_encontrada.descricao == configuracao.descricao
    assert configuracao_encontrada.tipo == configuracao.tipo


@pytest.mark.asyncio
async def test_buscar_configuracao_por_chave(
    session: AsyncSession,
    configuracao: Configuracao
):
    """Testa a busca de uma configuração por chave."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    configuracao_encontrada = await service.get_by_key(configuracao.chave)
    
    assert configuracao_encontrada.id_configuracao == configuracao.id_configuracao
    assert configuracao_encontrada.chave == configuracao.chave
    assert configuracao_encontrada.valor == configuracao.valor
    assert configuracao_encontrada.descricao == configuracao.descricao
    assert configuracao_encontrada.tipo == configuracao.tipo


@pytest.mark.asyncio
async def test_listar_configuracoes(
    session: AsyncSession,
    configuracoes_lista: list[Configuracao]
):
    """Testa a listagem de configurações."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    configuracoes = await service.list_all()
    
    assert len(configuracoes) >= len(configuracoes_lista)
    for configuracao in configuracoes_lista:
        assert any(c.id_configuracao == configuracao.id_configuracao for c in configuracoes)


@pytest.mark.asyncio
async def test_deletar_configuracao(
    session: AsyncSession,
    configuracao: Configuracao
):
    """Testa a deleção de uma configuração."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    await service.delete(configuracao.id_configuracao)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(configuracao.id_configuracao)
    
    assert exc_info.value.status_code == 404
    assert "Configuração não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_criar_configuracao_chave_duplicada(
    session: AsyncSession,
    configuracao: Configuracao
):
    """Testa o erro ao criar uma configuração com chave duplicada."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create(
            chave=configuracao.chave,
            valor="1.0",
            descricao="Teste",
            tipo="decimal"
        )
    
    assert exc_info.value.status_code == 400
    assert "Já existe uma configuração com esta chave" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_atualizar_configuracao_inexistente(session: AsyncSession):
    """Testa o erro ao atualizar uma configuração inexistente."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.update(
            id_configuracao=str(uuid4()),
            valor="1.0",
            descricao="Teste"
        )
    
    assert exc_info.value.status_code == 404
    assert "Configuração não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_buscar_configuracao_inexistente(session: AsyncSession):
    """Testa o erro ao buscar uma configuração inexistente."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(str(uuid4()))
    
    assert exc_info.value.status_code == 404
    assert "Configuração não encontrada" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_erro_buscar_configuracao_chave_inexistente(session: AsyncSession):
    """Testa o erro ao buscar uma configuração por chave inexistente."""
    service = ConfiguracaoService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_key("CHAVE_INEXISTENTE")
    
    assert exc_info.value.status_code == 404
    assert "Configuração não encontrada" in str(exc_info.value.detail) 