"""Testes para o serviço de contas a pagar."""
import pytest
from uuid import uuid4
from typing import Callable, AsyncGenerator
from decimal import Decimal
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.conta_pagar import ContaPagar
from app.schemas.conta_pagar import ContaPagarCreate, ContaPagarUpdate
from app.services.conta_pagar_service import ContaPagarService
from app.services.auditoria_service import AuditoriaService

from .fixtures.conta_pagar import conta_pagar, conta_pagar_factory, contas_pagar_lista


@pytest.mark.asyncio
async def test_criar_conta_pagar(
    session: AsyncSession,
    conta_pagar_factory: Callable[..., AsyncGenerator[ContaPagar, None]]
):
    """Teste de criação de conta a pagar."""
    # Arrange
    descricao = "Conta teste"
    valor = Decimal("1000.00")
    data_vencimento = date.today() + timedelta(days=30)
    observacao = "Observação teste"
    
    # Act
    conta = await conta_pagar_factory(
        descricao=descricao,
        valor=valor,
        data_vencimento=data_vencimento,
        observacao=observacao
    )
    
    # Assert
    assert conta.id_conta_pagar is not None
    assert conta.descricao == descricao
    assert conta.valor == valor
    assert conta.data_vencimento == data_vencimento
    assert conta.observacao == observacao
    assert conta.status == "pendente"
    assert conta.data_pagamento is None
    assert conta.valor_pago is None


@pytest.mark.asyncio
async def test_atualizar_conta_pagar(
    session: AsyncSession,
    conta_pagar: ContaPagar
):
    """Teste de atualização de conta a pagar."""
    # Arrange
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    nova_descricao = "Conta atualizada"
    novo_valor = Decimal("1500.00")
    nova_data_vencimento = date.today() + timedelta(days=45)
    nova_observacao = "Observação atualizada"
    
    conta_update = ContaPagarUpdate(
        descricao=nova_descricao,
        valor=novo_valor,
        data_vencimento=nova_data_vencimento,
        observacao=nova_observacao
    )
    
    # Act
    conta_atualizada = await service.update(
        conta_pagar.id_conta_pagar,
        conta_update
    )
    
    # Assert
    assert conta_atualizada.id_conta_pagar == conta_pagar.id_conta_pagar
    assert conta_atualizada.descricao == nova_descricao
    assert conta_atualizada.valor == novo_valor
    assert conta_atualizada.data_vencimento == nova_data_vencimento
    assert conta_atualizada.observacao == nova_observacao


@pytest.mark.asyncio
async def test_buscar_conta_pagar(
    session: AsyncSession,
    conta_pagar: ContaPagar
):
    """Teste de busca de conta a pagar por ID."""
    # Arrange
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    conta_encontrada = await service.get_by_id(conta_pagar.id_conta_pagar)
    
    # Assert
    assert conta_encontrada is not None
    assert conta_encontrada.id_conta_pagar == conta_pagar.id_conta_pagar
    assert conta_encontrada.descricao == conta_pagar.descricao
    assert conta_encontrada.valor == conta_pagar.valor
    assert conta_encontrada.data_vencimento == conta_pagar.data_vencimento


@pytest.mark.asyncio
async def test_listar_contas_pagar(
    session: AsyncSession,
    contas_pagar_lista: list[ContaPagar]
):
    """Teste de listagem de contas a pagar."""
    # Arrange
    service = ContaPagarService(
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
async def test_buscar_contas_por_vencimento(
    session: AsyncSession,
    contas_pagar_lista: list[ContaPagar]
):
    """Teste de busca de contas por período de vencimento."""
    # Arrange
    service = ContaPagarService(
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
    contas_pagar_lista: list[ContaPagar]
):
    """Teste de busca de contas por status."""
    # Arrange
    service = ContaPagarService(
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
async def test_pagar_conta(
    session: AsyncSession,
    conta_pagar: ContaPagar
):
    """Teste de pagamento de conta."""
    # Arrange
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    valor_pago = conta_pagar.valor
    data_pagamento = date.today()
    
    # Act
    conta_paga = await service.pagar(
        conta_pagar.id_conta_pagar,
        valor_pago,
        data_pagamento
    )
    
    # Assert
    assert conta_paga.id_conta_pagar == conta_pagar.id_conta_pagar
    assert conta_paga.status == "pago"
    assert conta_paga.valor_pago == valor_pago
    assert conta_paga.data_pagamento == data_pagamento


@pytest.mark.asyncio
async def test_cancelar_conta(
    session: AsyncSession,
    conta_pagar: ContaPagar
):
    """Teste de cancelamento de conta."""
    # Arrange
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    
    # Act
    conta_cancelada = await service.cancelar(conta_pagar.id_conta_pagar)
    
    # Assert
    assert conta_cancelada.id_conta_pagar == conta_pagar.id_conta_pagar
    assert conta_cancelada.status == "cancelado"


@pytest.mark.asyncio
async def test_erro_ao_pagar_conta_ja_paga(
    session: AsyncSession,
    conta_pagar_factory: Callable[..., AsyncGenerator[ContaPagar, None]]
):
    """Teste de erro ao pagar conta já paga."""
    # Arrange
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    conta = await conta_pagar_factory(status="pago")
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.pagar(
            conta.id_conta_pagar,
            conta.valor,
            date.today()
        )
    assert excinfo.value.status_code == 400
    assert "já está paga" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_pagar_conta_cancelada(
    session: AsyncSession,
    conta_pagar_factory: Callable[..., AsyncGenerator[ContaPagar, None]]
):
    """Teste de erro ao pagar conta cancelada."""
    # Arrange
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    conta = await conta_pagar_factory(status="cancelado")
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.pagar(
            conta.id_conta_pagar,
            conta.valor,
            date.today()
        )
    assert excinfo.value.status_code == 400
    assert "não pode ser paga" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_erro_ao_buscar_conta_inexistente(session: AsyncSession):
    """Teste de erro ao buscar conta inexistente."""
    # Arrange
    service = ContaPagarService(
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
    service = ContaPagarService(
        session=session,
        auditoria_service=AuditoriaService(session=session)
    )
    conta_update = ContaPagarUpdate(descricao="Teste")
    
    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.update(uuid4(), conta_update)
    assert excinfo.value.status_code == 404
    assert "não encontrada" in str(excinfo.value.detail) 