"""Testes para o serviço de auditoria."""
import pytest
from uuid import uuid4
from datetime import datetime
from typing import Callable, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.auditoria import Auditoria
from app.schemas.auditoria import AuditoriaCreate, TipoOperacao
from app.services.auditoria_service import AuditoriaService

from .fixtures.auditoria import auditoria, auditoria_factory, auditoria_lista
from .fixtures.usuario import usuario


@pytest.mark.asyncio
async def test_criar_registro_auditoria(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a criação de um registro de auditoria."""
    service = AuditoriaService(session=session)
    
    registro = await service.create(
        id_usuario=str(usuario.id_usuario),
        entidade="Cliente",
        operacao="CREATE",
        valor_anterior=None,
        valor_atual={"nome": "Cliente Teste", "email": "teste@teste.com"}
    )
    
    assert registro.id_auditoria is not None
    assert registro.id_usuario == str(usuario.id_usuario)
    assert registro.entidade == "Cliente"
    assert registro.operacao == "CREATE"
    assert registro.valor_anterior is None
    assert registro.valor_atual == {"nome": "Cliente Teste", "email": "teste@teste.com"}
    assert isinstance(registro.data_hora, datetime)


@pytest.mark.asyncio
async def test_buscar_registro_auditoria(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a busca de um registro de auditoria por ID."""
    service = AuditoriaService(session=session)
    
    # Criar registro
    registro = await service.create(
        id_usuario=str(usuario.id_usuario),
        entidade="Cliente",
        operacao="CREATE",
        valor_anterior=None,
        valor_atual={"nome": "Cliente Teste"}
    )
    
    # Buscar registro
    registro_encontrado = await service.get_by_id(registro.id_auditoria)
    
    assert registro_encontrado.id_auditoria == registro.id_auditoria
    assert registro_encontrado.id_usuario == registro.id_usuario
    assert registro_encontrado.entidade == registro.entidade
    assert registro_encontrado.operacao == registro.operacao
    assert registro_encontrado.valor_anterior == registro.valor_anterior
    assert registro_encontrado.valor_atual == registro.valor_atual
    assert registro_encontrado.data_hora == registro.data_hora


@pytest.mark.asyncio
async def test_listar_registros_auditoria(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a listagem de registros de auditoria."""
    service = AuditoriaService(session=session)
    
    # Criar vários registros
    registros = []
    for i in range(5):
        registro = await service.create(
            id_usuario=str(usuario.id_usuario),
            entidade="Cliente",
            operacao="UPDATE",
            valor_anterior={"nome": f"Cliente {i}"},
            valor_atual={"nome": f"Cliente {i} Atualizado"}
        )
        registros.append(registro)
    
    # Listar registros
    registros_encontrados = await service.list_all()
    
    assert len(registros_encontrados) >= 5
    for registro in registros:
        assert any(r.id_auditoria == registro.id_auditoria for r in registros_encontrados)


@pytest.mark.asyncio
async def test_buscar_registros_por_entidade(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a busca de registros de auditoria por entidade."""
    service = AuditoriaService(session=session)
    
    # Criar registros para diferentes entidades
    entidades = ["Cliente", "Produto", "Venda"]
    for entidade in entidades:
        await service.create(
            id_usuario=str(usuario.id_usuario),
            entidade=entidade,
            operacao="CREATE",
            valor_anterior=None,
            valor_atual={"nome": f"Teste {entidade}"}
        )
    
    # Buscar registros da entidade Cliente
    registros = await service.get_by_entity("Cliente")
    
    assert len(registros) >= 1
    for registro in registros:
        assert registro.entidade == "Cliente"


@pytest.mark.asyncio
async def test_buscar_registros_por_usuario(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a busca de registros de auditoria por usuário."""
    service = AuditoriaService(session=session)
    
    # Criar registros
    await service.create(
        id_usuario=str(usuario.id_usuario),
        entidade="Cliente",
        operacao="CREATE",
        valor_anterior=None,
        valor_atual={"nome": "Cliente Teste"}
    )
    
    # Buscar registros do usuário
    registros = await service.get_by_user(str(usuario.id_usuario))
    
    assert len(registros) >= 1
    for registro in registros:
        assert registro.id_usuario == str(usuario.id_usuario)


@pytest.mark.asyncio
async def test_buscar_registros_por_periodo(
    session: AsyncSession,
    usuario: Usuario
):
    """Testa a busca de registros de auditoria por período."""
    service = AuditoriaService(session=session)
    
    # Criar registros
    data_inicial = datetime.now()
    for _ in range(3):
        await service.create(
            id_usuario=str(usuario.id_usuario),
            entidade="Cliente",
            operacao="CREATE",
            valor_anterior=None,
            valor_atual={"nome": "Cliente Teste"}
        )
    data_final = datetime.now()
    
    # Buscar registros do período
    registros = await service.get_by_date_range(data_inicial, data_final)
    
    assert len(registros) >= 3
    for registro in registros:
        assert data_inicial <= registro.data_hora <= data_final


@pytest.mark.asyncio
async def test_erro_ao_buscar_registro_inexistente(session: AsyncSession):
    """Testa o erro ao buscar um registro de auditoria inexistente."""
    service = AuditoriaService(session=session)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(str(uuid4()))
    
    assert exc_info.value.status_code == 404
    assert "Registro de auditoria não encontrado" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_buscar_registros_auditoria(
    session: AsyncSession,
    auditoria_lista: list[Auditoria]
):
    """Teste de busca de registros de auditoria."""
    # Arrange
    service = AuditoriaService(session=session)
    empresa_id = auditoria_lista[0].empresa_id
    
    # Act
    resultado = await service.get_multi(
        empresa_id=empresa_id,
        skip=0,
        limit=10
    )
    
    # Assert
    assert resultado.total == 3
    assert len(resultado.items) == 3
    assert resultado.page == 1
    assert all(reg.empresa_id == empresa_id for reg in resultado.items)


@pytest.mark.asyncio
async def test_filtrar_registros_por_tabela(
    session: AsyncSession,
    auditoria_lista: list[Auditoria]
):
    """Teste de filtro de registros por tabela."""
    # Arrange
    service = AuditoriaService(session=session)
    empresa_id = auditoria_lista[0].empresa_id
    
    # Act
    resultado = await service.get_multi(
        empresa_id=empresa_id,
        tabela="contas_pagar"
    )
    
    # Assert
    assert resultado.total == 1
    assert len(resultado.items) == 1
    assert all(reg.tabela == "contas_pagar" for reg in resultado.items)


@pytest.mark.asyncio
async def test_filtrar_registros_por_operacao(
    session: AsyncSession,
    auditoria_lista: list[Auditoria]
):
    """Teste de filtro de registros por tipo de operação."""
    # Arrange
    service = AuditoriaService(session=session)
    empresa_id = auditoria_lista[0].empresa_id
    
    # Act
    resultado = await service.get_multi(
        empresa_id=empresa_id,
        operacao=TipoOperacao.ATUALIZACAO
    )
    
    # Assert
    assert resultado.total == 1
    assert len(resultado.items) == 1
    assert all(reg.operacao == TipoOperacao.ATUALIZACAO for reg in resultado.items)


@pytest.mark.asyncio
async def test_buscar_registro_por_id(
    session: AsyncSession,
    auditoria: Auditoria
):
    """Teste de busca de registro por ID."""
    # Arrange
    service = AuditoriaService(session=session)
    
    # Act
    registro = await service.get_by_id(auditoria.id_auditoria, auditoria.empresa_id)
    
    # Assert
    assert registro is not None
    assert registro.id_auditoria == auditoria.id_auditoria
    assert registro.tabela == auditoria.tabela
    assert registro.operacao == auditoria.operacao
    assert registro.empresa_id == auditoria.empresa_id


@pytest.mark.asyncio
async def test_erro_ao_buscar_registro_inexistente(session: AsyncSession):
    """Teste de erro ao buscar registro inexistente."""
    # Arrange
    service = AuditoriaService(session=session)
    
    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        await service.get_by_id(uuid4(), uuid4())
    assert "não encontrado" in str(excinfo.value) 