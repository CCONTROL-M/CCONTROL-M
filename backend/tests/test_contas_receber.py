"""Testes para o serviço de contas a receber."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from decimal import Decimal
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.conta_receber import ContaReceber
from app.schemas.conta_receber import ContaReceberCreate, ContaReceberUpdate
from app.services.conta_receber_service import ContaReceberService
from app.services.auditoria_service import AuditoriaService

from .fixtures.conta_receber import conta_receber, conta_receber_factory, contas_receber_lista
from .fixtures.cliente import cliente


@pytest.mark.asyncio
async def test_criar_conta_receber(
    session: AsyncSession,
    conta_receber_factory: Callable[..., AsyncGenerator[ContaReceber, None]],
    cliente: Cliente
):
    """Teste de criação de conta a receber."""
    # Arrange
    descricao = "Conta teste"
    valor = Decimal("1000.00")
    data_vencimento = date.today() + timedelta(days=30)
    observacao = "Observação teste"
    
    # Act
    conta = await conta_receber_factory(
        id_cliente=cliente.id_cliente,
        descricao=descricao,
        valor=valor,
        data_vencimento=data_vencimento,
        observacao=observacao
    )
    
    # Assert
    assert conta.id_conta_receber is not None
    assert conta.id_cliente == cliente.id_cliente
    assert conta.descricao == descricao
    assert conta.valor == valor
    assert conta.data_vencimento == data_vencimento
    assert conta.observacao == observacao
    assert conta.status == "pendente"
    assert conta.data_recebimento is None
    assert conta.valor_recebido is None


@pytest.mark.asyncio
async def test_atualizar_conta_receber(
    session: AsyncSession,
    conta_receber: ContaReceber
):
    """Teste de atualização de conta a receber."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    nova_descricao = "Conta atualizada"
    novo_valor = Decimal("1500.00")
    nova_data_vencimento = date.today() + timedelta(days=45)
    nova_observacao = "Observação atualizada"
    
    conta_update = ContaReceberUpdate(
        descricao=nova_descricao,
        valor=novo_valor,
        data_vencimento=nova_data_vencimento,
        observacao=nova_observacao
    )
    
    # Act
    conta_atualizada = await service.update(
        conta_receber.id_conta_receber,
        conta_update
    )
    
    # Assert
    assert conta_atualizada.id_conta_receber == conta_receber.id_conta_receber
    assert conta_atualizada.descricao == nova_descricao
    assert conta_atualizada.valor == novo_valor
    assert conta_atualizada.data_vencimento == nova_data_vencimento
    assert conta_atualizada.observacao == nova_observacao


@pytest.mark.asyncio
async def test_buscar_conta_receber(
    session: AsyncSession,
    conta_receber: ContaReceber
):
    """Teste de busca de conta a receber por ID."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    conta_encontrada = await service.get_by_id(conta_receber.id_conta_receber)
    
    # Assert
    assert conta_encontrada is not None
    assert conta_encontrada.id_conta_receber == conta_receber.id_conta_receber
    assert conta_encontrada.descricao == conta_receber.descricao
    assert conta_encontrada.valor == conta_receber.valor
    assert conta_encontrada.data_vencimento == conta_receber.data_vencimento


@pytest.mark.asyncio
async def test_listar_contas_receber(
    session: AsyncSession,
    contas_receber_lista: list[ContaReceber]
):
    """Teste de listagem de contas a receber."""
    # Arrange
    service = ContaReceberService(
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
async def test_buscar_contas_por_cliente(
    session: AsyncSession,
    contas_receber_lista: list[ContaReceber],
    cliente: Cliente
):
    """Teste de busca de contas por cliente."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    contas = await service.get_by_cliente(cliente.id_cliente)
    
    # Assert
    assert len(contas) > 0
    for conta in contas:
        assert conta.id_cliente == cliente.id_cliente


@pytest.mark.asyncio
async def test_buscar_contas_por_vencimento(
    session: AsyncSession,
    contas_receber_lista: list[ContaReceber]
):
    """Teste de busca de contas por período de vencimento."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    data_inicio = date.today()
    data_fim = date.today() + timedelta(days=30)
    
    # Act
    contas = await service.get_by_vencimento(data_inicio, data_fim)
    
    # Assert
    assert len(contas) > 0
    for conta in contas:
        assert conta.data_vencimento >= data_inicio
        assert conta.data_vencimento <= data_fim


@pytest.mark.asyncio
async def test_buscar_contas_por_status(
    session: AsyncSession,
    contas_receber_lista: list[ContaReceber]
):
    """Teste de busca de contas por status."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    status = "pendente"
    
    # Act
    contas = await service.get_by_status(status)
    
    # Assert
    assert len(contas) > 0
    for conta in contas:
        assert conta.status == status


@pytest.mark.asyncio
async def test_receber_conta(
    session: AsyncSession,
    conta_receber: ContaReceber
):
    """Teste de recebimento de conta."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    valor_recebido = conta_receber.valor
    data_recebimento = date.today()
    
    # Act
    conta_recebida = await service.receber(
        conta_receber.id_conta_receber,
        valor_recebido,
        data_recebimento
    )
    
    # Assert
    assert conta_recebida.id_conta_receber == conta_receber.id_conta_receber
    assert conta_recebida.status == "recebido"
    assert conta_recebida.valor_recebido == valor_recebido
    assert conta_recebida.data_recebimento == data_recebimento


@pytest.mark.asyncio
async def test_cancelar_conta(
    session: AsyncSession,
    conta_receber: ContaReceber
):
    """Teste de cancelamento de conta."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    conta_cancelada = await service.cancelar(conta_receber.id_conta_receber)
    
    # Assert
    assert conta_cancelada.id_conta_receber == conta_receber.id_conta_receber
    assert conta_cancelada.status == "cancelado"


@pytest.mark.asyncio
async def test_erro_ao_receber_conta_ja_recebida(
    session: AsyncSession,
    conta_receber_factory: Callable[..., AsyncGenerator[ContaReceber, None]],
    cliente: Cliente
):
    """Teste de erro ao receber conta já recebida."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    conta = await conta_receber_factory(
        id_cliente=cliente.id_cliente,
        status="recebido"
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.receber(
            conta.id_conta_receber,
            conta.valor,
            date.today()
        )
    assert excinfo.value.status_code == 400
    assert "já está recebida" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_receber_conta_cancelada(
    session: AsyncSession,
    conta_receber_factory: Callable[..., AsyncGenerator[ContaReceber, None]],
    cliente: Cliente
):
    """Teste de erro ao receber conta cancelada."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    conta = await conta_receber_factory(
        id_cliente=cliente.id_cliente,
        status="cancelado"
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.receber(
            conta.id_conta_receber,
            conta.valor,
            date.today()
        )
    assert excinfo.value.status_code == 400
    assert "não pode ser recebida" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_buscar_conta_inexistente(session: AsyncSession):
    """Teste de erro ao buscar conta inexistente."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_by_id(uuid4())
    assert excinfo.value.status_code == 404
    assert "não encontrada" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_atualizar_conta_inexistente(session: AsyncSession):
    """Teste de erro ao atualizar conta inexistente."""
    # Arrange
    service = ContaReceberService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    conta_update = ContaReceberUpdate(descricao="Teste")
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.update(uuid4(), conta_update)
    assert excinfo.value.status_code == 404
    assert "não encontrada" in str(excinfo.value.detail) 