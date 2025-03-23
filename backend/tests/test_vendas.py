"""Testes para o serviço de vendas."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from datetime import datetime, date

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.venda import Venda
from app.schemas.venda import VendaCreate, VendaUpdate
from app.services.venda_service import VendaService
from app.services.auditoria_service import AuditoriaService

from .fixtures.venda import venda, venda_factory, vendas_lista
from .fixtures.cliente import cliente
from .fixtures.usuario import usuario


@pytest.mark.asyncio
async def test_criar_venda(
    session: AsyncSession,
    venda_factory: Callable[..., AsyncGenerator[Venda, None]],
    cliente: Cliente,
    usuario: Usuario
):
    """Teste de criação de venda."""
    # Arrange
    valor_total = 100.50
    desconto = 10.00
    valor_final = 90.50
    forma_pagamento = "dinheiro"
    parcelas = 1
    observacao = "Venda teste"
    
    # Act
    venda = await venda_factory(
        id_cliente=cliente.id_cliente,
        id_usuario=usuario.id_usuario,
        valor_total=valor_total,
        desconto=desconto,
        valor_final=valor_final,
        forma_pagamento=forma_pagamento,
        parcelas=parcelas,
        observacao=observacao
    )
    
    # Assert
    assert venda.id_venda is not None
    assert venda.id_cliente == cliente.id_cliente
    assert venda.id_usuario == usuario.id_usuario
    assert venda.valor_total == valor_total
    assert venda.desconto == desconto
    assert venda.valor_final == valor_final
    assert venda.forma_pagamento == forma_pagamento
    assert venda.parcelas == parcelas
    assert venda.observacao == observacao
    assert venda.data_venda.date() == date.today()
    assert venda.status == "pendente"


@pytest.mark.asyncio
async def test_atualizar_venda(
    session: AsyncSession,
    venda: Venda
):
    """Teste de atualização de venda."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    novo_valor_total = 200.00
    novo_desconto = 20.00
    novo_valor_final = 180.00
    nova_forma_pagamento = "cartao"
    novas_parcelas = 2
    nova_observacao = "Venda atualizada"
    
    venda_update = VendaUpdate(
        valor_total=novo_valor_total,
        desconto=novo_desconto,
        valor_final=novo_valor_final,
        forma_pagamento=nova_forma_pagamento,
        parcelas=novas_parcelas,
        observacao=nova_observacao
    )
    
    # Act
    venda_atualizada = await service.update(
        venda.id_venda,
        venda_update
    )
    
    # Assert
    assert venda_atualizada.id_venda == venda.id_venda
    assert venda_atualizada.valor_total == novo_valor_total
    assert venda_atualizada.desconto == novo_desconto
    assert venda_atualizada.valor_final == novo_valor_final
    assert venda_atualizada.forma_pagamento == nova_forma_pagamento
    assert venda_atualizada.parcelas == novas_parcelas
    assert venda_atualizada.observacao == nova_observacao


@pytest.mark.asyncio
async def test_buscar_venda(
    session: AsyncSession,
    venda: Venda
):
    """Teste de busca de venda por ID."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    venda_encontrada = await service.get_by_id(venda.id_venda)
    
    # Assert
    assert venda_encontrada is not None
    assert venda_encontrada.id_venda == venda.id_venda
    assert venda_encontrada.id_cliente == venda.id_cliente
    assert venda_encontrada.id_usuario == venda.id_usuario
    assert venda_encontrada.valor_total == venda.valor_total
    assert venda_encontrada.valor_final == venda.valor_final


@pytest.mark.asyncio
async def test_listar_vendas(
    session: AsyncSession,
    vendas_lista: list[Venda]
):
    """Teste de listagem de vendas."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    resultado = await service.get_multi(
        skip=0,
        limit=10
    )
    
    # Assert
    assert resultado.total == 5
    assert len(resultado.items) == 5
    assert resultado.page == 1


@pytest.mark.asyncio
async def test_buscar_vendas_por_cliente(
    session: AsyncSession,
    vendas_lista: list[Venda],
    cliente: Cliente
):
    """Teste de busca de vendas por cliente."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    vendas = await service.get_by_cliente(cliente.id_cliente)
    
    # Assert
    assert len(vendas) > 0
    for venda in vendas:
        assert venda.id_cliente == cliente.id_cliente


@pytest.mark.asyncio
async def test_buscar_vendas_por_periodo(
    session: AsyncSession,
    vendas_lista: list[Venda]
):
    """Teste de busca de vendas por período."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    data_inicio = date.today()
    data_fim = date.today()
    
    # Act
    vendas = await service.get_by_periodo(data_inicio, data_fim)
    
    # Assert
    assert len(vendas) > 0
    for venda in vendas:
        assert venda.data_venda.date() >= data_inicio
        assert venda.data_venda.date() <= data_fim


@pytest.mark.asyncio
async def test_cancelar_venda(
    session: AsyncSession,
    venda: Venda
):
    """Teste de cancelamento de venda."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    venda_cancelada = await service.cancel(venda.id_venda)
    
    # Assert
    assert venda_cancelada.id_venda == venda.id_venda
    assert venda_cancelada.status == "cancelada"


@pytest.mark.asyncio
async def test_finalizar_venda(
    session: AsyncSession,
    venda: Venda
):
    """Teste de finalização de venda."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    venda_finalizada = await service.finish(venda.id_venda)
    
    # Assert
    assert venda_finalizada.id_venda == venda.id_venda
    assert venda_finalizada.status == "finalizada"


@pytest.mark.asyncio
async def test_erro_ao_buscar_venda_inexistente(session: AsyncSession):
    """Teste de erro ao buscar venda inexistente."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_by_id(uuid4())
    assert excinfo.value.status_code == 404
    assert "não encontrada" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_atualizar_venda_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar venda inexistente."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    venda_update = VendaUpdate(valor_total=100.00)
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.update(uuid4(), venda_update)
    assert excinfo.value.status_code == 404
    assert "não encontrada" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_cancelar_venda_finalizada(
    session: AsyncSession,
    venda_factory: Callable[..., AsyncGenerator[Venda, None]],
    cliente: Cliente,
    usuario: Usuario
):
    """Teste de erro ao cancelar venda finalizada."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    venda = await venda_factory(
        id_cliente=cliente.id_cliente,
        id_usuario=usuario.id_usuario,
        valor_total=100.00,
        valor_final=100.00,
        status="finalizada"
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.cancel(venda.id_venda)
    assert excinfo.value.status_code == 400
    assert "não pode ser cancelada" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_finalizar_venda_cancelada(
    session: AsyncSession,
    venda_factory: Callable[..., AsyncGenerator[Venda, None]],
    cliente: Cliente,
    usuario: Usuario
):
    """Teste de erro ao finalizar venda cancelada."""
    # Arrange
    service = VendaService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    venda = await venda_factory(
        id_cliente=cliente.id_cliente,
        id_usuario=usuario.id_usuario,
        valor_total=100.00,
        valor_final=100.00,
        status="cancelada"
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.finish(venda.id_venda)
    assert excinfo.value.status_code == 400
    assert "não pode ser finalizada" in str(excinfo.value.detail) 